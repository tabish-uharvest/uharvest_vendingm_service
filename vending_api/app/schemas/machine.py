from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid
from .common import BaseSchema


class MachineBase(BaseSchema):
    """Base machine schema"""
    location: str = Field(..., min_length=1, max_length=500, description="Machine location", example="Building A - Floor 1 - Cafeteria")
    status: str = Field("active", description="Machine status", example="active")
    cups_qty: int = Field(0, ge=0, description="Available cups quantity", example=100)
    bowls_qty: int = Field(0, ge=0, description="Available bowls quantity", example=50)
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['active', 'maintenance', 'inactive']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class MachineCreate(MachineBase):
    """Schema for creating a new machine"""
    
    class Config:
        schema_extra = {
            "example": {
                "location": "Building A - Floor 1 - Cafeteria",
                "status": "active",
                "cups_qty": 100,
                "bowls_qty": 50
            }
        }


class MachineUpdate(BaseSchema):
    """Schema for updating machine details"""
    location: Optional[str] = Field(None, min_length=1, max_length=500, example="Building B - Floor 2 - Break Room")
    status: Optional[str] = Field(None, example="maintenance")
    cups_qty: Optional[int] = Field(None, ge=0, example=75)
    bowls_qty: Optional[int] = Field(None, ge=0, example=25)
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['active', 'maintenance', 'inactive']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "location": "Building B - Floor 2 - Break Room",
                "status": "maintenance",
                "cups_qty": 75,
                "bowls_qty": 25
            }
        }


class MachineStatusUpdate(BaseSchema):
    """Schema for updating machine status"""
    status: str = Field(..., description="New machine status", example="active")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['active', 'maintenance', 'inactive']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class ContainerUpdate(BaseSchema):
    """Schema for updating container quantities"""
    cups_qty: Optional[int] = Field(None, ge=0, description="Cups quantity")
    bowls_qty: Optional[int] = Field(None, ge=0, description="Bowls quantity")


class MachineResponse(MachineBase):
    """Schema for machine response"""
    id: uuid.UUID
    created_at: datetime
    # Note: updated_at field removed as it doesn't exist in the database schema


class MachineInventoryItemResponse(BaseSchema):
    """Schema for inventory item in machine"""
    id: uuid.UUID
    name: str
    item_type: str  # 'ingredient' or 'addon'
    emoji: Optional[str] = None
    icon: Optional[str] = None
    qty_available: int
    qty_available_unit: str  # 'grams' or 'units'
    low_stock_threshold: int
    is_low_stock: bool
    is_available: bool
    price_per_unit: Optional[Decimal] = None
    calories_per_unit: Optional[Decimal] = None
    min_qty: Optional[int] = None
    max_percent_limit: Optional[int] = None


class MachineInventoryResponse(BaseSchema):
    """Schema for complete machine inventory"""
    machine_id: uuid.UUID
    machine_location: str
    machine_status: str
    ingredients: List[MachineInventoryItemResponse]
    addons: List[MachineInventoryItemResponse]
    last_updated: datetime


class IngredientStockUpdate(BaseSchema):
    """Schema for updating ingredient stock"""
    qty_available_g: int = Field(..., ge=0, description="Available quantity in grams", example=1000)
    low_stock_threshold_g: Optional[int] = Field(None, ge=0, description="Low stock threshold in grams", example=200)

    class Config:
        schema_extra = {
            "example": {
                "qty_available_g": 1000,
                "low_stock_threshold_g": 200
            }
        }


class AddonStockUpdate(BaseSchema):
    """Schema for updating addon stock"""
    qty_available: int = Field(..., ge=0, description="Available quantity in units", example=50)
    low_stock_threshold: Optional[int] = Field(None, ge=0, description="Low stock threshold in units", example=10)

    class Config:
        schema_extra = {
            "example": {
                "qty_available": 50,
                "low_stock_threshold": 10
            }
        }


