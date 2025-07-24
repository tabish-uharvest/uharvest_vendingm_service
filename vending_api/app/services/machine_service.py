from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from app.dao.machine_dao import MachineDAO
from app.dao.view_dao import MachineInventoryViewDAO, PresetViewDAO
from app.models.machine import VendingMachine
from app.schemas.machine import MachineInventoryResponse, MachineInventoryItemResponse, MachineMetrics, MachineAddonsResponse, MachineAddonResponse, MachineResponse
from app.utils.exceptions import NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class MachineService:
    """Service for machine operations"""
    
    def __init__(self):
        self.machine_dao = MachineDAO()
        self.inventory_view_dao = MachineInventoryViewDAO()
        self.preset_view_dao = PresetViewDAO()
    
    async def get_available_inventory(
        self, 
        session: AsyncSession, 
        machine_id: UUID
    ) -> Optional[MachineInventoryResponse]:
        """Get available inventory for a machine using views for better performance"""
        try:
            # Check if machine exists
            machine = await self.machine_dao.get_by_id(session, machine_id)
            if not machine:
                return None
            
            # Get inventory using views for better performance
            ingredient_data = await self.inventory_view_dao.get_machine_ingredient_inventory(
                session, machine_id, stock_status='AVAILABLE'
            )
            addon_data = await self.inventory_view_dao.get_machine_addon_inventory(
                session, machine_id, stock_status='AVAILABLE'
            )
            
            # Transform ingredient data to MachineInventoryItemResponse
            ingredients = [
                MachineInventoryItemResponse(
                    id=item['ingredient_id'],
                    name=item['ingredient_name'],
                    item_type='ingredient',
                    emoji=item.get('ingredient_emoji'),
                    icon=None,
                    qty_available=item['qty_available_g'],
                    qty_available_unit='grams',
                    low_stock_threshold=item['low_stock_threshold_g'],
                    is_low_stock=item.get('stock_status') == 'LOW_STOCK',
                    is_available=item.get('stock_status') == 'AVAILABLE',
                    price_per_unit=item.get('price_per_gram'),
                    calories_per_unit=item.get('calories_per_g'),
                    min_qty=None,  # Not available in view
                    max_percent_limit=item.get('max_percent_limit')
                )
                for item in ingredient_data
            ]
            
            # Transform addon data to MachineInventoryItemResponse
            addons = [
                MachineInventoryItemResponse(
                    id=item['addon_id'],
                    name=item['addon_name'],
                    item_type='addon',
                    emoji=None,
                    icon=item.get('addon_icon'),
                    qty_available=item['qty_available'],
                    qty_available_unit='units',
                    low_stock_threshold=item['low_stock_threshold'],
                    is_low_stock=item.get('stock_status') == 'LOW_STOCK',
                    is_available=item.get('stock_status') == 'AVAILABLE',
                    price_per_unit=item.get('addon_price'),
                    calories_per_unit=item.get('addon_calories'),
                    min_qty=None,  # Not applicable for addons
                    max_percent_limit=None  # Not applicable for addons
                )
                for item in addon_data
            ]
            
            return MachineInventoryResponse(
                machine_id=machine_id,
                machine_location=machine.location,
                machine_status=machine.status,
                ingredients=ingredients,
                addons=addons,
                last_updated=machine.created_at  # Use created_at since updated_at may not exist
            )
        except Exception as e:
            logger.error(f"Error getting machine inventory: {e}")
            raise
    
    async def get_available_presets(
        self, 
        session: AsyncSession, 
        machine_id: UUID,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get available presets for a machine using views"""
        try:
            # Normalize category to lowercase if provided
            normalized_category = category.lower() if category else None
            
            # Use the preset availability view for accurate results
            presets = await self.preset_view_dao.get_preset_availability_for_machine(
                session, machine_id, normalized_category
            )
            
            logger.info(f"Found {len(presets)} presets for machine {machine_id}, category: {normalized_category}")
            if presets:
                logger.info(f"First preset: {presets[0]}")
            
            # Filter to only return available presets
            available_presets = [preset for preset in presets if preset.get('availability_status') == 'AVAILABLE']
            logger.info(f"Available presets: {len(available_presets)}")
            
            return available_presets
        except Exception as e:
            logger.error(f"Error getting available presets: {e}")
            raise
    
    async def get_machine_status(
        self, 
        session: AsyncSession, 
        machine_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get machine status and availability"""
        try:
            machine = await self.machine_dao.get_by_id(session, machine_id)
            if not machine:
                return None
            
            is_available = await self.machine_dao.check_machine_availability(session, machine_id)
            
            return {
                "machine_id": machine_id,
                "location": machine.location,
                "status": machine.status,
                "is_available": is_available,
                "cups_qty": machine.cups_qty,
                "bowls_qty": machine.bowls_qty,
                "last_updated": machine.created_at  # Use created_at since updated_at doesn't exist
            }
        except Exception as e:
            logger.error(f"Error getting machine status: {e}")
            raise
    
    async def get_machine_metrics(
        self, 
        session: AsyncSession, 
        machine_id: UUID
    ) -> Dict[str, Any]:
        """Get machine performance metrics"""
        try:
            return await self.machine_dao.get_machine_metrics(session, machine_id)
        except Exception as e:
            logger.error(f"Error getting machine metrics: {e}")
            raise
    
    async def get_machine_addons(
        self, 
        session: AsyncSession, 
        machine_id: UUID,
        stock_status: Optional[str] = None
    ) -> Optional[MachineAddonsResponse]:
        """Get addons inventory for a machine using view"""
        try:
            # Check if machine exists
            machine = await self.machine_dao.get_by_id(session, machine_id)
            if not machine:
                return None
            
            # Get addon inventory using view
            addon_data = await self.inventory_view_dao.get_machine_addon_inventory(
                session, machine_id, stock_status
            )
            
            # Transform addon data to MachineAddonResponse
            addons = [
                MachineAddonResponse(
                    machine_id=item['machine_id'],
                    machine_location=item['machine_location'],
                    machine_status=item['machine_status'],
                    addon_id=item['addon_id'],
                    addon_name=item['addon_name'],
                    addon_icon=item.get('addon_icon'),
                    addon_price=item['addon_price'],
                    addon_calories=item['addon_calories'],
                    qty_available=item['qty_available'],
                    low_stock_threshold=item['low_stock_threshold'],
                    stock_status=item['stock_status'],
                    stock_percentage=item['stock_percentage'],
                    inventory_updated_at=item.get('inventory_updated_at')
                )
                for item in addon_data
            ]
            
            # Calculate statistics
            total_addons = len(addons)
            available_addons = sum(1 for addon in addons if addon.stock_status == 'AVAILABLE')
            low_stock_addons = sum(1 for addon in addons if addon.stock_status == 'LOW_STOCK')
            out_of_stock_addons = sum(1 for addon in addons if addon.stock_status == 'OUT_OF_STOCK')
            
            return MachineAddonsResponse(
                machine_id=machine_id,
                machine_location=machine.location,
                machine_status=machine.status,
                addons=addons,
                total_addons=total_addons,
                available_addons=available_addons,
                low_stock_addons=low_stock_addons,
                out_of_stock_addons=out_of_stock_addons
            )
        except Exception as e:
            logger.error(f"Error getting machine addons: {e}")
            raise
    
    async def list_machines(
        self, 
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[MachineResponse]:
        """List all machines with optional filtering"""
        try:
            filters = {}
            if status:
                filters['status'] = status
            
            machines = await self.machine_dao.get_all(
                session, 
                skip=skip, 
                limit=limit, 
                filters=filters,
                order_by="created_at"
            )
            
            return [
                MachineResponse(
                    id=machine.id,
                    location=machine.location,
                    status=machine.status,
                    cups_qty=machine.cups_qty,
                    bowls_qty=machine.bowls_qty,
                    created_at=machine.created_at
                    # Note: updated_at field removed as it doesn't exist in the database schema
                )
                for machine in machines
            ]
        except Exception as e:
            logger.error(f"Error listing machines: {e}")
            raise
        
    async def create_machine(
        self, 
        session: AsyncSession,
        machine_data: dict
    ) -> MachineResponse:
        """Create a new vending machine"""
        try:
            # Create the machine using the DAO
            machine = await self.machine_dao.create(session, **machine_data)
            
            # Return as MachineResponse
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

    async def update_machine(
        self, 
        session: AsyncSession,
        machine_id: UUID,
        machine_data: dict
    ) -> Optional[MachineResponse]:
        """Update a vending machine"""
        try:
            # Update the machine using the DAO
            machine = await self.machine_dao.update(session, machine_id, **machine_data)
            
            if not machine:
                return None
            
            # Return as MachineResponse
            return MachineResponse(
                id=machine.id,
                location=machine.location,
                status=machine.status,
                cups_qty=machine.cups_qty,
                bowls_qty=machine.bowls_qty,
                created_at=machine.created_at
            )
        except Exception as e:
            logger.error(f"Error updating machine: {e}")
            raise

    async def delete_machine(
        self, 
        session: AsyncSession,
        machine_id: UUID
    ) -> bool:
        """Delete a vending machine"""
        try:
            return await self.machine_dao.delete(session, machine_id)
        except Exception as e:
            logger.error(f"Error deleting machine: {e}")
            raise
    
    async def get_full_inventory_admin(
        self, 
        session: AsyncSession, 
        machine_id: UUID,
        include_out_of_stock: bool = True
    ) -> Optional[MachineInventoryResponse]:
        """Get full inventory for admin including all stock statuses"""
        try:
            # Check if machine exists
            machine = await self.machine_dao.get_by_id(session, machine_id)
            if not machine:
                return None
            
            # Get all inventory data (no stock status filter for admin)
            ingredient_data = await self.inventory_view_dao.get_machine_ingredient_inventory(
                session, machine_id, stock_status=None
            )
            addon_data = await self.inventory_view_dao.get_machine_addon_inventory(
                session, machine_id, stock_status=None
            )
            
            # Filter out out-of-stock items if not requested
            if not include_out_of_stock:
                ingredient_data = [item for item in ingredient_data if item.get('stock_status') != 'OUT_OF_STOCK']
                addon_data = [item for item in addon_data if item.get('stock_status') != 'OUT_OF_STOCK']
            
            # Transform ingredient data to MachineInventoryItemResponse
            ingredients = [
                MachineInventoryItemResponse(
                    id=item['ingredient_id'],
                    name=item['ingredient_name'],
                    item_type='ingredient',
                    emoji=item.get('ingredient_emoji'),
                    icon=None,
                    qty_available=item['qty_available_g'],
                    qty_available_unit='grams',
                    low_stock_threshold=item['low_stock_threshold_g'],
                    is_low_stock=item.get('stock_status') == 'LOW_STOCK',
                    is_available=item.get('stock_status') == 'AVAILABLE',
                    price_per_unit=item.get('price_per_gram'),
                    calories_per_unit=item.get('calories_per_g'),
                    min_qty=None,  # Not available in view
                    max_percent_limit=item.get('max_percent_limit')
                )
                for item in ingredient_data
            ]
            
            # Transform addon data to MachineInventoryItemResponse
            addons = [
                MachineInventoryItemResponse(
                    id=item['addon_id'],
                    name=item['addon_name'],
                    item_type='addon',
                    emoji=None,
                    icon=item.get('addon_icon'),
                    qty_available=item['qty_available'],
                    qty_available_unit='units',
                    low_stock_threshold=item['low_stock_threshold'],
                    is_low_stock=item.get('stock_status') == 'LOW_STOCK',
                    is_available=item.get('stock_status') == 'AVAILABLE',
                    price_per_unit=item.get('addon_price'),
                    calories_per_unit=item.get('addon_calories'),
                    min_qty=None,  # Not applicable for addons
                    max_percent_limit=None  # Not applicable for addons
                )
                for item in addon_data
            ]
            
            return MachineInventoryResponse(
                machine_id=machine_id,
                machine_location=machine.location,
                machine_status=machine.status,
                ingredients=ingredients,
                addons=addons,
                last_updated=machine.created_at  # Use created_at since updated_at may not exist
            )
        except Exception as e:
            logger.error(f"Error getting admin machine inventory: {e}")
            raise
    
    async def update_ingredient_stock(
        self,
        session: AsyncSession,
        machine_id: UUID,
        ingredient_id: UUID,
        qty_available_g: int,
        low_stock_threshold_g: int
    ) -> bool:
        """Update ingredient stock for a specific machine"""
        try:
            # Check if machine exists
            machine = await self.machine_dao.get_by_id(session, machine_id)
            if not machine:
                raise NotFoundError(f"Machine {machine_id} not found")
            
            # Update the machine ingredient stock
            success = await self.machine_dao.update_ingredient_stock(
                session,
                machine_id=machine_id,
                ingredient_id=ingredient_id,
                qty_available_g=qty_available_g,
                low_stock_threshold_g=low_stock_threshold_g
            )
            
            if not success:
                raise NotFoundError(f"Ingredient {ingredient_id} not found for machine {machine_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error updating ingredient stock: {e}")
            raise
    
    async def update_addon_stock(
        self,
        session: AsyncSession,
        machine_id: UUID,
        addon_id: UUID,
        qty_available: int,
        low_stock_threshold: int
    ) -> bool:
        """Update addon stock for a specific machine"""
        try:
            # Check if machine exists
            machine = await self.machine_dao.get_by_id(session, machine_id)
            if not machine:
                raise NotFoundError(f"Machine {machine_id} not found")
            
            # Update the machine addon stock
            success = await self.machine_dao.update_addon_stock(
                session,
                machine_id=machine_id,
                addon_id=addon_id,
                qty_available=qty_available,
                low_stock_threshold=low_stock_threshold
            )
            
            if not success:
                raise NotFoundError(f"Addon {addon_id} not found for machine {machine_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error updating addon stock: {e}")
            raise
    
    async def bulk_restock(
        self,
        session: AsyncSession,
        machine_id: UUID,
        restock_items: List[Any]
    ) -> Dict[str, Any]:
        """Perform bulk restock operation"""
        try:
            # Check if machine exists
            machine = await self.machine_dao.get_by_id(session, machine_id)
            if not machine:
                raise NotFoundError(f"Machine {machine_id} not found")
            
            results = {
                "successful_updates": 0,
                "failed_updates": 0,
                "failures": []
            }
            
            for item in restock_items:
                try:
                    item_id = item.item_id
                    item_type = item.item_type
                    qty_to_add = item.qty_to_add
                    
                    if item_type == "ingredient":
                        # Get current stock first
                        current_stock = await self.machine_dao.get_ingredient_stock(
                            session, machine_id, item_id
                        )
                        if current_stock:
                            new_qty = current_stock["qty_available_g"] + qty_to_add
                            success = await self.machine_dao.update_ingredient_stock(
                                session,
                                machine_id=machine_id,
                                ingredient_id=item_id,
                                qty_available_g=new_qty,
                                low_stock_threshold_g=current_stock["low_stock_threshold_g"]
                            )
                            if success:
                                results["successful_updates"] += 1
                            else:
                                results["failed_updates"] += 1
                                results["failures"].append({
                                    "item_id": item_id,
                                    "item_type": item_type,
                                    "reason": "Update failed"
                                })
                        else:
                            results["failed_updates"] += 1
                            results["failures"].append({
                                "item_id": item_id,
                                "item_type": item_type,
                                "reason": "Ingredient not found"
                            })
                    
                    elif item_type == "addon":
                        # Get current stock first
                        current_stock = await self.machine_dao.get_addon_stock(
                            session, machine_id, item_id
                        )
                        if current_stock:
                            new_qty = current_stock["qty_available"] + qty_to_add
                            success = await self.machine_dao.update_addon_stock(
                                session,
                                machine_id=machine_id,
                                addon_id=item_id,
                                qty_available=new_qty,
                                low_stock_threshold=current_stock["low_stock_threshold"]
                            )
                            if success:
                                results["successful_updates"] += 1
                            else:
                                results["failed_updates"] += 1
                                results["failures"].append({
                                    "item_id": item_id,
                                    "item_type": item_type,
                                    "reason": "Update failed"
                                })
                        else:
                            results["failed_updates"] += 1
                            results["failures"].append({
                                "item_id": item_id,
                                "item_type": item_type,
                                "reason": "Addon not found"
                            })
                    
                except Exception as item_error:
                    results["failed_updates"] += 1
                    results["failures"].append({
                        "item_id": getattr(item, 'item_id', None),
                        "item_type": getattr(item, 'item_type', None),
                        "reason": str(item_error)
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error performing bulk restock: {e}")
            raise
    
    async def update_stock_thresholds(
        self,
        session: AsyncSession,
        threshold_items: List[Any]
    ) -> Dict[str, Any]:
        """Update stock thresholds for multiple items"""
        try:
            results = {
                "successful_updates": 0,
                "failed_updates": 0,
                "failures": []
            }
            
            for item in threshold_items:
                try:
                    item_id = item.item_id
                    item_type = item.item_type
                    threshold = item.threshold
                    
                    if item_type == "ingredient":
                        # Check if ingredient exists in any machine
                        current_stock = await self.machine_dao.get_ingredient_stock_all_machines(
                            session, item_id
                        )
                        if current_stock:
                            success = await self.machine_dao.update_ingredient_thresholds(
                                session,
                                ingredient_id=item_id,
                                low_stock_threshold_g=threshold
                            )
                            if success:
                                results["successful_updates"] += 1
                            else:
                                results["failed_updates"] += 1
                                results["failures"].append({
                                    "item_id": item_id,
                                    "item_type": item_type,
                                    "reason": "Update failed"
                                })
                        else:
                            results["failed_updates"] += 1
                            results["failures"].append({
                                "item_id": item_id,
                                "item_type": item_type,
                                "reason": "Ingredient not found in any machine"
                            })
                    
                    elif item_type == "addon":
                        # Check if addon exists in any machine
                        current_stock = await self.machine_dao.get_addon_stock_all_machines(
                            session, item_id
                        )
                        if current_stock:
                            success = await self.machine_dao.update_addon_thresholds(
                                session,
                                addon_id=item_id,
                                low_stock_threshold=threshold
                            )
                            if success:
                                results["successful_updates"] += 1
                            else:
                                results["failed_updates"] += 1
                                results["failures"].append({
                                    "item_id": item_id,
                                    "item_type": item_type,
                                    "reason": "Update failed"
                                })
                        else:
                            results["failed_updates"] += 1
                            results["failures"].append({
                                "item_id": item_id,
                                "item_type": item_type,
                                "reason": "Addon not found in any machine"
                            })
                    
                except Exception as item_error:
                    results["failed_updates"] += 1
                    results["failures"].append({
                        "item_id": getattr(item, 'item_id', None),
                        "item_type": getattr(item, 'item_type', None),
                        "reason": str(item_error)
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error updating stock thresholds: {e}")
            raise
