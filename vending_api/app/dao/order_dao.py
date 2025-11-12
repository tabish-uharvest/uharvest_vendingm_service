from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func, text, or_
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from app.models.order import Order, OrderItem, OrderAddon
from app.models.machine import VendingMachine, MachineIngredient, MachineAddon
from app.models.product import Ingredient, Addon
from app.models.user import User
from app.dao.base_dao import BaseDAO
from app.dao.machine_dao import MachineDAO
from app.utils.exceptions import (
    NotFoundError, 
    BusinessRuleError, 
    ConflictError, 
    DatabaseError,
    InsufficientStockError,
    OrderProcessingError
)

logger = logging.getLogger(__name__)


class OrderDAO(BaseDAO[Order]):
    def __init__(self):
        super().__init__(Order)
        self.machine_dao = MachineDAO()
    
    async def create_order_with_items(
        self, 
        session: AsyncSession,
        machine_id: UUID,
        user_id: Optional[UUID],
        session_id: Optional[str],
        total_price: Decimal,
        total_calories: int,
        status: str,
        ingredients: List[Dict[str, Any]],
        addons: List[Dict[str, Any]],
        liquids: Optional[List[Dict[str, Any]]] = None
    ) -> Order:
        """Create order with items - all data comes from UI"""
        try:
            # Validate machine availability
            await self.machine_dao.validate_machine_for_order(session, machine_id)
            
            # Validate ingredients and addons exist (no calculation needed)
            await self._validate_ingredients_exist(session, ingredients)
            await self._validate_addons_exist(session, addons)
            
            # Validate stock availability
            await self._validate_stock_availability(session, machine_id, ingredients, addons)
            
            # Create the order with UI-provided data
            order_data = {
                "machine_id": machine_id,
                "user_id": user_id,
                "session_id": session_id,
                "status": status,
                "total_price": total_price,
                "total_calories": total_calories
            }
            
            order = await self.create(session, **order_data)
            
            # Create order items
            for ingredient_data in ingredients:
                await self._create_order_item(session, order.id, ingredient_data)
            
            # Create order addons
            for addon_data in addons:
                await self._create_order_addon(session, order.id, addon_data)
            
            # Deduct stock
            await self.machine_dao.deduct_stock(session, machine_id, ingredients, addons, session_id)
            
            # Load the complete order with relationships
            return await self.get_order_with_details(session, order.id)
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise OrderProcessingError(f"Failed to create order: {str(e)}")
    
    async def get_order_with_details(self, session: AsyncSession, order_id: UUID) -> Optional[Order]:
        """Get order with all related data"""
        try:
            result = await session.execute(
                select(Order)
                .options(
                    selectinload(Order.order_items).selectinload(OrderItem.ingredient),
                    selectinload(Order.order_addons).selectinload(OrderAddon.addon),
                    selectinload(Order.machine),
                    selectinload(Order.user)
                )
                .where(Order.id == order_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting order details {order_id}: {e}")
            raise DatabaseError("Failed to get order details")
    
    async def update_order_status(
        self, 
        session: AsyncSession, 
        order_id: UUID, 
        status: str,
        payment_status: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Order]:
        """Update order status with validation"""
        try:
            # Get the order first to validate it exists
            order = await session.get(Order, order_id)
            if not order:
                raise NotFoundError(f"Order {order_id} not found")
            
            # Validate status transition
            self._validate_status_transition(order.status, status)
            
            # Update only the status field directly
            order.status = status
            
            # Flush to ensure the update is reflected
            await session.flush()
            
            # Handle status-specific logic for stock restoration
            if status == "cancelled":
                await self._handle_order_cancellation(session, order_id)
            elif status == "failed":
                await self._handle_order_failure(session, order_id)
            
            # Refresh the order to get updated data
            await session.refresh(order)
            
            return order
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            raise OrderProcessingError(f"Failed to update order status: {str(e)}")
    
    async def get_orders_by_machine(
        self, 
        session: AsyncSession, 
        machine_id: UUID,
        status_filter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get orders for a specific machine with filters"""
        try:
            query = select(Order).options(
                selectinload(Order.order_items).selectinload(OrderItem.ingredient),
                selectinload(Order.order_addons).selectinload(OrderAddon.addon),
                selectinload(Order.machine),
                selectinload(Order.user)
            ).where(Order.machine_id == machine_id)
            
            if status_filter:
                query = query.where(Order.status == status_filter)
            
            if date_from:
                query = query.where(Order.created_at >= date_from)
            
            if date_to:
                query = query.where(Order.created_at <= date_to)
            
            query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting orders by machine: {e}")
            raise DatabaseError("Failed to get orders")
    
    async def get_order_statistics(
        self, 
        session: AsyncSession,
        machine_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get order statistics"""
        try:
            # Use more database-agnostic SQL with CASE statements instead of FILTER
            # Cast machine_id parameter to UUID to avoid PostgreSQL ambiguity
            stats_query = text("""
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_orders,
                    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_orders,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_orders,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
                    SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing_orders,
                    COALESCE(SUM(CASE WHEN status = 'completed' THEN total_price ELSE 0 END), 0) as total_revenue,
                    COALESCE(AVG(CASE WHEN status = 'completed' THEN total_price ELSE NULL END), 0) as avg_order_value,
                    COALESCE(AVG(CASE WHEN status = 'completed' THEN total_calories ELSE NULL END), 0) as avg_calories
                FROM orders o
                WHERE (:machine_id::uuid IS NULL OR o.machine_id = :machine_id::uuid)
                  AND (:date_from::timestamp IS NULL OR o.created_at >= :date_from::timestamp)
                  AND (:date_to::timestamp IS NULL OR o.created_at <= :date_to::timestamp)
            """)
            
            result = await session.execute(
                stats_query, 
                {
                    "machine_id": machine_id,
                    "date_from": date_from,
                    "date_to": date_to
                }
            )
            row = result.first()
            
            if not row:
                return {
                    "total_orders": 0,
                    "completed_orders": 0,
                    "cancelled_orders": 0,
                    "failed_orders": 0,
                    "pending_orders": 0,
                    "processing_orders": 0,
                    "total_revenue": Decimal("0"),
                    "avg_order_value": Decimal("0"),
                    "avg_calories": Decimal("0")
                }
            
            # Convert to proper types to ensure JSON serialization
            raw_data = dict(row._mapping)
            return {
                "total_orders": int(raw_data.get("total_orders", 0)),
                "completed_orders": int(raw_data.get("completed_orders", 0)),
                "cancelled_orders": int(raw_data.get("cancelled_orders", 0)),
                "failed_orders": int(raw_data.get("failed_orders", 0)),
                "pending_orders": int(raw_data.get("pending_orders", 0)),
                "processing_orders": int(raw_data.get("processing_orders", 0)),
                "total_revenue": Decimal(str(raw_data.get("total_revenue", 0))),
                "avg_order_value": Decimal(str(raw_data.get("avg_order_value", 0))),
                "avg_calories": Decimal(str(raw_data.get("avg_calories", 0)))
            }
        except Exception as e:
            logger.error(f"Error getting order statistics: {e}")
            # Log the full traceback for debugging
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise DatabaseError("Failed to get order statistics")
    
    async def get_popular_items(
        self, 
        session: AsyncSession,
        machine_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get most popular ingredients and addons"""
        try:
            # Popular ingredients
            ingredients_query = text("""
                SELECT 
                    i.id,
                    i.name,
                    i.emoji,
                    COUNT(oi.id) as order_count,
                    SUM(oi.grams_used) as total_grams_used,
                    0 as total_revenue
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                JOIN ingredients i ON oi.ingredient_id = i.id
                WHERE o.status = 'completed'
                  AND (:machine_id::uuid IS NULL OR o.machine_id = :machine_id::uuid)
                  AND (:date_from::timestamp IS NULL OR o.created_at >= :date_from::timestamp)
                  AND (:date_to::timestamp IS NULL OR o.created_at <= :date_to::timestamp)
                GROUP BY i.id, i.name, i.emoji
                ORDER BY order_count DESC
                LIMIT :limit
            """)
            
            ingredients_result = await session.execute(
                ingredients_query,
                {
                    "machine_id": machine_id,
                    "date_from": date_from,
                    "date_to": date_to,
                    "limit": limit
                }
            )
            ingredients = []
            for row in ingredients_result:
                raw_data = dict(row._mapping)
                ingredients.append({
                    "id": raw_data["id"],  # Keep as UUID object for schema
                    "name": raw_data["name"],
                    "emoji": raw_data.get("emoji"),
                    "icon": None,  # Ingredients don't have icons
                    "order_count": int(raw_data["order_count"]),
                    "total_quantity": int(raw_data["total_grams_used"]),  # Map grams to quantity
                    "total_revenue": Decimal(str(raw_data["total_revenue"]))
                })
            
            # Popular addons
            addons_query = text("""
                SELECT 
                    a.id,
                    a.name,
                    a.icon,
                    COUNT(oa.id) as order_count,
                    SUM(oa.qty) as total_quantity,
                    0 as total_revenue
                FROM order_addons oa
                JOIN orders o ON oa.order_id = o.id
                JOIN addons a ON oa.addon_id = a.id
                WHERE o.status = 'completed'
                  AND (:machine_id::uuid IS NULL OR o.machine_id = :machine_id::uuid)
                  AND (:date_from::timestamp IS NULL OR o.created_at >= :date_from::timestamp)
                  AND (:date_to::timestamp IS NULL OR o.created_at <= :date_to::timestamp)
                GROUP BY a.id, a.name, a.icon
                ORDER BY order_count DESC
                LIMIT :limit
            """)
            
            addons_result = await session.execute(
                addons_query,
                {
                    "machine_id": machine_id,
                    "date_from": date_from,
                    "date_to": date_to,
                    "limit": limit
                }
            )
            addons = []
            for row in addons_result:
                raw_data = dict(row._mapping)
                addons.append({
                    "id": raw_data["id"],  # Keep as UUID object for schema
                    "name": raw_data["name"],
                    "emoji": None,  # Addons don't have emojis
                    "icon": raw_data.get("icon"),
                    "order_count": int(raw_data["order_count"]),
                    "total_quantity": int(raw_data["total_quantity"]),
                    "total_revenue": Decimal(str(raw_data["total_revenue"]))
                })
            
            return {
                "ingredients": ingredients,
                "addons": addons
            }
        except Exception as e:
            logger.error(f"Error getting popular items: {e}")
            raise DatabaseError("Failed to get popular items")

    async def _validate_ingredients_exist(
        self, 
        session: AsyncSession,
        ingredients: List[Dict[str, Any]]
    ) -> bool:
        """Validate that all ingredients exist"""
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['ingredient_id']
            ingredient = await session.get(Ingredient, ingredient_id)
            if not ingredient:
                raise NotFoundError(f"Ingredient {ingredient_id} not found")
        return True
    
    async def _validate_addons_exist(
        self, 
        session: AsyncSession,
        addons: List[Dict[str, Any]]
    ) -> bool:
        """Validate that all addons exist"""
        for addon_data in addons:
            addon_id = addon_data['addon_id']
            addon = await session.get(Addon, addon_id)
            if not addon:
                raise NotFoundError(f"Addon {addon_id} not found")
        return True
    
    async def _validate_stock_availability(
        self, 
        session: AsyncSession,
        machine_id: UUID,
        ingredients: List[Dict[str, Any]],
        addons: List[Dict[str, Any]]
    ) -> bool:
        """Validate that sufficient stock is available"""
        # This will be handled by the machine_dao.deduct_stock method
        # which validates before deducting
        return True
    
    async def _create_order_item(
        self, 
        session: AsyncSession,
        order_id: UUID,
        ingredient_data: Dict[str, Any]
    ) -> OrderItem:
        """Create an order item"""
        order_item = OrderItem(
            order_id=order_id,
            ingredient_id=ingredient_data['ingredient_id'],
            qty_ml=ingredient_data.get('qty_ml', 0),  # Default to 0 if not provided
            grams_used=ingredient_data['grams_used'],
            calories=ingredient_data['calories']
        )
        session.add(order_item)
        await session.flush()
        return order_item
    
    async def _create_order_addon(
        self, 
        session: AsyncSession,
        order_id: UUID,
        addon_data: Dict[str, Any]
    ) -> OrderAddon:
        """Create an order addon"""
        order_addon = OrderAddon(
            order_id=order_id,
            addon_id=addon_data['addon_id'],
            qty=addon_data['qty'],
            calories=addon_data['calories']
        )
        session.add(order_addon)
        await session.flush()
        return order_addon
    
    def _validate_status_transition(self, current_status: str, new_status: str) -> bool:
        """Validate that status transition is allowed"""
        allowed_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'failed', 'cancelled'],
            'completed': [],  # Terminal state
            'failed': [],     # Terminal state
            'cancelled': []   # Terminal state
        }
        
        if new_status not in allowed_transitions.get(current_status, []):
            raise BusinessRuleError(
                f"Invalid status transition from {current_status} to {new_status}",
                {"current_status": current_status, "new_status": new_status}
            )
        
        return True
    
    async def _handle_order_cancellation(self, session: AsyncSession, order_id: UUID) -> None:
        """Handle order cancellation - restore stock"""
        try:
            order = await self.get_order_with_details(session, order_id)
            if not order:
                return
            
            # Restore ingredient stock
            for order_item in order.order_items:
                if order_item.ingredient_id:
                    await session.execute(
                        update(MachineIngredient)
                        .where(
                            and_(
                                MachineIngredient.machine_id == order.machine_id,
                                MachineIngredient.ingredient_id == order_item.ingredient_id
                            )
                        )
                        .values(qty_available_g=MachineIngredient.qty_available_g + order_item.grams_used)
                    )
            
            # Restore addon stock
            for order_addon in order.order_addons:
                if order_addon.addon_id:
                    await session.execute(
                        update(MachineAddon)
                        .where(
                            and_(
                                MachineAddon.machine_id == order.machine_id,
                                MachineAddon.addon_id == order_addon.addon_id
                            )
                        )
                        .values(qty_available=MachineAddon.qty_available + order_addon.qty)
                    )
            
        except Exception as e:
            logger.error(f"Error handling order cancellation: {e}")
            raise
    
    async def _handle_order_failure(self, session: AsyncSession, order_id: UUID) -> None:
        """Handle order failure - restore stock (same as cancellation)"""
        await self._handle_order_cancellation(session, order_id)