class BulkRestockItem(BaseSchema):
    """Schema for bulk restock item"""
    item_id: uuid.UUID = Field(..., description="Ingredient or addon ID", example="3a0b1590-8601-4925-bb00-21f1fb24bfc5")
    item_type: str = Field(..., description="Type: 'ingredient' or 'addon'", example="ingredient")
    qty_to_add: int = Field(..., gt=0, description="Quantity to add", example=500)
    
    @validator('item_type')
    def validate_item_type(cls, v):
        if v not in ['ingredient', 'addon']:
            raise ValueError('Item type must be "ingredient" or "addon"')
        return v

    class Config:
        schema_extra = {
            "example": {
                "item_id": "3a0b1590-8601-4925-bb00-21f1fb24bfc5",
                "item_type": "ingredient",
                "qty_to_add": 500
            }
        }


class BulkRestockRequest(BaseSchema):
    """Schema for bulk restock operation"""
    items: List[BulkRestockItem] = Field(..., min_items=1, max_items=50, description="Items to restock")

    class Config:
        schema_extra = {
            "example": {
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
        }


class LowStockAlert(BaseSchema):
    """Schema for low stock alert"""
    machine_id: uuid.UUID
    machine_location: str
    item_id: uuid.UUID
    item_name: str
    item_type: str
    current_qty: int
    threshold: int
    percentage_remaining: float
    priority: str  # 'critical', 'warning', 'info'
    last_updated: datetime


class MachineMetrics(BaseSchema):
    """Schema for machine performance metrics"""
    machine_id: uuid.UUID
    machine_location: str
    orders_today: int
    orders_this_week: int
    orders_this_month: int
    revenue_today: Decimal
    revenue_this_week: Decimal
    revenue_this_month: Decimal
    avg_order_value: Decimal
    most_popular_items: List[str]
    inventory_alerts_count: int
    uptime_percentage: float


class ThresholdUpdate(BaseSchema):
    """Schema for updating stock thresholds"""
    item_id: uuid.UUID = Field(..., description="Ingredient or addon ID")
    item_type: str = Field(..., description="Type: 'ingredient' or 'addon'")
    threshold: int = Field(..., ge=0, description="New threshold value")
    
    @validator('item_type')
    def validate_item_type(cls, v):
        if v not in ['ingredient', 'addon']:
            raise ValueError('Item type must be "ingredient" or "addon"')
        return v


class MachineAddonResponse(BaseSchema):
    """Schema for machine addon inventory item"""
    machine_id: uuid.UUID
    machine_location: str
    machine_status: str
    addon_id: uuid.UUID
    addon_name: str
    addon_icon: Optional[str]
    addon_price: Decimal
    addon_calories: int
    qty_available: int
    low_stock_threshold: int
    stock_status: str
    stock_percentage: Decimal
    inventory_updated_at: Optional[datetime]


class MachineAddonsResponse(BaseSchema):
    """Schema for machine addons inventory"""
    machine_id: uuid.UUID
    machine_location: str
    machine_status: str
    addons: List[MachineAddonResponse]
    total_addons: int
    available_addons: int
    low_stock_addons: int
    out_of_stock_addons: int


class ThresholdUpdateItem(BaseSchema):
    """Schema for threshold update item"""
    item_id: uuid.UUID = Field(
        ..., 
        description="Ingredient or addon ID", 
        example="3a0b1590-8601-4925-bb00-21f1fb24bfc5"
    )
    item_type: str = Field(
        ..., 
        description="Type: 'ingredient' or 'addon'", 
        example="ingredient"
    )
    threshold: int = Field(
        ..., 
        gt=0, 
        description="New low stock threshold", 
        example=400
    )
    
    @validator('item_type')
    def validate_item_type(cls, v):
        if v not in ['ingredient', 'addon']:
            raise ValueError('Item type must be "ingredient" or "addon"')
        return v

    class Config:
        schema_extra = {
            "example": {
                "item_id": "3a0b1590-8601-4925-bb00-21f1fb24bfc5",
                "item_type": "ingredient",
                "threshold": 400
            }
        }


class ThresholdUpdateRequest(BaseSchema):
    """Schema for bulk threshold update operation"""
    items: List[ThresholdUpdateItem] = Field(
        ..., 
        min_items=1, 
        max_items=50, 
        description="Items to update thresholds",
        example=[
            {
                "item_id": "3a0b1590-8601-4925-bb00-21f1fb24bfc5",
                "item_type": "ingredient",
                "threshold": 400
            }
        ]
    )

    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "item_id": "3a0b1590-8601-4925-bb00-21f1fb24bfc5",
                        "item_type": "ingredient",
                        "threshold": 400
                    }
                ]
            }
        }
