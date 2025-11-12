from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid
from .common import BaseSchema


class OrderItemRequest(BaseSchema):
    """Schema for order item in request"""
    ingredient_id: uuid.UUID = Field(..., description="Ingredient ID")
    grams_used: int = Field(..., gt=0, le=1000, description="Grams to use")
    calories: int = Field(..., ge=0, description="Calories for this ingredient (calculated by UI)")


class OrderAddonRequest(BaseSchema):
    """Schema for order addon in request"""
    addon_id: uuid.UUID = Field(..., description="Addon ID")
    qty: int = Field(1, gt=0, le=10, description="Quantity")
    calories: int = Field(..., ge=0, description="Calories for this addon (calculated by UI)")


class OrderCreateRequest(BaseSchema):
    """Schema for creating a new order"""
    machine_id: uuid.UUID = Field(..., description="Vending machine ID")
    total_price: Decimal = Field(..., gt=0, description="Total price calculated by UI")
    total_calories: int = Field(..., ge=0, description="Total calories calculated by UI")
    status: str = Field("processing", description="Order status")
    session_id: Optional[str] = Field(None, description="Session ID from UI")
    ingredients: List[OrderItemRequest] = Field(..., min_items=1, max_items=20, description="Order ingredients")
    addons: List[OrderAddonRequest] = Field([], max_items=10, description="Order addons")
    liquids: List[Dict[str, Any]] = Field([], description="Liquids for dynamic order string (not saved to DB)")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class OrderStatusUpdate(BaseSchema):
    """Schema for updating order status"""
    status: str = Field(..., description="New order status")
    payment_status: Optional[str] = Field(None, description="Payment status (accepted but not stored)")
    notes: Optional[str] = Field(None, max_length=500, description="Status update notes (accepted but not stored)")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    @validator('payment_status')
    def validate_payment_status(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'paid', 'failed', 'refunded']
            if v not in allowed_statuses:
                raise ValueError(f'Payment status must be one of: {", ".join(allowed_statuses)}')
        return v


class OrderItemResponse(BaseSchema):
    """Schema for order item in response"""
    id: uuid.UUID
    ingredient_id: Optional[uuid.UUID]
    ingredient_name: Optional[str]
    ingredient_emoji: Optional[str]
    qty_ml: int = Field(default=0, description="Quantity in ml")
    grams_used: int
    calories: int


class OrderAddonResponse(BaseSchema):
    """Schema for order addon in response"""
    id: uuid.UUID
    addon_id: Optional[uuid.UUID]
    addon_name: Optional[str]
    addon_icon: Optional[str]
    qty: int
    calories: int


class OrderResponse(BaseSchema):
    """Schema for order response"""
    id: uuid.UUID
    machine_id: Optional[uuid.UUID]
    machine_location: Optional[str]
    user_id: Optional[uuid.UUID]
    session_id: Optional[str]
    status: str
    total_price: Decimal
    total_calories: int
    created_at: datetime
    # Note: updated_at field removed as it doesn't exist in the database schema
    items: List[OrderItemResponse]
    addons: List[OrderAddonResponse]
    order_string: Optional[str] = Field(None, description="Formatted order details string")


class OrderDetailResponse(OrderResponse):
    """Extended order response with additional details for admin views"""
    preparation_time: Optional[int] = Field(None, description="Preparation time in seconds")
    completion_time: Optional[datetime] = Field(None, description="When the order was completed")
    customer_feedback: Optional[str] = Field(None, description="Customer feedback")
    refund_amount: Optional[Decimal] = Field(None, description="Refund amount if applicable")
    staff_notes: Optional[str] = Field(None, description="Internal staff notes")
    
    # Additional machine details
    machine_status_at_order: Optional[str] = Field(None, description="Machine status when order was placed")
    
    # Enhanced ingredient details with nutritional info
    total_protein: Optional[Decimal] = Field(None, description="Total protein content")
    total_fiber: Optional[Decimal] = Field(None, description="Total fiber content")
    total_sugar: Optional[Decimal] = Field(None, description="Total sugar content")
    
    # Order flow tracking
    status_history: Optional[List[Dict[str, Any]]] = Field(None, description="Status change history")


class OrderListResponse(BaseSchema):
    """Schema for order list item (lighter than full response)"""
    id: uuid.UUID
    machine_id: Optional[uuid.UUID]
    machine_location: Optional[str]
    user_id: Optional[uuid.UUID]
    session_id: Optional[str]
    status: str
    total_price: Decimal
    total_calories: int
    created_at: datetime
    items_count: int
    addons_count: int


class OrderStatsResponse(BaseSchema):
    """Schema for order statistics"""
    total_orders: int
    completed_orders: int
    cancelled_orders: int
    failed_orders: int
    pending_orders: int
    processing_orders: int
    total_revenue: Decimal
    avg_order_value: Decimal
    avg_calories: Decimal
    completion_rate: float = Field(..., description="Percentage of completed orders")
    
    @validator('completion_rate', pre=True, always=True)
    def calculate_completion_rate(cls, v, values):
        total = values.get('total_orders', 0)
        completed = values.get('completed_orders', 0)
        return round((completed / total * 100) if total > 0 else 0, 2)


class PopularItemResponse(BaseSchema):
    """Schema for popular item"""
    id: uuid.UUID
    name: str
    emoji: Optional[str] = None
    icon: Optional[str] = None
    order_count: int
    total_quantity: int
    total_revenue: Decimal


class PopularItemsResponse(BaseSchema):
    """Schema for popular items response"""
    ingredients: List[PopularItemResponse]
    addons: List[PopularItemResponse]


class OrderFilters(BaseSchema):
    """Schema for order filtering"""
    machine_id: Optional[uuid.UUID] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    user_id: Optional[uuid.UUID] = None
    payment_status: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    @validator('payment_status')
    def validate_payment_status(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'paid', 'failed', 'refunded']
            if v not in allowed_statuses:
                raise ValueError(f'Payment status must be one of: {", ".join(allowed_statuses)}')
        return v
