"""
Enhanced Machine Service with full schema alignment.
Handles machine operations, inventory management, and status updates.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, and_, or_
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from app.dao.machine_dao import MachineDAO
from app.dao.view_dao import MachineInventoryViewDAO, DashboardViewDAO, PresetViewDAO
from app.models.machine import VendingMachine, MachineIngredient, MachineAddon
from app.models.product import Ingredient, Addon
from app.schemas.machine import (
    MachineCreate, MachineUpdate, MachineResponse,
    MachineInventoryResponse, MachineMetrics,
    IngredientStockUpdate, AddonStockUpdate,
    BulkRestockRequest, LowStockAlert
)
from app.utils.exceptions import NotFoundError, BusinessRuleError, DatabaseError

logger = logging.getLogger(__name__)


class EnhancedMachineService:
    """Enhanced machine service with full database schema support"""
    
    def __init__(self):
        self.machine_dao = MachineDAO()
        self.inventory_view_dao = MachineInventoryViewDAO()
        self.dashboard_view_dao = DashboardViewDAO()
        self.preset_view_dao = PresetViewDAO()
    
    async def create_machine(
        self, 
        session: AsyncSession, 
        machine_data: MachineCreate
    ) -> MachineResponse:
        """Create a new vending machine"""
        try:
            machine = await self.machine_dao.create(
                session,
                location=machine_data.location,
                status=machine_data.status,
                cups_qty=machine_data.cups_qty,
                bowls_qty=machine_data.bowls_qty
            )
            
            return MachineResponse(
                id=machine.id,
                location=machine.location,
                status=machine.status,
                cups_qty=machine.cups_qty,
                bowls_qty=machine.bowls_qty,
                created_at=machine.created_at
            )
        except Exception as e:
            logger.error(f"Error creating machine: {e}")
            raise
    
    async def get_machine_complete_inventory(
        self, 
        session: AsyncSession, 
        machine_id: UUID
    ) -> Dict[str, Any]:
        """Get complete machine inventory using database views"""
        try:
            # Get ingredients inventory
            ingredients = await self.inventory_view_dao.get_machine_ingredient_inventory(
                session, machine_id
            )
            
            # Get addons inventory
            addons = await self.inventory_view_dao.get_machine_addon_inventory(
                session, machine_id
            )
            
            # Get machine info
            machine = await self.machine_dao.get_by_id(session, machine_id)
            if not machine:
                raise NotFoundError(f"Machine {machine_id} not found")
            
            return {
                "machine_id": machine_id,
                "machine_location": machine.location,
                "machine_status": machine.status,
                "cups_qty": machine.cups_qty,
                "bowls_qty": machine.bowls_qty,
                "ingredients": ingredients,
                "addons": addons,
                "total_ingredients": len(ingredients),
                "total_addons": len(addons),
                "ingredients_available": len([i for i in ingredients if i.get('stock_status') == 'AVAILABLE']),
                "ingredients_low_stock": len([i for i in ingredients if i.get('stock_status') == 'LOW_STOCK']),
                "ingredients_out_of_stock": len([i for i in ingredients if i.get('stock_status') == 'OUT_OF_STOCK']),
                "addons_available": len([a for a in addons if a.get('stock_status') == 'AVAILABLE']),
                "addons_low_stock": len([a for a in addons if a.get('stock_status') == 'LOW_STOCK']),
                "addons_out_of_stock": len([a for a in addons if a.get('stock_status') == 'OUT_OF_STOCK']),
                "last_updated": machine.created_at
            }
        except Exception as e:
            logger.error(f"Error getting complete machine inventory: {e}")
            raise
    
    async def get_low_stock_alerts(
        self, 
        session: AsyncSession, 
        machine_id: Optional[UUID] = None
    ) -> List[LowStockAlert]:
        """Get low stock alerts using database views"""
        try:
            machine_location = None
            if machine_id:
                machine = await self.machine_dao.get_by_id(session, machine_id)
                if machine:
                    machine_location = machine.location
            
            alerts_data = await self.dashboard_view_dao.get_low_stock_alerts(
                session, machine_location
            )
            
            alerts = []
            for alert in alerts_data:
                alerts.append(LowStockAlert(
                    machine_location=alert['machine_location'],
                    item_type=alert['item_type'],
                    item_name=alert['item_name'],
                    current_stock=alert['current_stock'],
                    threshold=alert['threshold'],
                    alert_level=alert['alert_level'],
                    priority=alert['priority_order']
                ))
            
            return alerts
        except Exception as e:
            logger.error(f"Error getting low stock alerts: {e}")
            raise
    
    async def bulk_restock(
        self, 
        session: AsyncSession, 
        machine_id: UUID,
        restock_data: BulkRestockRequest
    ) -> Dict[str, Any]:
        """Perform bulk restock operation"""
        try:
            results = {
                "machine_id": machine_id,
                "ingredients_updated": 0,
                "addons_updated": 0,
                "errors": []
            }
            
            # Update ingredients
            for ingredient_update in restock_data.ingredients:
                try:
                    await self.machine_dao.update_ingredient_stock(
                        session, machine_id, ingredient_update.ingredient_id,
                        ingredient_update.qty_available_g,
                        ingredient_update.low_stock_threshold_g
                    )
                    results["ingredients_updated"] += 1
                except Exception as e:
                    results["errors"].append(f"Ingredient {ingredient_update.ingredient_id}: {str(e)}")
            
            # Update addons
            for addon_update in restock_data.addons:
                try:
                    await self.machine_dao.update_addon_stock(
                        session, machine_id, addon_update.addon_id,
                        addon_update.qty_available,
                        addon_update.low_stock_threshold
                    )
                    results["addons_updated"] += 1
                except Exception as e:
                    results["errors"].append(f"Addon {addon_update.addon_id}: {str(e)}")
            
            return results
        except Exception as e:
            logger.error(f"Error performing bulk restock: {e}")
            raise
    
    async def get_machine_performance_metrics(
        self, 
        session: AsyncSession, 
        machine_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get machine performance metrics using dashboard views"""
        try:
            # Get dashboard data for the machine
            dashboard_data = await self.dashboard_view_dao.get_machine_dashboard_data(
                session, machine_id
            )
            
            if not dashboard_data:
                raise NotFoundError(f"No dashboard data found for machine {machine_id}")
            
            machine_metrics = dashboard_data[0]
            
            # Calculate additional metrics
            total_stock_items = (
                machine_metrics.get('total_ingredients', 0) + 
                machine_metrics.get('total_addons', 0)
            )
            
            available_items = (
                machine_metrics.get('ingredients_in_stock', 0) + 
                machine_metrics.get('addons_in_stock', 0)
            )
            
            availability_percentage = (
                (available_items / total_stock_items * 100) if total_stock_items > 0 else 0
            )
            
            return {
                "machine_id": machine_id,
                "location": machine_metrics.get('machine_location'),
                "status": machine_metrics.get('machine_status'),
                "performance_metrics": {
                    "orders_last_30_days": machine_metrics.get('orders_last_30_days', 0),
                    "revenue_last_30_days": float(machine_metrics.get('revenue_last_30_days', 0)),
                    "orders_today": machine_metrics.get('orders_today', 0),
                    "last_order_date": machine_metrics.get('last_order_date'),
                    "availability_percentage": round(availability_percentage, 2),
                    "total_stock_items": total_stock_items,
                    "available_items": available_items,
                    "low_stock_items": (
                        machine_metrics.get('ingredients_low_stock', 0) + 
                        machine_metrics.get('addons_low_stock', 0)
                    ),
                    "out_of_stock_items": (
                        machine_metrics.get('ingredients_out_of_stock', 0) + 
                        machine_metrics.get('addons_out_of_stock', 0)
                    )
                },
                "inventory_summary": {
                    "cups_qty": machine_metrics.get('cups_qty', 0),
                    "bowls_qty": machine_metrics.get('bowls_qty', 0),
                    "ingredients": {
                        "total": machine_metrics.get('total_ingredients', 0),
                        "in_stock": machine_metrics.get('ingredients_in_stock', 0),
                        "low_stock": machine_metrics.get('ingredients_low_stock', 0),
                        "out_of_stock": machine_metrics.get('ingredients_out_of_stock', 0)
                    },
                    "addons": {
                        "total": machine_metrics.get('total_addons', 0),
                        "in_stock": machine_metrics.get('addons_in_stock', 0),
                        "low_stock": machine_metrics.get('addons_low_stock', 0),
                        "out_of_stock": machine_metrics.get('addons_out_of_stock', 0)
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error getting machine performance metrics: {e}")
            raise
    
    async def validate_machine_for_order(
        self, 
        session: AsyncSession, 
        machine_id: UUID,
        required_ingredients: List[Dict[str, Any]],
        required_addons: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate if machine can fulfill an order"""
        try:
            validation_result = {
                "can_fulfill": True,
                "missing_ingredients": [],
                "insufficient_ingredients": [],
                "missing_addons": [],
                "insufficient_addons": [],
                "issues": []
            }
            
            # Check machine status
            machine = await self.machine_dao.get_by_id(session, machine_id)
            if not machine:
                validation_result["can_fulfill"] = False
                validation_result["issues"].append("Machine not found")
                return validation_result
            
            if machine.status != 'active':
                validation_result["can_fulfill"] = False
                validation_result["issues"].append(f"Machine status is {machine.status}")
                return validation_result
            
            # Check ingredient availability
            available_ingredients = await self.inventory_view_dao.get_machine_ingredient_inventory(
                session, machine_id, stock_status='AVAILABLE'
            )
            
            ingredient_lookup = {
                ing['ingredient_id']: ing for ing in available_ingredients
            }
            
            for req_ingredient in required_ingredients:
                ingredient_id = req_ingredient['ingredient_id']
                required_grams = req_ingredient['grams_used']
                
                if ingredient_id not in ingredient_lookup:
                    validation_result["missing_ingredients"].append(ingredient_id)
                    validation_result["can_fulfill"] = False
                elif ingredient_lookup[ingredient_id]['qty_available_g'] < required_grams:
                    validation_result["insufficient_ingredients"].append({
                        "ingredient_id": ingredient_id,
                        "required": required_grams,
                        "available": ingredient_lookup[ingredient_id]['qty_available_g']
                    })
                    validation_result["can_fulfill"] = False
            
            # Check addon availability
            available_addons = await self.inventory_view_dao.get_machine_addon_inventory(
                session, machine_id, stock_status='AVAILABLE'
            )
            
            addon_lookup = {
                addon['addon_id']: addon for addon in available_addons
            }
            
            for req_addon in required_addons:
                addon_id = req_addon['addon_id']
                required_qty = req_addon['qty']
                
                if addon_id not in addon_lookup:
                    validation_result["missing_addons"].append(addon_id)
                    validation_result["can_fulfill"] = False
                elif addon_lookup[addon_id]['qty_available'] < required_qty:
                    validation_result["insufficient_addons"].append({
                        "addon_id": addon_id,
                        "required": required_qty,
                        "available": addon_lookup[addon_id]['qty_available']
                    })
                    validation_result["can_fulfill"] = False
            
            return validation_result
        except Exception as e:
            logger.error(f"Error validating machine for order: {e}")
            raise
