from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import logging

from app.dao.order_dao import OrderDAO
from app.dao.machine_dao import MachineDAO
from app.models.order import Order
from app.models.product import Ingredient, Addon
from app.schemas.order import (
    OrderCreateRequest, OrderResponse, OrderStatusUpdate,
    OrderItemResponse, OrderAddonResponse
)
from app.utils.exceptions import (
    ValidationError, 
    BusinessRuleError, 
    OrderProcessingError,
    InsufficientStockError
)
from app.config.database import get_async_db, get_async_transaction
from app.ros.ros_interface import RosInterface

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order processing with transaction management"""
    
    def __init__(self):
        self.order_dao = OrderDAO()
        self.machine_dao = MachineDAO()
        self.ros_interface = RosInterface.get_instance()
    async def create_order(
        self, 
        order_request: OrderCreateRequest,
        session_id: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> OrderResponse:
        """Create a new order with full transaction support"""
        try:
            async with get_async_transaction() as session:
                # Validate the order request
                await self._validate_order_request(session, order_request)
                
                # Convert Pydantic models to dictionaries
                ingredients_dict = [item.dict() for item in order_request.ingredients]
                addons_dict = [addon.dict() for addon in order_request.addons]
                liquids_dict = order_request.liquids if isinstance(order_request.liquids, list) else []
                
                # Create the order with all items (liquids not saved to DB)
                order = await self.order_dao.create_order_with_items(
                    session=session,
                    machine_id=order_request.machine_id,
                    user_id=user_id,
                    session_id=session_id,
                    total_price=order_request.total_price,
                    total_calories=order_request.total_calories,
                    status=order_request.status,
                    ingredients=ingredients_dict,
                    addons=addons_dict,
                    liquids=liquids_dict
                )
                
                # Generate order string for successful order (uses liquids for dynamic amounts)
                order_string = self._generate_order_string(order, liquids_dict)
                logger.info(f"ORDER CREATED: {order_string}")

                self.ros_interface.publish_order_string(order_string)
                
                # Convert to response schema
                return await self._order_to_response(session, order, order_string)
                
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise OrderProcessingError(f"Failed to create order: {str(e)}")
    
    async def get_order(self, session: AsyncSession, order_id: UUID) -> Optional[OrderResponse]:
        """Get order by ID"""
        try:
            order = await self.order_dao.get_order_with_details(session, order_id)
            if not order:
                return None
            
            return await self._order_to_response(session, order)
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            raise
    
    async def update_order_status(
        self, 
        session: AsyncSession,
        order_id: UUID, 
        status_update: OrderStatusUpdate
    ) -> Optional[OrderResponse]:
        """Update order status"""
        try:
            # Update order status using the existing session
            order = await self.order_dao.update_order_status(
                session,
                order_id,
                status_update.status,
                status_update.payment_status,
                status_update.notes
            )
            
            if not order:
                return None
                
            # Get the order with all details for the response
            detailed_order = await self.order_dao.get_order_with_details(session, order_id)
            if not detailed_order:
                return None
                
            return await self._order_to_response(session, detailed_order)
                
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            raise
    
    async def get_orders_by_machine(
        self, 
        session: AsyncSession,
        machine_id: UUID,
        status_filter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[OrderResponse]:
        """Get orders for a machine with filters"""
        try:
            # Get orders with all relationships pre-loaded
            orders = await self.order_dao.get_orders_by_machine(
                session, machine_id, status_filter, date_from, date_to, skip, limit
            )
            
            # Convert to response format
            order_responses = []
            for order in orders:
                try:
                    response = await self._order_to_response(session, order)
                    order_responses.append(response)
                except Exception as e:
                    logger.warning(f"Error converting order {order.id} to response: {e}")
                    # Skip this order and continue with others
                    continue
            
            return order_responses
        except Exception as e:
            logger.error(f"Error getting orders by machine: {e}")
            raise
    
    async def get_order_statistics(
        self, 
        session: AsyncSession,
        machine_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get order statistics"""
        try:
            return await self.order_dao.get_order_statistics(
                session, machine_id, date_from, date_to
            )
        except Exception as e:
            logger.error(f"Error getting order statistics: {e}")
            raise
    
    async def get_popular_items(
        self, 
        session: AsyncSession,
        machine_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get popular items"""
        try:
            return await self.order_dao.get_popular_items(
                session, machine_id, date_from, date_to, limit
            )
        except Exception as e:
            logger.error(f"Error getting popular items: {e}")
            raise
    
    async def _validate_order_request(
        self, 
        session: AsyncSession, 
        order_request: OrderCreateRequest
    ) -> bool:
        """Validate order request"""
        try:
            # Validate machine exists and is available
            await self.machine_dao.validate_machine_for_order(session, order_request.machine_id)
            
            # Validate ingredients and addons exist
            await self._validate_ingredients_exist(session, order_request.ingredients)
            await self._validate_addons_exist(session, order_request.addons)
            
            # Validate ingredient constraints
            await self._validate_ingredient_constraints(session, order_request.ingredients)
            
            return True
        except Exception as e:
            logger.error(f"Error validating order request: {e}")
            raise
    
    async def _validate_ingredients_exist(
        self, 
        session: AsyncSession, 
        ingredients: List
    ) -> bool:
        """Validate that all ingredients exist"""
        for ingredient_data in ingredients:
            # Handle both Pydantic objects and dictionaries
            ingredient_id = ingredient_data.ingredient_id if hasattr(ingredient_data, 'ingredient_id') else ingredient_data['ingredient_id']
            ingredient = await session.get(Ingredient, ingredient_id)
            if not ingredient:
                raise ValidationError(f"Ingredient {ingredient_id} not found")
        return True
    
    async def _validate_addons_exist(
        self, 
        session: AsyncSession, 
        addons: List
    ) -> bool:
        """Validate that all addons exist"""
        for addon_data in addons:
            # Handle both Pydantic objects and dictionaries
            addon_id = addon_data.addon_id if hasattr(addon_data, 'addon_id') else addon_data['addon_id']
            addon = await session.get(Addon, addon_id)
            if not addon:
                raise ValidationError(f"Addon {addon_id} not found")
        return True
    
    async def _validate_ingredient_constraints(
        self, 
        session: AsyncSession, 
        ingredients: List
    ) -> bool:
        """Validate ingredient constraints (min_qty_g, max_percent_limit)"""
        # Handle both Pydantic objects and dictionaries
        total_grams = sum(
            ingredient.grams_used if hasattr(ingredient, 'grams_used') else ingredient['grams_used'] 
            for ingredient in ingredients
        )
        
        for ingredient_data in ingredients:
            # Handle both Pydantic objects and dictionaries
            ingredient_id = ingredient_data.ingredient_id if hasattr(ingredient_data, 'ingredient_id') else ingredient_data['ingredient_id']
            grams_used = ingredient_data.grams_used if hasattr(ingredient_data, 'grams_used') else ingredient_data['grams_used']
            
            ingredient = await session.get(Ingredient, ingredient_id)
            if not ingredient:
                continue
            
            # Check minimum quantity
            if grams_used < ingredient.min_qty_g:
                raise ValidationError(
                    f"Ingredient {ingredient.name} requires minimum {ingredient.min_qty_g}g, got {grams_used}g"
                )
            
            # Check maximum percentage
            if total_grams > 0:
                percentage = (grams_used / total_grams) * 100
                if percentage > ingredient.max_percent_limit:
                    raise ValidationError(
                        f"Ingredient {ingredient.name} exceeds maximum {ingredient.max_percent_limit}% limit"
                    )
        
        return True
    
    def _generate_order_string(self, order: Order, liquids: Optional[List[Dict[str, Any]]] = None) -> str:
        """Generate formatted order string with dispensing process details"""
        try:
            process_steps = []
            
            # Step 1: Determine container type from session_id
            container_type = "1 container"  # Default fallback
            is_smoothie = False
            is_salad = False
            
            if order.session_id:
                if order.session_id.startswith("smoothie-"):
                    container_type = "1 cup"
                    is_smoothie = True
                elif order.session_id.startswith("salad-"):
                    container_type = "1 bowl"
                    is_salad = True
            
            # Add container dispensing
            process_steps.append(container_type)
            
            # Step 2: Dispense all ingredients
            if order.order_items:
                for item in order.order_items:
                    ingredient_name = "Unknown Item"
                    if item.ingredient:
                        ingredient_name = item.ingredient.name or "Unknown Item"
                    
                    # Format: "dispense item_name qty"
                    if item.qty_ml and item.qty_ml > 0:
                        process_steps.append(f"dispense {ingredient_name} {item.qty_ml}ml")
                    elif item.grams_used and item.grams_used > 0:
                        process_steps.append(f"dispense {ingredient_name} {item.grams_used}g")
                    else:
                        process_steps.append(f"dispense {ingredient_name}")
            
            # Step 3: Add all addons
            if order.order_addons:
                for addon in order.order_addons:
                    addon_name = "Unknown Addon"
                    if addon.addon:
                        addon_name = addon.addon.name or "Unknown Addon"
                    
                    qty = addon.qty or 1
                    process_steps.append(f"add {addon_name} x{qty}")
            
            # Step 4: Move to next chamber AFTER all items and addons are dispensed
            if order.order_items or order.order_addons:
                process_steps.append("move to next chamber")
            
            # Step 5: Add dynamic liquid components based on liquids from UI and order type
            if liquids:
                for liquid in liquids:
                    liquid_name = liquid.get('liquid_name', 'liquid')
                    qty = liquid.get('qty', '0 ml')
                    process_steps.append(f"add {qty} {liquid_name}")
            # elif is_smoothie:
            #     process_steps.append("add 50ml milk")
            #     process_steps.append("add 50ml hot water")
            # elif is_salad:
            #     process_steps.append("add 50ml salad dressing 1")
            #     process_steps.append("add 50ml salad dressing 2")
            else:
                # Default for unknown types
                process_steps.append("add finishing touches")
            
            # Join all steps with ", "
            order_string = ", ".join(process_steps)
            
            # Add order ID and timestamp for reference
            order_timestamp = order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "Unknown time"
            final_string = f"Order #{str(order.id)[:8]} - {order_string} - {order_timestamp}"
            
            return final_string
            
        except Exception as e:
            logger.error(f"Error generating order string for order {order.id}: {e}")
            return f"Order #{str(order.id)[:8]} - Order details unavailable"
    
    async def get_order_string(self, session: AsyncSession, order_id: UUID) -> str:
        """Get formatted order string for existing order"""
        try:
            order = await self.order_dao.get_order_with_details(session, order_id)
            if not order:
                return f"Order #{str(order_id)[:8]} - Order not found"
            
            return self._generate_order_string(order)
        except Exception as e:
            logger.error(f"Error getting order string for {order_id}: {e}")
            return f"Order #{str(order_id)[:8]} - Error retrieving order details"
    
    async def _order_to_response(self, session: AsyncSession, order: Order, order_string: Optional[str] = None) -> OrderResponse:
        """Convert Order model to OrderResponse schema"""
        try:
            # Transform order items with safe attribute access
            items = []
            if order.order_items:
                for item in order.order_items:
                    ingredient_name = "Unknown"
                    ingredient_emoji = None
                    
                    if item.ingredient:
                        ingredient_name = item.ingredient.name or "Unknown"
                        ingredient_emoji = item.ingredient.emoji
                    
                    items.append(OrderItemResponse(
                        id=item.id,
                        ingredient_id=item.ingredient_id,
                        ingredient_name=ingredient_name,
                        ingredient_emoji=ingredient_emoji,
                        qty_ml=item.qty_ml or 0,
                        grams_used=item.grams_used or 0,
                        calories=item.calories or 0
                    ))
            
            # Transform order addons with safe attribute access
            addons = []
            if order.order_addons:
                for addon in order.order_addons:
                    addon_name = "Unknown"
                    addon_icon = None
                    
                    if addon.addon:
                        addon_name = addon.addon.name or "Unknown"
                        addon_icon = addon.addon.icon
                    
                    addons.append(OrderAddonResponse(
                        id=addon.id,
                        addon_id=addon.addon_id,
                        addon_name=addon_name,
                        addon_icon=addon_icon,
                        qty=addon.qty or 1,
                        calories=addon.calories or 0
                    ))
            
            # Get machine location with safe attribute access
            machine_location = None
            if order.machine:
                machine_location = order.machine.location
            
            return OrderResponse(
                id=order.id,
                machine_id=order.machine_id,
                machine_location=machine_location,
                user_id=order.user_id,
                session_id=order.session_id,
                status=order.status or "unknown",
                total_price=order.total_price or 0,
                total_calories=order.total_calories or 0,
                created_at=order.created_at,
                items=items,
                addons=addons,
                order_string=order_string or self._generate_order_string(order)
            )
        except Exception as e:
            logger.error(f"Error converting order {order.id} to response: {e}")
            # Return a minimal response to prevent complete failure
            return OrderResponse(
                id=order.id,
                machine_id=order.machine_id,
                machine_location=None,
                user_id=order.user_id,
                session_id=order.session_id,
                status=order.status or "unknown",
                total_price=order.total_price or 0,
                total_calories=order.total_calories or 0,
                created_at=order.created_at,
                items=[],
                addons=[],
                order_string=order_string or f"Order #{str(order.id)[:8]} - Order details unavailable"
            )
