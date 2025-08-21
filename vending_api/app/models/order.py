from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid
from .base import BaseModel


class Order(BaseModel):
    __tablename__ = "orders"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("vending_machines.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(String(255), nullable=True)
    status = Column(String(20), default='processing', nullable=False)
    total_price = Column(Numeric(10, 2), default=0, nullable=False)
    total_calories = Column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')", name='check_order_status'),
        CheckConstraint("total_price >= 0", name='check_total_price'),
        CheckConstraint("total_calories >= 0", name='check_total_calories'),
    )
    
    # Relationships
    user = relationship("User", back_populates="orders")
    machine = relationship("VendingMachine", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    order_addons = relationship("OrderAddon", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Order item model - doesn't inherit created_at from BaseModel"""
    __tablename__ = "order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    ingredient_id = Column(UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="SET NULL"), nullable=True)
    qty_ml = Column(Integer, default=0, nullable=False)
    grams_used = Column(Integer, default=0, nullable=False)
    calories = Column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        CheckConstraint("qty_ml >= 0", name='check_qty_ml'),
        CheckConstraint("grams_used >= 0", name='check_grams_used'),
        CheckConstraint("calories >= 0", name='check_item_calories'),
    )
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    ingredient = relationship("Ingredient", back_populates="order_items")


class OrderAddon(Base):
    """Order addon model - doesn't inherit created_at from BaseModel"""
    __tablename__ = "order_addons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    addon_id = Column(UUID(as_uuid=True), ForeignKey("addons.id", ondelete="SET NULL"), nullable=True)
    qty = Column(Integer, default=1, nullable=False)
    calories = Column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        CheckConstraint("qty > 0", name='check_addon_qty'),
        CheckConstraint("calories >= 0", name='check_addon_calories'),
    )
    
    # Relationships
    order = relationship("Order", back_populates="order_addons")
    addon = relationship("Addon", back_populates="order_addons")
