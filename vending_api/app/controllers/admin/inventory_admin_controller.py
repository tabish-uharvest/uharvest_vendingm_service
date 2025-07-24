from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid

from app.config.database import get_async_db
from app.services.inventory_service import InventoryService
from app.schemas.machine import (
    IngredientStockUpdate,
    AddonStockUpdate,
    BulkRestockRequest,
    LowStockAlert,
    ThresholdUpdate
)
from app.schemas.common import SuccessResponse, PaginatedResponse

router = APIRouter()
inventory_service = InventoryService()


@router.get("/machines/{machine_id}/inventory")
async def get_machine_inventory_admin(
    machine_id: uuid.UUID,
    include_out_of_stock: bool = Query(False, description="Include out of stock items"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get full inventory with stock levels for admin"""
    try:
        inventory = await inventory_service.get_machine_inventory_admin(
            session=db,
            machine_id=machine_id,
            include_out_of_stock=include_out_of_stock
        )
        return inventory
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/machines/{machine_id}/ingredients/{ingredient_id}/stock")
async def update_ingredient_stock(
    machine_id: uuid.UUID,
    ingredient_id: uuid.UUID,
    stock_update: IngredientStockUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update ingredient stock for a specific machine"""
    try:
        result = await inventory_service.update_ingredient_stock(
            session=db,
            machine_id=machine_id,
            ingredient_id=ingredient_id,
            stock_update=stock_update
        )
        return SuccessResponse(message="Ingredient stock updated successfully", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/machines/{machine_id}/addons/{addon_id}/stock")
async def update_addon_stock(
    machine_id: uuid.UUID,
    addon_id: uuid.UUID,
    stock_update: AddonStockUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update addon stock for a specific machine"""
    try:
        result = await inventory_service.update_addon_stock(
            session=db,
            machine_id=machine_id,
            addon_id=addon_id,
            stock_update=stock_update
        )
        return SuccessResponse(message="Addon stock updated successfully", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/machines/{machine_id}/restock")
async def bulk_restock(
    machine_id: uuid.UUID,
    restock_request: BulkRestockRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Bulk restock operation for a machine"""
    try:
        result = await inventory_service.bulk_restock(
            session=db,
            machine_id=machine_id,
            restock_request=restock_request
        )
        return SuccessResponse(message="Bulk restock completed successfully", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/alerts", response_model=List[LowStockAlert])
async def get_low_stock_alerts(
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine"),
    severity: Optional[str] = Query(None, description="Filter by severity (low/out)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_async_db)
):
    """Get low stock and out-of-stock alerts"""
    try:
        alerts = await inventory_service.get_low_stock_alerts(
            session=db,
            machine_id=machine_id,
            severity=severity,
            skip=skip,
            limit=limit
        )
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/inventory/thresholds")
async def update_stock_thresholds(
    threshold_updates: List[ThresholdUpdate],
    db: AsyncSession = Depends(get_async_db)
):
    """Update low stock thresholds for multiple items"""
    try:
        result = await inventory_service.update_stock_thresholds(
            session=db,
            threshold_updates=threshold_updates
        )
        return SuccessResponse(
            message=f"Updated {result['updated_count']} stock thresholds",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
