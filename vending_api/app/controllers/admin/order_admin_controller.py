from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, date
import uuid

from app.config.database import get_async_db
from app.services.order_service import OrderService
from app.schemas.order import (
    OrderResponse,
    OrderDetailResponse,
    OrderStatusUpdate,
    OrderStatsResponse,
    OrderFilters
)
from app.schemas.common import SuccessResponse, PaginatedResponse

router = APIRouter()
order_service = OrderService()


@router.get("/orders", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user"),
    db: AsyncSession = Depends(get_async_db)
):
    """List orders with filters (date, machine, status)"""
    try:
        filters = OrderFilters(
            machine_id=machine_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )
        
        result = await order_service.list_orders_admin(
            session=db,
            filters=filters,
            skip=skip,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/{order_id}", response_model=OrderDetailResponse)
async def get_order_details(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed order information"""
    try:
        order = await order_service.get_order_details_admin(
            session=db,
            order_id=order_id
        )
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/orders/{order_id}/status")
async def update_order_status_admin(
    order_id: uuid.UUID,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Admin order status updates"""
    try:
        result = await order_service.update_order_status_admin(
            session=db,
            order_id=order_id,
            status_update=status_update
        )
        if not result:
            raise HTTPException(status_code=404, detail="Order not found")
        return SuccessResponse(
            message=f"Order status updated to {status_update.status}",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/stats", response_model=OrderStatsResponse)
async def get_order_statistics(
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine"),
    start_date: Optional[date] = Query(None, description="Statistics from date"),
    end_date: Optional[date] = Query(None, description="Statistics to date"),
    db: AsyncSession = Depends(get_async_db)
):
    """Order statistics and metrics"""
    try:
        stats = await order_service.get_order_statistics(
            session=db,
            machine_id=machine_id,
            start_date=start_date,
            end_date=end_date
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/popular-items")
async def get_popular_items(
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine"),
    start_date: Optional[date] = Query(None, description="From date"),
    end_date: Optional[date] = Query(None, description="To date"),
    limit: int = Query(10, ge=1, le=50, description="Number of items to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get popular items ordered"""
    try:
        popular_items = await order_service.get_popular_items(
            session=db,
            machine_id=machine_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return {"popular_items": popular_items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/revenue")
async def get_revenue_analytics(
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine"),
    start_date: Optional[date] = Query(None, description="From date"),
    end_date: Optional[date] = Query(None, description="To date"),
    group_by: str = Query("day", description="Group by: hour, day, week, month"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get revenue analytics"""
    try:
        revenue_data = await order_service.get_revenue_analytics(
            session=db,
            machine_id=machine_id,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )
        return {"revenue_analytics": revenue_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
