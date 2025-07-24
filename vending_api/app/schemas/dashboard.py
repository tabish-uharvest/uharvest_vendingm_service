from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import uuid
from .common import BaseSchema


class DashboardMetrics(BaseSchema):
    """Overall system metrics"""
    total_machines: int
    active_machines: int
    total_orders_today: int
    total_revenue_today: Decimal
    total_orders_this_month: int
    total_revenue_this_month: Decimal
    avg_order_value: Decimal
    completion_rate: float
    low_stock_alerts: int
    out_of_stock_alerts: int


class MachineSummary(BaseSchema):
    """Machine summary for dashboard"""
    id: uuid.UUID
    location: str
    status: str
    orders_today: int
    revenue_today: Decimal
    low_stock_items: int
    last_order_time: Optional[datetime]


class DashboardResponse(BaseSchema):
    """Dashboard overview response"""
    metrics: DashboardMetrics
    machines: List[MachineSummary]
    recent_orders: List[Dict[str, Any]]
    top_selling_items: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SalesDataPoint(BaseSchema):
    """Sales data point for reports"""
    period: str  # Date/hour/week identifier
    orders_count: int
    revenue: Decimal
    avg_order_value: Decimal
    completion_rate: float


class SalesReportResponse(BaseSchema):
    """Sales report response"""
    start_date: date
    end_date: date
    machine_id: Optional[uuid.UUID]
    machine_location: Optional[str]
    total_orders: int
    total_revenue: Decimal
    avg_order_value: Decimal
    completion_rate: float
    data_points: List[SalesDataPoint]
    top_products: List[Dict[str, Any]]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class InventoryMovement(BaseSchema):
    """Inventory movement data"""
    item_id: uuid.UUID
    item_name: str
    item_type: str  # 'ingredient' or 'addon'
    machine_id: uuid.UUID
    machine_location: str
    starting_qty: int
    ending_qty: int
    consumed_qty: int
    restocked_qty: int
    waste_qty: int = 0


class InventoryReportResponse(BaseSchema):
    """Inventory movement report"""
    start_date: date
    end_date: date
    machine_id: Optional[uuid.UUID]
    movements: List[InventoryMovement]
    top_consumed_items: List[Dict[str, Any]]
    low_stock_items: List[Dict[str, Any]]
    restock_recommendations: List[Dict[str, Any]]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class MachinePerformanceMetrics(BaseSchema):
    """Machine performance metrics"""
    orders_count: int
    revenue: Decimal
    avg_order_value: Decimal
    uptime_percentage: float
    completion_rate: float
    customer_satisfaction: Optional[float]
    avg_preparation_time: Optional[float]


class MachinePerformanceResponse(BaseSchema):
    """Machine performance report"""
    machine_id: uuid.UUID
    machine_location: str
    period_start: date
    period_end: date
    metrics: MachinePerformanceMetrics
    daily_performance: List[Dict[str, Any]]
    top_selling_items: List[Dict[str, Any]]
    issues_log: List[Dict[str, Any]]


class TrendDataPoint(BaseSchema):
    """Trend analysis data point"""
    date: date
    value: Decimal
    change_percentage: Optional[float]


class AlertSummary(BaseSchema):
    """System alerts summary"""
    critical_alerts: int
    warning_alerts: int
    info_alerts: int
    total_alerts: int
    latest_alerts: List[Dict[str, Any]]


class RealtimeMetrics(BaseSchema):
    """Real-time system metrics"""
    active_orders: int
    machines_online: int
    current_revenue_today: Decimal
    orders_per_hour: float
    avg_response_time: float
    system_health: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)
