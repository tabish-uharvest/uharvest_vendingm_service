from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid
from datetime import datetime

from app.config.database import get_async_db
from app.services.order_service import OrderService
from app.services.machine_registration_service import get_current_machine_id, MachineRegistrationService
from app.schemas.order import (
    OrderCreateRequest, 
    OrderResponse, 
    OrderStatusUpdate,
    OrderStatsResponse,
    PopularItemsResponse,
    OrderFilters
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.utils.exceptions import NotFoundError

router = APIRouter()
order_service = OrderService()
machine_registration_service = MachineRegistrationService()


@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    order_request: OrderCreateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new order
    All data including calories and session_id comes from UI
    """
    try:
        # Validate machine ID exists or auto-register
        machine_valid = await machine_registration_service.validate_or_register_machine(
            session=db,
            machine_id=order_request.machine_id
        )
        
        if not machine_valid:
            raise HTTPException(
                status_code=404, 
                detail=f"Machine {order_request.machine_id} not found and auto-registration is disabled"
            )
        
        return await order_service.create_order(
            order_request=order_request,
            session_id=order_request.session_id,  # From request body now
            user_id=None  # For now, we're not handling user authentication
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/machine/orders", response_model=OrderResponse, status_code=201)
async def create_order_for_current_machine(
    order_request: OrderCreateRequest,
    session_id: Optional[str] = Query(None, description="Customer session ID"),
    db: AsyncSession = Depends(get_async_db),
    current_machine_id: Optional[uuid.UUID] = Depends(get_current_machine_id)
):
    """
    Create a new order for the current machine
    (single-machine deployment mode)
    Machine ID is automatically resolved from configuration
    """
    if not current_machine_id:
        raise HTTPException(
            status_code=400, 
            detail="No machine configured. Use /orders for multi-machine mode with machine_id in request"
        )
    
    # Override machine_id in request with current machine
    order_request.machine_id = current_machine_id
    
    try:
        return await order_service.create_order(
            order_request=order_request,
            session_id=session_id,
            user_id=None
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/orders/stats", response_model=OrderStatsResponse)
async def get_order_statistics(
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get order statistics"""
    stats = await order_service.get_order_statistics(db, machine_id, date_from, date_to)
    return OrderStatsResponse(**stats)


@router.get("/orders/popular-items", response_model=PopularItemsResponse)
async def get_popular_items(
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    limit: int = Query(10, ge=1, le=50, description="Items limit"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get most popular ingredients and addons"""
    items = await order_service.get_popular_items(db, machine_id, date_from, date_to, limit)
    return PopularItemsResponse(**items)


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get order by ID"""
    order = await order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: uuid.UUID,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update order status (for machine updates)"""
    try:
        order = await order_service.update_order_status(db, order_id, status_update)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        await db.commit()  # Commit the transaction
        return order
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating order status: {str(e)}")


@router.get("/machines/{machine_id}/orders", response_model=List[OrderResponse])
async def get_machine_orders(
    machine_id: uuid.UUID,
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get orders for a specific machine"""
    return await order_service.get_orders_by_machine(
        db, machine_id, status, date_from, date_to, skip, limit
    )


@router.get("/machine/orders", response_model=List[OrderResponse])
async def get_current_machine_orders(
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_async_db),
    current_machine_id: Optional[uuid.UUID] = Depends(get_current_machine_id)
):
    """
    Get orders for the current machine
    (single-machine deployment mode)
    """
    if not current_machine_id:
        raise HTTPException(
            status_code=400, 
            detail="No machine configured. Use /machines/{machine_id}/orders for multi-machine mode"
        )
    
    return await order_service.get_orders_by_machine(
        db, current_machine_id, status, date_from, date_to, skip, limit
    )


@router.get("/orders/{order_id}/summary", response_model=dict)
async def get_order_summary_string(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get formatted order summary string
    Returns container type, items, and quantities in readable format
    """
    try:
        order_string = await order_service.get_order_string(db, order_id)
        return {
            "order_id": order_id,
            "order_string": order_string,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
