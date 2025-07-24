from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid
import logging

from app.config.database import get_async_db
from app.services.machine_service import MachineService
from app.services.enhanced_machine_service import EnhancedMachineService
from app.schemas.machine import (
    MachineCreate,
    MachineUpdate,
    MachineResponse,
    MachineStatusUpdate,
    ContainerUpdate,
    IngredientStockUpdate,
    AddonStockUpdate,
    BulkRestockRequest,
    LowStockAlert,
    MachineMetrics,
    MachineInventoryResponse,
    ThresholdUpdateRequest
)
from app.schemas.common import SuccessResponse, PaginatedResponse

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()
machine_service = MachineService()
enhanced_machine_service = EnhancedMachineService()


@router.get("/machines", response_model=List[MachineResponse])
async def list_machines(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_async_db)
):
    """List all vending machines with status and metrics"""
    try:
        machines = await machine_service.list_machines(
            session=db,
            skip=skip,
            limit=limit,
            status=status
        )
        return machines
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving machines: {str(e)}")


@router.post("/machines", response_model=MachineResponse, status_code=201)
async def create_machine(
    machine_data: MachineCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new vending machine"""
    try:
        machine = await machine_service.create_machine(
            session=db,
            machine_data=machine_data.model_dump()
        )
        await db.commit()  # Commit the transaction
        return machine
    except Exception as e:
        await db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail=f"Error creating machine: {str(e)}")


@router.put("/machines/{machine_id}", response_model=MachineResponse)
async def update_machine(
    machine_id: uuid.UUID,
    machine_data: MachineUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update machine details"""
    try:
        machine = await machine_service.update_machine(
            session=db,
            machine_id=machine_id,
            machine_data=machine_data.model_dump(exclude_unset=True)
        )
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        await db.commit()  # Commit the transaction
        return machine
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating machine: {str(e)}")


@router.delete("/machines/{machine_id}")
async def delete_machine(
    machine_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a vending machine"""
    try:
        deleted = await machine_service.delete_machine(db, machine_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Machine not found")
        await db.commit()  # Commit the transaction
        return {"message": "Machine deleted successfully"}
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting machine: {str(e)}")


@router.put("/machines/{machine_id}/status", response_model=MachineResponse)
async def update_machine_status(
    machine_id: uuid.UUID,
    status_update: MachineStatusUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Change machine status (active/maintenance/inactive)"""
    try:
        machine = await machine_service.update_machine(
            session=db,
            machine_id=machine_id,
            machine_data=status_update.model_dump()
        )
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        await db.commit()  # Commit the transaction
        return machine
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating machine status: {str(e)}")


@router.put("/machines/{machine_id}/containers", response_model=MachineResponse)
async def update_containers(
    machine_id: uuid.UUID,
    container_update: ContainerUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update cups/bowls quantity"""
    try:
        machine = await machine_service.update_machine(
            session=db,
            machine_id=machine_id,
            machine_data=container_update.model_dump(exclude_unset=True)
        )
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        await db.commit()  # Commit the transaction
        return machine
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating containers: {str(e)}")


@router.get("/machines/{machine_id}/inventory", response_model=MachineInventoryResponse)
async def get_machine_inventory_admin(
    machine_id: uuid.UUID,
    include_out_of_stock: bool = Query(True, description="Include out-of-stock items"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get full inventory with stock levels for admin"""
    try:
        inventory = await machine_service.get_full_inventory_admin(
            session=db,
            machine_id=machine_id,
            include_out_of_stock=include_out_of_stock
        )
        if not inventory:
            raise HTTPException(status_code=404, detail="Machine not found")
        return inventory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting machine inventory: {str(e)}")


@router.put("/machines/{machine_id}/ingredients/{ingredient_id}/stock", response_model=SuccessResponse)
async def update_ingredient_stock(
    machine_id: uuid.UUID,
    ingredient_id: uuid.UUID,
    stock_update: IngredientStockUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update ingredient stock"""
    try:
        success = await machine_service.update_ingredient_stock(
            session=db,
            machine_id=machine_id,
            ingredient_id=ingredient_id,
            qty_available_g=stock_update.qty_available_g,
            low_stock_threshold_g=stock_update.low_stock_threshold_g
        )
        if not success:
            raise HTTPException(status_code=404, detail="Ingredient not found for this machine")
        await db.commit()  # Commit the transaction
        return SuccessResponse(message="Ingredient stock updated successfully")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating ingredient stock: {str(e)}")


@router.put("/machines/{machine_id}/addons/{addon_id}/stock", response_model=SuccessResponse)
async def update_addon_stock(
    machine_id: uuid.UUID,
    addon_id: uuid.UUID,
    stock_update: AddonStockUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update addon stock"""
    try:
        success = await machine_service.update_addon_stock(
            session=db,
            machine_id=machine_id,
            addon_id=addon_id,
            qty_available=stock_update.qty_available,
            low_stock_threshold=stock_update.low_stock_threshold
        )
        if not success:
            raise HTTPException(status_code=404, detail="Addon not found for this machine")
        await db.commit()  # Commit the transaction
        return SuccessResponse(message="Addon stock updated successfully")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating addon stock: {str(e)}")


@router.post("/machines/{machine_id}/restock", response_model=SuccessResponse)
async def bulk_restock(
    machine_id: uuid.UUID,
    restock_request: BulkRestockRequest = Body(
        ...,
        example={
            "items": [
                {
                    "item_id": "3a0b1590-8601-4925-bb00-21f1fb24bfc5",
                    "item_type": "ingredient",
                    "qty_to_add": 500
                },
                {
                    "item_id": "7b1c2591-9712-5a36-cc11-32g2gc35cgd6",
                    "item_type": "addon",
                    "qty_to_add": 100
                }
            ]
        }
    ),
    db: AsyncSession = Depends(get_async_db)
):
    """Bulk restock operation"""
    try:
        results = await machine_service.bulk_restock(
            session=db,
            machine_id=machine_id,
            restock_items=restock_request.items
        )
        await db.commit()  # Commit the transaction
        
        # Create detailed response message
        message = f"Bulk restock completed. {results['successful_updates']} items updated, {results['failed_updates']} failed."
        if results['failures']:
            message += f" Failures: {results['failures']}"
            
        return SuccessResponse(message=message)
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error during bulk restock: {str(e)}")


@router.get("/inventory/alerts", response_model=List[LowStockAlert])
async def get_low_stock_alerts(
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get low stock and out-of-stock alerts"""
    try:
        # Use the machine DAO directly since it returns the correct format
        from app.dao.machine_dao import MachineDAO
        machine_dao = MachineDAO()
        
        alerts = await machine_dao.get_low_stock_alerts(
            session=db,
            machine_id=machine_id
        )
        
        # Filter by priority if specified
        if priority:
            alerts = [alert for alert in alerts if alert.get('priority') == priority]
        
        # Apply pagination
        total_alerts = len(alerts)
        alerts = alerts[skip:skip + limit]
        
        # The machine DAO already returns the correct format
        return alerts
        
    except Exception as e:
        logger.error(f"Error getting low stock alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")


@router.put("/inventory/thresholds", response_model=SuccessResponse)
async def update_stock_thresholds(
    threshold_request: ThresholdUpdateRequest = Body(
        ...,
        example={
            "items": [
                {
                    "item_id": "3a0b1590-8601-4925-bb00-21f1fb24bfc5",
                    "item_type": "ingredient",
                    "threshold": 400
                }
            ]
        }
    ),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update low stock thresholds for multiple items
    
    Request body should be an object with an 'items' array:
    ```json
    {
        "items": [
            {
                "item_id": "3a0b1590-8601-4925-bb00-21f1fb24bfc5",
                "item_type": "ingredient",
                "threshold": 400
            }
        ]
    }
    ```
    """
    try:
        results = await machine_service.update_stock_thresholds(
            session=db,
            threshold_items=threshold_request.items
        )
        await db.commit()  # Commit the transaction
        
        # Create detailed response message
        message = f"Threshold update completed. {results['successful_updates']} items updated, {results['failed_updates']} failed."
        if results['failures']:
            message += f" Failures: {results['failures']}"
            
        return SuccessResponse(message=message)
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating thresholds: {str(e)}")
