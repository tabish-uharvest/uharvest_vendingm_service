"""
Database view models for Urban Harvest Vending Machine system.
These models represent PostgreSQL views defined in the schema.
"""
from sqlalchemy import Column, String, Integer, Text, Numeric, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

# Create a separate base for views since they're read-only
ViewBase = declarative_base()


class VMachineIngredientInventory(ViewBase):
    """Model for v_machine_ingredient_inventory view"""
    __tablename__ = "v_machine_ingredient_inventory"
    
    machine_id = Column(UUID(as_uuid=True), primary_key=True)
    machine_location = Column(Text)
    machine_status = Column(String(20))
    ingredient_id = Column(UUID(as_uuid=True), primary_key=True)
    ingredient_name = Column(Text)
    ingredient_emoji = Column(String(10))
    price_per_gram = Column(Numeric(10, 4))
    calories_per_g = Column(Numeric(5, 2))
    max_percent_limit = Column(Integer)
    qty_available_g = Column(Integer)
    low_stock_threshold_g = Column(Integer)
    stock_status = Column(String(20))
    stock_percentage = Column(Numeric(5, 2))
    inventory_updated_at = Column(DateTime)
    min_qty_g = Column(Integer)  

class VMachineAddonInventory(ViewBase):
    """Model for v_machine_addon_inventory view"""
    __tablename__ = "v_machine_addon_inventory"
    
    machine_id = Column(UUID(as_uuid=True), primary_key=True)
    machine_location = Column(Text)
    machine_status = Column(String(20))
    addon_id = Column(UUID(as_uuid=True), primary_key=True)
    addon_name = Column(Text)
    addon_icon = Column(Text)
    addon_price = Column(Numeric(10, 2))
    addon_calories = Column(Integer)
    qty_available = Column(Integer)
    low_stock_threshold = Column(Integer)
    stock_status = Column(String(20))
    stock_percentage = Column(Numeric(5, 2))
    inventory_updated_at = Column(DateTime)


class VCompleteOrderDetails(ViewBase):
    """Model for v_complete_order_details view"""
    __tablename__ = "v_complete_order_details"
    
    order_id = Column(UUID(as_uuid=True), primary_key=True)
    session_id = Column(String(255))
    order_status = Column(String(20))
    total_price = Column(Numeric(10, 2))
    total_calories = Column(Integer)
    order_date = Column(DateTime)
    customer_name = Column(Text)
    customer_email = Column(String(255))
    machine_location = Column(Text)
    ingredients_used = Column(Text)
    addons_used = Column(Text)
    total_ingredients = Column(Integer)
    total_addons = Column(Integer)
    calories_from_ingredients = Column(Integer)
    calories_from_addons = Column(Integer)
    cost_from_ingredients = Column(Numeric(10, 4))
    cost_from_addons = Column(Numeric(10, 2))


class VMachineDashboard(ViewBase):
    """Model for v_machine_dashboard view"""
    __tablename__ = "v_machine_dashboard"
    
    machine_id = Column(UUID(as_uuid=True), primary_key=True)
    machine_location = Column(Text)
    machine_status = Column(String(20))
    cups_qty = Column(Integer)
    bowls_qty = Column(Integer)
    total_ingredients = Column(Integer)
    total_addons = Column(Integer)
    ingredients_in_stock = Column(Integer)
    ingredients_low_stock = Column(Integer)
    ingredients_out_of_stock = Column(Integer)
    addons_in_stock = Column(Integer)
    addons_low_stock = Column(Integer)
    addons_out_of_stock = Column(Integer)
    orders_last_30_days = Column(Integer)
    revenue_last_30_days = Column(Numeric(10, 2))
    last_order_date = Column(DateTime)
    orders_today = Column(Integer)


class VLowStockAlerts(ViewBase):
    """Model for v_low_stock_alerts view"""
    __tablename__ = "v_low_stock_alerts"
    
    item_type = Column(String(20), primary_key=True)
    machine_location = Column(Text, primary_key=True)
    item_name = Column(Text, primary_key=True)
    item_icon = Column(Text)
    current_stock = Column(Integer)
    threshold = Column(Integer)
    unit = Column(String(10))
    alert_level = Column(String(50))
    priority_order = Column(Integer)
    last_updated = Column(DateTime)


class VPresetAvailabilityPerMachine(ViewBase):
    """Model for v_preset_availability_per_machine view"""
    __tablename__ = "v_preset_availability_per_machine"
    
    machine_id = Column(UUID(as_uuid=True), primary_key=True)
    machine_location = Column(Text)
    preset_id = Column(UUID(as_uuid=True), primary_key=True)
    preset_name = Column(Text)
    preset_category = Column(String(50))
    preset_price = Column(Numeric(10, 2))
    preset_calories = Column(Integer)
    preset_description = Column(Text)
    preset_image = Column(Text)
    availability_status = Column(String(20))
    missing_ingredients = Column(Text)


class VAvailableItemsPerMachine(ViewBase):
    """Model for v_available_items_per_machine view"""
    __tablename__ = "v_available_items_per_machine"
    
    machine_id = Column(UUID(as_uuid=True), primary_key=True)
    machine_location = Column(Text)
    machine_status = Column(String(20))
    item_type = Column(String(20), primary_key=True)
    item_id = Column(UUID(as_uuid=True), primary_key=True)
    item_name = Column(Text)
    item_icon = Column(Text)
    item_price = Column(Numeric(10, 4))  # Could be price_per_gram or addon price
    item_calories = Column(Numeric(5, 2))  # Could be calories_per_g or addon calories
    quantity_available = Column(Integer)
    max_percent_limit = Column(Integer)  # Only for ingredients


class VOrderSummary(ViewBase):
    """Model for v_order_summary view"""
    __tablename__ = "v_order_summary"
    
    order_id = Column(UUID(as_uuid=True), primary_key=True)
    session_id = Column(String(255))
    order_status = Column(String(20))
    total_price = Column(Numeric(10, 2))
    total_calories = Column(Integer)
    order_date = Column(DateTime)
    user_id = Column(UUID(as_uuid=True))
    customer_name = Column(Text)
    customer_email = Column(String(255))
    customer_phone = Column(String(20))
    machine_id = Column(UUID(as_uuid=True))
    machine_location = Column(Text)
    machine_status = Column(String(20))


class VPresetDetails(ViewBase):
    """Model for v_preset_details view"""
    __tablename__ = "v_preset_details"
    
    preset_id = Column(UUID(as_uuid=True), primary_key=True)
    preset_name = Column(Text)
    preset_category = Column(String(50))
    preset_price = Column(Numeric(10, 2))
    preset_total_calories = Column(Integer)
    preset_description = Column(Text)
    preset_image = Column(Text)
    preset_created_at = Column(DateTime)
    ingredient_id = Column(UUID(as_uuid=True), primary_key=True)
    ingredient_name = Column(Text)
    ingredient_emoji = Column(String(10))
    ingredient_price_per_gram = Column(Numeric(10, 4))
    ingredient_calories_per_g = Column(Numeric(5, 2))
    ingredient_percent = Column(Integer)
    ingredient_grams_used = Column(Integer)
    ingredient_calories_in_preset = Column(Integer)
    ingredient_cost_in_preset = Column(Numeric(10, 4))
