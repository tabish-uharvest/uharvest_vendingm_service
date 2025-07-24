from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid

from app.config.database import get_async_db
from app.services.machine_service import MachineService
from app.services.machine_registration_service import get_current_machine_id, MachineRegistrationService
from app.schemas.machine import (
    MachineInventoryResponse,
    MachineResponse,
    MachineMetrics,
    LowStockAlert,
    MachineAddonsResponse
)
from app.schemas.common import SuccessResponse

router = APIRouter()
machine_service = MachineService()
machine_registration_service = MachineRegistrationService()


@router.get("/machines/{machine_id}/inventory", response_model=MachineInventoryResponse)
async def get_machine_inventory(
    machine_id: uuid.UUID = Path(..., description="Machine ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get available ingredients and addons for a specific machine"""
    # Validate machine ID exists or auto-register
    machine_valid = await machine_registration_service.validate_or_register_machine(
        session=db,
        machine_id=machine_id
    )
    
    if not machine_valid:
        raise HTTPException(
            status_code=404, 
            detail=f"Machine {machine_id} not found and auto-registration is disabled"
        )
    
    inventory = await machine_service.get_available_inventory(db, machine_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Machine not found")
    return inventory


@router.get("/machine/inventory", response_model=MachineInventoryResponse)
async def get_current_machine_inventory(
    db: AsyncSession = Depends(get_async_db),
    current_machine_id: Optional[uuid.UUID] = Depends(get_current_machine_id)
):
    """
    Get available ingredients and addons for the current machine
    (single-machine deployment mode)
    """
    if not current_machine_id:
        raise HTTPException(
            status_code=400, 
            detail="No machine configured. Use /machines/{machine_id}/inventory for multi-machine mode"
        )
    
    inventory = await machine_service.get_available_inventory(db, current_machine_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Machine not found")
    return inventory


@router.get("/machines/{machine_id}/presets")
async def get_machine_presets(
    machine_id: uuid.UUID = Path(..., description="Machine ID"),
    category: Optional[str] = Query(None, description="Filter by category (smoothie/salad)"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get available preset recipes for a specific machine"""
    # Validate machine ID exists or auto-register
    machine_valid = await machine_registration_service.validate_or_register_machine(
        session=db,
        machine_id=machine_id
    )
    
    if not machine_valid:
        raise HTTPException(
            status_code=404, 
            detail=f"Machine {machine_id} not found and auto-registration is disabled"
        )
    
    presets = await machine_service.get_available_presets(db, machine_id, category)
    return {"presets": presets}


@router.get("/machine/presets")
async def get_current_machine_presets(
    category: Optional[str] = Query(None, description="Filter by category (smoothie/salad)"),
    db: AsyncSession = Depends(get_async_db),
    current_machine_id: Optional[uuid.UUID] = Depends(get_current_machine_id)
):
    """
    Get available preset recipes for the current machine
    (single-machine deployment mode)
    """
    if not current_machine_id:
        raise HTTPException(
            status_code=400, 
            detail="No machine configured. Use /machines/{machine_id}/presets for multi-machine mode"
        )
    
    presets = await machine_service.get_available_presets(db, current_machine_id, category)
    return {"presets": presets}


@router.get("/machines/{machine_id}/status")
async def get_machine_status(
    machine_id: uuid.UUID = Path(..., description="Machine ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get machine status and availability"""
    status = await machine_service.get_machine_status(db, machine_id)
    if not status:
        raise HTTPException(status_code=404, detail="Machine not found")
    return status


@router.get("/machine/status")
async def get_current_machine_status(
    db: AsyncSession = Depends(get_async_db),
    current_machine_id: Optional[uuid.UUID] = Depends(get_current_machine_id)
):
    """
    Get current machine status and availability
    (single-machine deployment mode)
    """
    if not current_machine_id:
        raise HTTPException(
            status_code=400, 
            detail="No machine configured. Use /machines/{machine_id}/status for multi-machine mode"
        )
    
    status = await machine_service.get_machine_status(db, current_machine_id)
    if not status:
        raise HTTPException(status_code=404, detail="Machine not found")
    return status


@router.get("/machines/{machine_id}/metrics", response_model=MachineMetrics)
async def get_machine_metrics(
    machine_id: uuid.UUID = Path(..., description="Machine ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get machine performance metrics"""
    metrics = await machine_service.get_machine_metrics(db, machine_id)
    return MachineMetrics(**metrics)


@router.get("/machine/info")
async def get_current_machine_info(
    db: AsyncSession = Depends(get_async_db),
    current_machine_id: Optional[uuid.UUID] = Depends(get_current_machine_id)
):
    """
    Get current machine information and configuration
    Useful for frontend to know which machine it's connected to
    """
    from app.config.machine_config import machine_settings
    
    response = {
        "deployment_mode": "multi-machine" if machine_settings.multi_machine_mode else "single-machine",
        "machine_id": current_machine_id,
        "auto_register": machine_settings.auto_register_machine,
        "configured_location": machine_settings.machine_location
    }
    
    if current_machine_id:
        machine_status = await machine_service.get_machine_status(db, current_machine_id)
        if machine_status:
            response.update({
                "machine_details": machine_status
            })
    
    return response


@router.get("/machines/{machine_id}/addons", response_model=MachineAddonsResponse)
async def get_machine_addons(
    machine_id: uuid.UUID = Path(..., description="Machine ID"),
    stock_status: Optional[str] = Query(None, description="Filter by stock status (AVAILABLE, LOW_STOCK, OUT_OF_STOCK)"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get addon inventory for a specific machine using v_machine_addon_inventory view"""
    # Validate machine ID exists or auto-register
    machine_valid = await machine_registration_service.validate_or_register_machine(
        session=db,
        machine_id=machine_id
    )
    
    if not machine_valid:
        raise HTTPException(
            status_code=404, 
            detail=f"Machine {machine_id} not found and auto-registration is disabled"
        )
    
    addons = await machine_service.get_machine_addons(db, machine_id, stock_status)
    if not addons:
        raise HTTPException(status_code=404, detail="Machine not found")
    return addons


@router.get("/machine/addons", response_model=MachineAddonsResponse)
async def get_current_machine_addons(
    stock_status: Optional[str] = Query(None, description="Filter by stock status (AVAILABLE, LOW_STOCK, OUT_OF_STOCK)"),
    db: AsyncSession = Depends(get_async_db),
    current_machine_id: Optional[uuid.UUID] = Depends(get_current_machine_id)
):
    """
    Get addon inventory for the current machine using v_machine_addon_inventory view
    (single-machine deployment mode)
    """
    if not current_machine_id:
        raise HTTPException(
            status_code=400, 
            detail="No machine configured. Use /machines/{machine_id}/addons for multi-machine mode"
        )
    
    addons = await machine_service.get_machine_addons(db, current_machine_id, stock_status)
    if not addons:
        raise HTTPException(status_code=404, detail="Machine not found")
    return addons
