from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid
from .common import BaseSchema


# Ingredient Schemas
class IngredientBase(BaseSchema):
    """Base ingredient schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Ingredient name")
    emoji: Optional[str] = Field(None, max_length=10, description="Ingredient emoji")
    image: Optional[str] = Field(None, max_length=500, description="Image URL")
    min_qty_g: int = Field(0, ge=0, description="Minimum quantity in grams")
    max_percent_limit: Optional[int] = Field(None, ge=0, le=100, description="Maximum percentage limit")
    calories_per_g: Decimal = Field(..., ge=0, description="Calories per gram")
    price_per_gram: Decimal = Field(..., ge=0, description="Price per gram")


class IngredientCreate(IngredientBase):
    """Schema for creating a new ingredient"""
    pass


class IngredientUpdate(BaseSchema):
    """Schema for updating ingredient details"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    emoji: Optional[str] = Field(None, max_length=10)
    image: Optional[str] = Field(None, max_length=500)
    min_qty_g: Optional[int] = Field(None, ge=0)
    max_percent_limit: Optional[int] = Field(None, ge=0, le=100)
    calories_per_g: Optional[Decimal] = Field(None, ge=0)
    price_per_gram: Optional[Decimal] = Field(None, ge=0)


class IngredientResponse(IngredientBase):
    """Schema for ingredient response"""
    id: uuid.UUID
    created_at: datetime
    # Note: updated_at field removed as it doesn't exist in the database schema


# Addon Schemas
class AddonBase(BaseSchema):
    """Base addon schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Addon name")
    price: Decimal = Field(..., ge=0, description="Addon price")
    calories: int = Field(..., ge=0, description="Addon calories")
    icon: Optional[str] = Field(None, max_length=500, description="Icon URL")


class AddonCreate(AddonBase):
    """Schema for creating a new addon"""
    pass


class AddonUpdate(BaseSchema):
    """Schema for updating addon details"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)
    calories: Optional[int] = Field(None, ge=0)
    icon: Optional[str] = Field(None, max_length=500)


class AddonResponse(AddonBase):
    """Schema for addon response"""
    id: uuid.UUID
    # Note: created_at and updated_at fields removed as they don't exist in the database schema


# Preset Schemas
class PresetIngredientRequest(BaseSchema):
    """Schema for preset ingredient in request"""
    ingredient_id: uuid.UUID = Field(..., description="Ingredient ID")
    grams_used: int = Field(..., gt=0, le=1000, description="Grams used in preset")
    percent: Optional[int] = Field(None, ge=0, le=100, description="Percentage of total")


class PresetIngredientResponse(BaseSchema):
    """Schema for preset ingredient in response"""
    ingredient_id: uuid.UUID
    ingredient_name: str
    ingredient_emoji: Optional[str]
    grams_used: int
    percent: int
    calories: int
    price: Decimal


class PresetBase(BaseSchema):
    """Base preset schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Preset name")
    category: str = Field(..., description="Preset category (smoothie/salad)")
    price: Decimal = Field(..., ge=0, description="Preset price")
    calories: int = Field(..., ge=0, description="Total calories")
    description: Optional[str] = Field(None, max_length=500, description="Preset description")
    image: Optional[str] = Field(None, max_length=500, description="Image URL")
    
    @validator('category')
    def validate_category(cls, v):
        allowed_categories = ['smoothie', 'salad']
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of: {", ".join(allowed_categories)}')
        return v


class PresetCreate(PresetBase):
    """Schema for creating a new preset"""
    ingredients: List[PresetIngredientRequest] = Field(..., min_items=1, max_items=20, description="Preset ingredients")


class PresetUpdate(BaseSchema):
    """Schema for updating preset"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    calories: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=500)
    image: Optional[str] = Field(None, max_length=500)
    ingredients: Optional[List[PresetIngredientRequest]] = Field(None, min_items=1, max_items=20)
    
    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            allowed_categories = ['smoothie', 'salad']
            if v not in allowed_categories:
                raise ValueError(f'Category must be one of: {", ".join(allowed_categories)}')
        return v


class PresetResponse(PresetBase):
    """Schema for preset response (without ingredients)"""
    id: uuid.UUID
    created_at: datetime
    # Note: updated_at field removed as it doesn't exist in the database schema


class PresetDetailResponse(PresetBase):
    """Schema for detailed preset response (with ingredients)"""
    id: uuid.UUID
    ingredients: List[PresetIngredientResponse]
    created_at: datetime
    # Note: updated_at field removed as it doesn't exist in the database schema


# Availability Schemas
class IngredientAvailability(BaseSchema):
    """Schema for ingredient availability on machine"""
    ingredient_id: uuid.UUID
    name: str
    emoji: Optional[str]
    qty_available_g: int
    min_qty_g: int
    max_percent_limit: Optional[int]
    calories_per_g: Decimal
    price_per_gram: Decimal
    is_available: bool
    is_low_stock: bool


class AddonAvailability(BaseSchema):
    """Schema for addon availability on machine"""
    addon_id: uuid.UUID
    name: str
    icon: Optional[str]
    qty_available: int
    price: Decimal
    calories: int
    is_available: bool
    is_low_stock: bool


class PresetAvailability(PresetResponse):
    """Schema for preset availability on machine"""
    is_available: bool
    missing_ingredients: List[str]
    availability_percentage: int
