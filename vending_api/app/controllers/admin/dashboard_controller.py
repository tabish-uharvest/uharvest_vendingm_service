from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import uuid

from app.config.database import get_async_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import (
    DashboardResponse,
    SalesReportResponse,
    InventoryReportResponse,
    MachinePerformanceResponse
)
from app.schemas.common import SuccessResponse

router = APIRouter()
dashboard_service = DashboardService()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_async_db)
):
    """Overall system metrics and KPIs"""
    try:
        dashboard_data = await dashboard_service.get_dashboard_overview(db)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/sales", response_model=SalesReportResponse)
async def get_sales_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine"),
    group_by: str = Query("day", description="Group by: hour, day, week, month"),
    db: AsyncSession = Depends(get_async_db)
):
    """Sales reports by date range"""
    try:
        report = await dashboard_service.generate_sales_report(
            session=db,
            start_date=start_date,
            end_date=end_date,
            machine_id=machine_id,
            group_by=group_by
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/inventory", response_model=InventoryReportResponse)
async def get_inventory_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine"),
    item_type: Optional[str] = Query(None, description="Filter by type: ingredient, addon"),
    db: AsyncSession = Depends(get_async_db)
):
    """Inventory movement reports"""
    try:
        report = await dashboard_service.generate_inventory_report(
            session=db,
            start_date=start_date,
            end_date=end_date,
            machine_id=machine_id,
            item_type=item_type
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/machine-performance", response_model=List[MachinePerformanceResponse])
async def get_machine_performance_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by specific machine"),
    db: AsyncSession = Depends(get_async_db)
):
    """Machine performance analytics"""
    try:
        report = await dashboard_service.generate_machine_performance_report(
            session=db,
            start_date=start_date,
            end_date=end_date,
            machine_id=machine_id
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/real-time")
async def get_real_time_analytics(
    db: AsyncSession = Depends(get_async_db)
):
    """Real-time system analytics"""
    try:
        analytics = await dashboard_service.get_real_time_analytics(db)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/trends")
async def get_trend_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days for trend analysis"),
    metric: str = Query("revenue", description="Metric to analyze: revenue, orders, popular_items"),
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine"),
    db: AsyncSession = Depends(get_async_db)
):
    """Trend analytics for specified metrics"""
    try:
        trends = await dashboard_service.get_trend_analytics(
            session=db,
            days=days,
            metric=metric,
            machine_id=machine_id
        )
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/summary")
async def get_alerts_summary(
    db: AsyncSession = Depends(get_async_db)
):
    """Summary of all system alerts"""
    try:
        alerts = await dashboard_service.get_alerts_summary(db)
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
