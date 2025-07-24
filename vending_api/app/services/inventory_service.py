from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
import logging

from app.dao.machine_dao import MachineDAO
from app.models.machine import VendingMachine, MachineIngredient, MachineAddon
from app.models.product import Ingredient, Addon
from app.schemas.machine import (
    IngredientStockUpdate,
    AddonStockUpdate,
    BulkRestockRequest,
    BulkRestockItem,
    LowStockAlert,
    ThresholdUpdate,
    MachineInventoryResponse,
    MachineInventoryItemResponse
)
from app.utils.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for managing machine inventory"""
    
    def __init__(self):
        self.machine_dao = MachineDAO()

    async def get_machine_inventory_admin(
        self, 
        session: AsyncSession,
        machine_id: UUID,
        include_out_of_stock: bool = False
    ) -> MachineInventoryResponse:
        """Get full inventory with stock levels for admin view"""
        try:
            # Get machine with inventory
            stmt = select(VendingMachine).options(
                selectinload(VendingMachine.machine_ingredients).selectinload(MachineIngredient.ingredient),
                selectinload(VendingMachine.machine_addons).selectinload(MachineAddon.addon)
            ).where(VendingMachine.id == machine_id)
            
            result = await session.execute(stmt)
            machine = result.scalar_one_or_none()
            
            if not machine:
                raise NotFoundError(f"Machine {machine_id} not found")
            
            # Build ingredient inventory
            ingredients = []
            for mi in machine.machine_ingredients:
                if not include_out_of_stock and mi.qty_available_g <= 0:
                    continue
                    
                ingredients.append(MachineInventoryItemResponse(
                    id=mi.ingredient.id,
                    name=mi.ingredient.name,
                    emoji=mi.ingredient.emoji,
                    qty_available=mi.qty_available_g,
                    unit="g",
                    low_stock_threshold=mi.low_stock_threshold_g,
                    is_low_stock=mi.qty_available_g <= mi.low_stock_threshold_g,
                    price_per_unit=mi.ingredient.price_per_gram
                ))
            
            # Build addon inventory  
            addons = []
            for ma in machine.machine_addons:
                if not include_out_of_stock and ma.qty_available <= 0:
                    continue
                    
                addons.append(MachineInventoryItemResponse(
                    id=ma.addon.id,
                    name=ma.addon.name,
                    emoji=ma.addon.icon,  # addon uses 'icon' field
                    qty_available=ma.qty_available,
                    unit="units",
                    low_stock_threshold=ma.low_stock_threshold,
                    is_low_stock=ma.qty_available <= ma.low_stock_threshold,
                    price_per_unit=ma.addon.price
                ))
            
            return MachineInventoryResponse(
                machine_id=machine.id,
                machine_location=machine.location,
                machine_status=machine.status,
                ingredients=ingredients,
                addons=addons,
                last_updated=machine.updated_at
            )
            
        except Exception as e:
            logger.error(f"Error getting machine inventory admin {machine_id}: {e}")
            raise

    async def update_ingredient_stock(
        self,
        session: AsyncSession,
        machine_id: UUID,
        ingredient_id: UUID,
        stock_update: IngredientStockUpdate
    ) -> Dict[str, Any]:
        """Update ingredient stock for a machine"""
        try:
            # Find machine ingredient record
            stmt = select(MachineIngredient).where(
                and_(
                    MachineIngredient.machine_id == machine_id,
                    MachineIngredient.ingredient_id == ingredient_id
                )
            )
            result = await session.execute(stmt)
            machine_ingredient = result.scalar_one_or_none()
            
            if not machine_ingredient:
                # Create new machine ingredient record if it doesn't exist
                machine_ingredient = MachineIngredient(
                    machine_id=machine_id,
                    ingredient_id=ingredient_id,
                    qty_available_g=stock_update.qty_available_g,
                    low_stock_threshold_g=stock_update.low_stock_threshold_g or 0
                )
                session.add(machine_ingredient)
            else:
                # Update existing record
                machine_ingredient.qty_available_g = stock_update.qty_available_g
                if stock_update.low_stock_threshold_g is not None:
                    machine_ingredient.low_stock_threshold_g = stock_update.low_stock_threshold_g
            
            await session.commit()
            
            return {
                "machine_id": machine_id,
                "ingredient_id": ingredient_id,
                "qty_available_g": machine_ingredient.qty_available_g,
                "low_stock_threshold_g": machine_ingredient.low_stock_threshold_g,
                "is_low_stock": machine_ingredient.qty_available_g <= machine_ingredient.low_stock_threshold_g
            }
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating ingredient stock: {e}")
            raise

    async def update_addon_stock(
        self,
        session: AsyncSession,
        machine_id: UUID,
        addon_id: UUID,
        stock_update: AddonStockUpdate
    ) -> Dict[str, Any]:
        """Update addon stock for a machine"""
        try:
            # Find machine addon record
            stmt = select(MachineAddon).where(
                and_(
                    MachineAddon.machine_id == machine_id,
                    MachineAddon.addon_id == addon_id
                )
            )
            result = await session.execute(stmt)
            machine_addon = result.scalar_one_or_none()
            
            if not machine_addon:
                # Create new machine addon record if it doesn't exist
                machine_addon = MachineAddon(
                    machine_id=machine_id,
                    addon_id=addon_id,
                    qty_available=stock_update.qty_available,
                    low_stock_threshold=stock_update.low_stock_threshold or 0
                )
                session.add(machine_addon)
            else:
                # Update existing record
                machine_addon.qty_available = stock_update.qty_available
                if stock_update.low_stock_threshold is not None:
                    machine_addon.low_stock_threshold = stock_update.low_stock_threshold
            
            await session.commit()
            
            return {
                "machine_id": machine_id,
                "addon_id": addon_id,
                "qty_available": machine_addon.qty_available,
                "low_stock_threshold": machine_addon.low_stock_threshold,
                "is_low_stock": machine_addon.qty_available <= machine_addon.low_stock_threshold
            }
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating addon stock: {e}")
            raise

    async def bulk_restock(
        self,
        session: AsyncSession,
        machine_id: UUID,
        restock_request: BulkRestockRequest
    ) -> Dict[str, Any]:
        """Perform bulk restock operation"""
        try:
            updated_ingredients = 0
            updated_addons = 0
            errors = []
            
            for item in restock_request.items:
                try:
                    if item.item_type == "ingredient":
                        # Find existing ingredient stock
                        stmt = select(MachineIngredient).where(
                            and_(
                                MachineIngredient.machine_id == machine_id,
                                MachineIngredient.ingredient_id == item.item_id
                            )
                        )
                        result = await session.execute(stmt)
                        machine_ingredient = result.scalar_one_or_none()
                        
                        if machine_ingredient:
                            machine_ingredient.qty_available_g += item.qty_to_add
                            updated_ingredients += 1
                        else:
                            errors.append(f"Ingredient {item.item_id} not found for machine {machine_id}")
                    
                    elif item.item_type == "addon":
                        # Find existing addon stock
                        stmt = select(MachineAddon).where(
                            and_(
                                MachineAddon.machine_id == machine_id,
                                MachineAddon.addon_id == item.item_id
                            )
                        )
                        result = await session.execute(stmt)
                        machine_addon = result.scalar_one_or_none()
                        
                        if machine_addon:
                            machine_addon.qty_available += item.qty_to_add
                            updated_addons += 1
                        else:
                            errors.append(f"Addon {item.item_id} not found for machine {machine_id}")
                            
                except Exception as e:
                    errors.append(f"Error updating {item.item_type} {item.item_id}: {str(e)}")
            
            await session.commit()
            
            return {
                "machine_id": machine_id,
                "updated_ingredients": updated_ingredients,
                "updated_addons": updated_addons,
                "total_items_updated": updated_ingredients + updated_addons,
                "errors": errors
            }
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during bulk restock: {e}")
            raise

    async def get_low_stock_alerts(
        self,
        session: AsyncSession,
        machine_id: Optional[UUID] = None,
        severity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LowStockAlert]:
        """Get low stock and out-of-stock alerts"""
        try:
            alerts = []
            
            # Get ingredient alerts
            ingredient_stmt = select(MachineIngredient, Ingredient, VendingMachine).join(
                Ingredient, MachineIngredient.ingredient_id == Ingredient.id
            ).join(
                VendingMachine, MachineIngredient.machine_id == VendingMachine.id
            ).where(
                MachineIngredient.qty_available_g <= MachineIngredient.low_stock_threshold_g
            )
            
            if machine_id:
                ingredient_stmt = ingredient_stmt.where(MachineIngredient.machine_id == machine_id)
            
            ingredient_result = await session.execute(ingredient_stmt)
            
            for mi, ingredient, machine in ingredient_result:
                percentage_remaining = (mi.qty_available_g / max(mi.low_stock_threshold_g, 1)) * 100
                
                if mi.qty_available_g == 0:
                    priority = "critical"
                elif percentage_remaining <= 25:
                    priority = "critical"
                elif percentage_remaining <= 50:
                    priority = "warning"
                else:
                    priority = "info"
                
                if severity and (
                    (severity == "out" and mi.qty_available_g > 0) or
                    (severity == "low" and mi.qty_available_g == 0)
                ):
                    continue
                
                alerts.append(LowStockAlert(
                    machine_id=machine.id,
                    machine_location=machine.location,
                    item_id=ingredient.id,
                    item_name=ingredient.name,
                    item_type="ingredient",
                    current_qty=mi.qty_available_g,
                    threshold=mi.low_stock_threshold_g,
                    percentage_remaining=percentage_remaining,
                    priority=priority,
                    last_updated=mi.updated_at
                ))
            
            # Get addon alerts
            addon_stmt = select(MachineAddon, Addon, VendingMachine).join(
                Addon, MachineAddon.addon_id == Addon.id
            ).join(
                VendingMachine, MachineAddon.machine_id == VendingMachine.id
            ).where(
                MachineAddon.qty_available <= MachineAddon.low_stock_threshold
            )
            
            if machine_id:
                addon_stmt = addon_stmt.where(MachineAddon.machine_id == machine_id)
            
            addon_result = await session.execute(addon_stmt)
            
            for ma, addon, machine in addon_result:
                percentage_remaining = (ma.qty_available / max(ma.low_stock_threshold, 1)) * 100
                
                if ma.qty_available == 0:
                    priority = "critical"
                elif percentage_remaining <= 25:
                    priority = "critical"
                elif percentage_remaining <= 50:
                    priority = "warning"
                else:
                    priority = "info"
                
                if severity and (
                    (severity == "out" and ma.qty_available > 0) or
                    (severity == "low" and ma.qty_available == 0)
                ):
                    continue
                
                alerts.append(LowStockAlert(
                    machine_id=machine.id,
                    machine_location=machine.location,
                    item_id=addon.id,
                    item_name=addon.name,
                    item_type="addon",
                    current_qty=ma.qty_available,
                    threshold=ma.low_stock_threshold,
                    percentage_remaining=percentage_remaining,
                    priority=priority,
                    last_updated=ma.updated_at
                ))
            
            # Sort by priority and apply pagination
            priority_order = {"critical": 0, "warning": 1, "info": 2}
            alerts.sort(key=lambda x: (priority_order.get(x.priority, 3), x.machine_location, x.item_name))
            
            return alerts[skip:skip + limit]
            
        except Exception as e:
            logger.error(f"Error getting low stock alerts: {e}")
            raise

    async def update_stock_thresholds(
        self,
        session: AsyncSession,
        threshold_updates: List[ThresholdUpdate]
    ) -> Dict[str, Any]:
        """Update stock thresholds for multiple items"""
        try:
            updated_count = 0
            errors = []
            
            for update in threshold_updates:
                try:
                    if update.item_type == "ingredient":
                        stmt = select(MachineIngredient).where(
                            MachineIngredient.ingredient_id == update.item_id
                        )
                        result = await session.execute(stmt)
                        machine_ingredients = result.scalars().all()
                        
                        for mi in machine_ingredients:
                            mi.low_stock_threshold_g = update.threshold
                            updated_count += 1
                    
                    elif update.item_type == "addon":
                        stmt = select(MachineAddon).where(
                            MachineAddon.addon_id == update.item_id
                        )
                        result = await session.execute(stmt)
                        machine_addons = result.scalars().all()
                        
                        for ma in machine_addons:
                            ma.low_stock_threshold = update.threshold
                            updated_count += 1
                            
                except Exception as e:
                    errors.append(f"Error updating threshold for {update.item_type} {update.item_id}: {str(e)}")
            
            await session.commit()
            
            return {
                "updated_count": updated_count,
                "errors": errors
            }
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating stock thresholds: {e}")
            raise
