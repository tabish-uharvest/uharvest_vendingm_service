from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func, text, case
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from decimal import Decimal
import logging

from app.models.machine import VendingMachine, MachineIngredient, MachineAddon
from app.models.product import Ingredient, Addon
from app.models.order import Order
from app.dao.base_dao import BaseDAO
from app.utils.exceptions import NotFoundError, BusinessRuleError, ConflictError, DatabaseError

logger = logging.getLogger(__name__)


class MachineDAO(BaseDAO[VendingMachine]):
    def __init__(self):
        super().__init__(VendingMachine)
    
    async def get_with_inventory(self, session: AsyncSession, machine_id: UUID) -> Optional[VendingMachine]:
        """Get machine with full inventory loaded"""
        try:
            result = await session.execute(
                select(VendingMachine)
                .options(
                    selectinload(VendingMachine.machine_ingredients).selectinload(MachineIngredient.ingredient),
                    selectinload(VendingMachine.machine_addons).selectinload(MachineAddon.addon)
                )
                .where(VendingMachine.id == machine_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting machine with inventory {machine_id}: {e}")
            raise DatabaseError("Failed to get machine inventory")
    
    async def get_available_inventory(
        self, 
        session: AsyncSession, 
        machine_id: UUID
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get available ingredients and addons for a machine"""
        try:
            # Get available ingredients
            ingredients_query = text("""
                SELECT 
                    i.id,
                    i.name,
                    i.emoji,
                    i.min_qty_g,
                    i.max_percent_limit,
                    i.calories_per_g,
                    i.price_per_gram,
                    mi.qty_available_g,
                    mi.low_stock_threshold_g,
                    CASE WHEN mi.qty_available_g >= i.min_qty_g THEN true ELSE false END as is_available
                FROM machine_ingredients mi
                JOIN ingredients i ON mi.ingredient_id = i.id
                WHERE mi.machine_id = :machine_id
                  AND mi.qty_available_g > 0
                ORDER BY i.name
            """)
            
            ingredients_result = await session.execute(
                ingredients_query, 
                {"machine_id": machine_id}
            )
            ingredients = [dict(row._mapping) for row in ingredients_result]
            
            # Get available addons
            addons_query = text("""
                SELECT 
                    a.id,
                    a.name,
                    a.icon,
                    a.price,
                    a.calories,
                    ma.qty_available,
                    ma.low_stock_threshold,
                    CASE WHEN ma.qty_available > 0 THEN true ELSE false END as is_available
                FROM machine_addons ma
                JOIN addons a ON ma.addon_id = a.id
                WHERE ma.machine_id = :machine_id
                  AND ma.qty_available > 0
                ORDER BY a.name
            """)
            
            addons_result = await session.execute(
                addons_query, 
                {"machine_id": machine_id}
            )
            addons = [dict(row._mapping) for row in addons_result]
            
            return {
                "ingredients": ingredients,
                "addons": addons
            }
        except Exception as e:
            logger.error(f"Error getting available inventory for machine {machine_id}: {e}")
            raise DatabaseError("Failed to get machine inventory")
    
    async def check_machine_availability(self, session: AsyncSession, machine_id: UUID) -> bool:
        """Check if machine is available for orders"""
        try:
            machine = await self.get_by_id(session, machine_id)
            if not machine or machine.status != 'active':
                return False
            
            # Check if there's already a processing order
            result = await session.execute(
                select(func.count(Order.id))
                .where(
                    and_(
                        Order.machine_id == machine_id,
                        Order.status.in_(['pending', 'processing'])
                    )
                )
            )
            processing_orders = result.scalar()
            
            return processing_orders == 0
        except Exception as e:
            logger.error(f"Error checking machine availability {machine_id}: {e}")
            raise DatabaseError("Failed to check machine availability")
    
    async def get_machine_metrics(self, session: AsyncSession, machine_id: UUID) -> Dict[str, Any]:
        """Get machine performance metrics"""
        try:
            # Main metrics query
            metrics_query = text("""
                SELECT 
                    vm.id as machine_id,
                    vm.location as machine_location,
                    vm.status,
                    vm.cups_qty,
                    vm.bowls_qty,
                    COUNT(DISTINCT o.id) FILTER (WHERE o.created_at >= CURRENT_DATE) as orders_today,
                    COUNT(DISTINCT o.id) FILTER (WHERE o.created_at >= CURRENT_DATE - INTERVAL '7 days') as orders_this_week,
                    COUNT(DISTINCT o.id) FILTER (WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days') as orders_this_month,
                    COALESCE(SUM(o.total_price) FILTER (WHERE o.created_at >= CURRENT_DATE), 0) as revenue_today,
                    COALESCE(SUM(o.total_price) FILTER (WHERE o.created_at >= CURRENT_DATE - INTERVAL '7 days'), 0) as revenue_this_week,
                    COALESCE(SUM(o.total_price) FILTER (WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days'), 0) as revenue_this_month,
                    CASE 
                        WHEN COUNT(DISTINCT o.id) FILTER (WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days') > 0 
                        THEN COALESCE(AVG(o.total_price), 0) 
                        ELSE 0 
                    END as avg_order_value
                FROM vending_machines vm
                LEFT JOIN orders o ON vm.id = o.machine_id AND o.status = 'completed'
                WHERE vm.id = :machine_id
                GROUP BY vm.id, vm.location, vm.status, vm.cups_qty, vm.bowls_qty
            """)
            
            result = await session.execute(metrics_query, {"machine_id": machine_id})
            row = result.first()
            
            if not row:
                raise NotFoundError(f"Machine {machine_id} not found")
            
            metrics = dict(row._mapping)
            
            # Get most popular items
            popular_items_query = text("""
                SELECT 
                    i.name,
                    COUNT(*) as order_count
                FROM order_items oi
                JOIN ingredients i ON oi.ingredient_id = i.id
                JOIN orders o ON oi.order_id = o.id
                WHERE o.machine_id = :machine_id 
                  AND o.status = 'completed'
                  AND o.created_at >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY i.id, i.name
                ORDER BY order_count DESC
                LIMIT 5
            """)
            
            popular_result = await session.execute(popular_items_query, {"machine_id": machine_id})
            popular_items = [row[0] for row in popular_result.fetchall()]
            
            # Get inventory alerts count
            alerts_query = text("""
                SELECT COUNT(*) as alert_count
                FROM (
                    SELECT mi.machine_id
                    FROM machine_ingredients mi
                    WHERE mi.machine_id = :machine_id 
                      AND mi.qty_available_g <= mi.low_stock_threshold_g
                    UNION ALL
                    SELECT ma.machine_id
                    FROM machine_addons ma
                    WHERE ma.machine_id = :machine_id 
                      AND ma.qty_available <= ma.low_stock_threshold
                ) alerts
            """)
            
            alerts_result = await session.execute(alerts_query, {"machine_id": machine_id})
            alerts_count = alerts_result.scalar() or 0
            
            # Add missing fields
            metrics.update({
                'most_popular_items': popular_items,
                'inventory_alerts_count': alerts_count,
                'uptime_percentage': 95.0  # Default uptime percentage (could be calculated from logs)
            })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting machine metrics {machine_id}: {e}")
            raise DatabaseError("Failed to get machine metrics")
    
    async def get_low_stock_alerts(
        self, 
        session: AsyncSession, 
        machine_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get low stock alerts for machines"""
        try:
            low_stock_query = text("""
                SELECT 
                    'ingredient' as item_type,
                    vm.id as machine_id,
                    vm.location as machine_location,
                    i.id as item_id,
                    i.name as item_name,
                    mi.qty_available_g as current_qty,
                    mi.low_stock_threshold_g as threshold,
                    ROUND((mi.qty_available_g::decimal / NULLIF(mi.low_stock_threshold_g, 0)) * 100, 2) as percentage_remaining,
                    CASE 
                        WHEN mi.qty_available_g = 0 THEN 'critical'
                        WHEN mi.qty_available_g <= mi.low_stock_threshold_g * 0.5 THEN 'critical'
                        WHEN mi.qty_available_g <= mi.low_stock_threshold_g THEN 'warning'
                        ELSE 'info'
                    END as priority,
                    mi.updated_at as last_updated
                FROM machine_ingredients mi
                JOIN vending_machines vm ON mi.machine_id = vm.id
                JOIN ingredients i ON mi.ingredient_id = i.id
                WHERE mi.qty_available_g <= mi.low_stock_threshold_g
                  AND (:machine_id IS NULL OR vm.id = :machine_id)
                
                UNION ALL
                
                SELECT 
                    'addon' as item_type,
                    vm.id as machine_id,
                    vm.location as machine_location,
                    a.id as item_id,
                    a.name as item_name,
                    ma.qty_available as current_qty,
                    ma.low_stock_threshold as threshold,
                    ROUND((ma.qty_available::decimal / NULLIF(ma.low_stock_threshold, 0)) * 100, 2) as percentage_remaining,
                    CASE 
                        WHEN ma.qty_available = 0 THEN 'critical'
                        WHEN ma.qty_available <= ma.low_stock_threshold * 0.5 THEN 'critical'
                        WHEN ma.qty_available <= ma.low_stock_threshold THEN 'warning'
                        ELSE 'info'
                    END as priority,
                    ma.updated_at as last_updated
                FROM machine_addons ma
                JOIN vending_machines vm ON ma.machine_id = vm.id
                JOIN addons a ON ma.addon_id = a.id
                WHERE ma.qty_available <= ma.low_stock_threshold
                  AND (:machine_id IS NULL OR vm.id = :machine_id)
                
                ORDER BY 
                    CASE priority 
                        WHEN 'critical' THEN 1
                        WHEN 'warning' THEN 2
                        ELSE 3
                    END,
                    machine_location,
                    item_type,
                    item_name
            """)
            
            result = await session.execute(low_stock_query, {"machine_id": machine_id})
            return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error getting low stock alerts: {e}")
            raise DatabaseError("Failed to get low stock alerts")
    
    async def update_ingredient_stock(
        self, 
        session: AsyncSession, 
        machine_id: UUID, 
        ingredient_id: UUID, 
        qty_available_g: int,
        low_stock_threshold_g: Optional[int] = None
    ) -> bool:
        """Update ingredient stock for a machine"""
        try:
            update_data = {"qty_available_g": qty_available_g}
            if low_stock_threshold_g is not None:
                update_data["low_stock_threshold_g"] = low_stock_threshold_g
            
            result = await session.execute(
                update(MachineIngredient)
                .where(
                    and_(
                        MachineIngredient.machine_id == machine_id,
                        MachineIngredient.ingredient_id == ingredient_id
                    )
                )
                .values(**update_data)
            )
            
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating ingredient stock: {e}")
            raise DatabaseError("Failed to update ingredient stock")
    
    async def update_addon_stock(
        self, 
        session: AsyncSession, 
        machine_id: UUID, 
        addon_id: UUID, 
        qty_available: int,
        low_stock_threshold: Optional[int] = None
    ) -> bool:
        """Update addon stock for a machine"""
        try:
            update_data = {"qty_available": qty_available}
            if low_stock_threshold is not None:
                update_data["low_stock_threshold"] = low_stock_threshold
            
            result = await session.execute(
                update(MachineAddon)
                .where(
                    and_(
                        MachineAddon.machine_id == machine_id,
                        MachineAddon.addon_id == addon_id
                    )
                )
                .values(**update_data)
            )
            
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating addon stock: {e}")
            raise DatabaseError("Failed to update addon stock")
    
    async def deduct_stock(
        self, 
        session: AsyncSession, 
        machine_id: UUID, 
        ingredients: List[Dict[str, Any]], 
        addons: List[Dict[str, Any]]
    ) -> bool:
        """Deduct stock for ingredients and addons (used in order processing)"""
        try:
            # Deduct ingredient stock
            for ingredient in ingredients:
                ingredient_id = ingredient['ingredient_id']
                grams_used = ingredient['grams_used']
                
                # Check current stock
                result = await session.execute(
                    select(MachineIngredient.qty_available_g)
                    .where(
                        and_(
                            MachineIngredient.machine_id == machine_id,
                            MachineIngredient.ingredient_id == ingredient_id
                        )
                    )
                )
                current_qty = result.scalar()
                
                if current_qty is None or current_qty < grams_used:
                    raise BusinessRuleError(
                        f"Insufficient ingredient stock",
                        {"ingredient_id": ingredient_id, "required": grams_used, "available": current_qty}
                    )
                
                # Deduct stock
                await session.execute(
                    update(MachineIngredient)
                    .where(
                        and_(
                            MachineIngredient.machine_id == machine_id,
                            MachineIngredient.ingredient_id == ingredient_id
                        )
                    )
                    .values(qty_available_g=MachineIngredient.qty_available_g - grams_used)
                )
            
            # Deduct addon stock
            for addon in addons:
                addon_id = addon['addon_id']
                qty = addon['qty']
                
                # Check current stock
                result = await session.execute(
                    select(MachineAddon.qty_available)
                    .where(
                        and_(
                            MachineAddon.machine_id == machine_id,
                            MachineAddon.addon_id == addon_id
                        )
                    )
                )
                current_qty = result.scalar()
                
                if current_qty is None or current_qty < qty:
                    raise BusinessRuleError(
                        f"Insufficient addon stock",
                        {"addon_id": addon_id, "required": qty, "available": current_qty}
                    )
                
                # Deduct stock
                await session.execute(
                    update(MachineAddon)
                    .where(
                        and_(
                            MachineAddon.machine_id == machine_id,
                            MachineAddon.addon_id == addon_id
                        )
                    )
                    .values(qty_available=MachineAddon.qty_available - qty)
                )
            
            return True
        except Exception as e:
            logger.error(f"Error deducting stock: {e}")
            raise
    
    async def validate_machine_for_order(self, session: AsyncSession, machine_id: UUID) -> bool:
        """Validate machine is ready for order processing"""
        try:
            machine = await self.get_by_id(session, machine_id)
            
            if not machine:
                raise NotFoundError(f"Machine {machine_id} not found")
            
            if machine.status != 'active':
                raise BusinessRuleError(
                    f"Machine is not active (status: {machine.status})",
                    {"machine_status": machine.status}
                )
            
            # Check for existing processing orders
            is_available = await self.check_machine_availability(session, machine_id)
            if not is_available:
                raise BusinessRuleError(
                    "Machine is currently processing another order",
                    {"machine_id": machine_id}
                )
            
            return True
        except Exception as e:
            logger.error(f"Error validating machine for order: {e}")
            raise
    
    async def get_ingredient_stock(
        self, 
        session: AsyncSession, 
        machine_id: UUID, 
        ingredient_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get current ingredient stock for a machine"""
        try:
            result = await session.execute(
                select(MachineIngredient)
                .where(
                    and_(
                        MachineIngredient.machine_id == machine_id,
                        MachineIngredient.ingredient_id == ingredient_id
                    )
                )
            )
            machine_ingredient = result.scalar_one_or_none()
            
            if machine_ingredient:
                return {
                    "qty_available_g": machine_ingredient.qty_available_g,
                    "low_stock_threshold_g": machine_ingredient.low_stock_threshold_g
                }
            return None
        except Exception as e:
            logger.error(f"Error getting ingredient stock: {e}")
            raise DatabaseError("Failed to get ingredient stock")
    
    async def get_addon_stock(
        self, 
        session: AsyncSession, 
        machine_id: UUID, 
        addon_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get current addon stock for a machine"""
        try:
            result = await session.execute(
                select(MachineAddon)
                .where(
                    and_(
                        MachineAddon.machine_id == machine_id,
                        MachineAddon.addon_id == addon_id
                    )
                )
            )
            machine_addon = result.scalar_one_or_none()
            
            if machine_addon:
                return {
                    "qty_available": machine_addon.qty_available,
                    "low_stock_threshold": machine_addon.low_stock_threshold
                }
            return None
        except Exception as e:
            logger.error(f"Error getting addon stock: {e}")
            raise DatabaseError("Failed to get addon stock")
    
    async def get_ingredient_stock_all_machines(
        self, 
        session: AsyncSession, 
        ingredient_id: UUID
    ) -> bool:
        """Check if ingredient exists in any machine"""
        try:
            result = await session.execute(
                select(func.count(MachineIngredient.id))
                .where(MachineIngredient.ingredient_id == ingredient_id)
            )
            count = result.scalar()
            return count > 0
        except Exception as e:
            logger.error(f"Error checking ingredient stock across machines: {e}")
            raise DatabaseError("Failed to check ingredient stock")
    
    async def get_addon_stock_all_machines(
        self, 
        session: AsyncSession, 
        addon_id: UUID
    ) -> bool:
        """Check if addon exists in any machine"""
        try:
            result = await session.execute(
                select(func.count(MachineAddon.id))
                .where(MachineAddon.addon_id == addon_id)
            )
            count = result.scalar()
            return count > 0
        except Exception as e:
            logger.error(f"Error checking addon stock across machines: {e}")
            raise DatabaseError("Failed to check addon stock")
    
    async def update_ingredient_thresholds(
        self, 
        session: AsyncSession, 
        ingredient_id: UUID, 
        low_stock_threshold_g: int
    ) -> bool:
        """Update ingredient threshold across all machines"""
        try:
            result = await session.execute(
                update(MachineIngredient)
                .where(MachineIngredient.ingredient_id == ingredient_id)
                .values(low_stock_threshold_g=low_stock_threshold_g)
            )
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating ingredient thresholds: {e}")
            raise DatabaseError("Failed to update ingredient thresholds")
    
    async def update_addon_thresholds(
        self, 
        session: AsyncSession, 
        addon_id: UUID, 
        low_stock_threshold: int
    ) -> bool:
        """Update addon threshold across all machines"""
        try:
            result = await session.execute(
                update(MachineAddon)
                .where(MachineAddon.addon_id == addon_id)
                .values(low_stock_threshold=low_stock_threshold)
            )
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating addon thresholds: {e}")
            raise DatabaseError("Failed to update addon thresholds")
