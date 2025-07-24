from sqlalchemy import Column, String, Integer, CheckConstraint, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class VendingMachine(BaseModel):
    __tablename__ = "vending_machines"
    
    location = Column(Text, nullable=False)
    status = Column(String(20), default='active', nullable=False)
    cups_qty = Column(Integer, default=0, nullable=False)
    bowls_qty = Column(Integer, default=0, nullable=False)
    
    # Add check constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'maintenance', 'inactive')", name='check_status'),
        CheckConstraint("cups_qty >= 0", name='check_cups_qty'),
        CheckConstraint("bowls_qty >= 0", name='check_bowls_qty'),
    )
    
    # Relationships
    machine_ingredients = relationship("MachineIngredient", back_populates="machine", cascade="all, delete-orphan")
    machine_addons = relationship("MachineAddon", back_populates="machine", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="machine")


class MachineIngredient(BaseModel):
    __tablename__ = "machine_ingredients"
    
    machine_id = Column(UUID(as_uuid=True), ForeignKey("vending_machines.id"), nullable=False)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id"), nullable=False)
    qty_available_g = Column(Integer, default=0, nullable=False)
    low_stock_threshold_g = Column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        CheckConstraint("qty_available_g >= 0", name='check_qty_available_g'),
        CheckConstraint("low_stock_threshold_g >= 0", name='check_low_stock_threshold_g'),
    )
    
    # Relationships
    machine = relationship("VendingMachine", back_populates="machine_ingredients")
    ingredient = relationship("Ingredient")


class MachineAddon(BaseModel):
    __tablename__ = "machine_addons"
    
    machine_id = Column(UUID(as_uuid=True), ForeignKey("vending_machines.id"), nullable=False)
    addon_id = Column(UUID(as_uuid=True), ForeignKey("addons.id"), nullable=False)
    qty_available = Column(Integer, default=0, nullable=False)
    low_stock_threshold = Column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        CheckConstraint("qty_available >= 0", name='check_qty_available'),
        CheckConstraint("low_stock_threshold >= 0", name='check_low_stock_threshold'),
    )
    
    # Relationships
    machine = relationship("VendingMachine", back_populates="machine_addons")
    addon = relationship("Addon")
