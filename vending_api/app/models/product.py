from sqlalchemy import Column, String, Integer, Text, Numeric, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Ingredient(BaseModel):
    __tablename__ = "ingredients"
    
    name = Column(Text, nullable=False)
    emoji = Column(String(10))
    image = Column(Text)
    min_qty_g = Column(Integer, default=0, nullable=False)
    max_percent_limit = Column(Integer, default=100, nullable=False)
    calories_per_g = Column(Numeric(5, 2), default=0, nullable=False)
    price_per_gram = Column(Numeric(10, 4), default=0, nullable=False)
    
    __table_args__ = (
        CheckConstraint("min_qty_g >= 0", name='check_min_qty_g'),
        CheckConstraint("max_percent_limit > 0 AND max_percent_limit <= 100", name='check_max_percent_limit'),
        CheckConstraint("calories_per_g >= 0", name='check_calories_per_g'),
        CheckConstraint("price_per_gram >= 0", name='check_price_per_gram'),
    )
    
    # Relationships
    machine_ingredients = relationship("MachineIngredient", back_populates="ingredient")
    preset_ingredients = relationship("PresetIngredient", back_populates="ingredient")
    order_items = relationship("OrderItem", back_populates="ingredient")


class Addon(BaseModel):
    __tablename__ = "addons"
    
    # Override the created_at from BaseModel since addons table doesn't have this column
    created_at = None
    
    name = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), default=0, nullable=False)
    calories = Column(Integer, default=0, nullable=False)
    icon = Column(Text)
    
    __table_args__ = (
        CheckConstraint("price >= 0", name='check_addon_price'),
        CheckConstraint("calories >= 0", name='check_addon_calories'),
    )
    
    # Relationships
    machine_addons = relationship("MachineAddon", back_populates="addon")
    order_addons = relationship("OrderAddon", back_populates="addon")


class Preset(BaseModel):
    __tablename__ = "presets"
    
    name = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), default=0, nullable=False)
    calories = Column(Integer, default=0, nullable=False)
    description = Column(Text)
    image = Column(Text)
    
    __table_args__ = (
        CheckConstraint("category IN ('smoothie', 'salad')", name='check_preset_category'),
        CheckConstraint("price >= 0", name='check_preset_price'),
        CheckConstraint("calories >= 0", name='check_preset_calories'),
    )
    
    # Relationships
    preset_ingredients = relationship("PresetIngredient", back_populates="preset", cascade="all, delete-orphan")


class PresetIngredient(BaseModel):
    __tablename__ = "preset_ingredients"
    
    # Override the created_at from BaseModel since preset_ingredients table doesn't have this column
    created_at = None
    
    preset_id = Column(UUID(as_uuid=True), ForeignKey("presets.id"), nullable=False)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False)
    percent = Column(Integer, nullable=False)
    grams_used = Column(Integer, nullable=False)
    calories = Column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        CheckConstraint("percent > 0 AND percent <= 100", name='check_percent'),
        CheckConstraint("grams_used >= 0", name='check_grams_used'),
        CheckConstraint("calories >= 0", name='check_preset_ingredient_calories'),
    )
    
    # Relationships
    preset = relationship("Preset", back_populates="preset_ingredients")
    ingredient = relationship("Ingredient", back_populates="preset_ingredients")
