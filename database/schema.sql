-- Urban Harvest Vending Machine Database Schema
-- This schema is designed for a vending machine that serves smoothies and salads.

-- Core Tables

CREATE TABLE "users" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "name" TEXT,
  "email" TEXT UNIQUE,
  "phone" TEXT,
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "vending_machines" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "location" TEXT NOT NULL,
  "status" TEXT DEFAULT 'active' CHECK (status IN ('active', 'maintenance', 'inactive')),
  "cups_qty" INT DEFAULT 0 CHECK (cups_qty >= 0),
  "bowls_qty" INT DEFAULT 0 CHECK (bowls_qty >= 0),
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "ingredients" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "name" TEXT NOT NULL,
  "image" TEXT,
  "min_qty_g" INT DEFAULT 0 CHECK (min_qty_g >= 0),
  "max_percent_limit" INT DEFAULT 100 CHECK (max_percent_limit >= 0 AND max_percent_limit <= 100),
  "calories_per_g" INT DEFAULT 0 CHECK (calories_per_g >= 0),
  "emoji" TEXT,
  "price_per_gram" DECIMAL(10,4) DEFAULT 0.00 CHECK (price_per_gram >= 0),
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "addons" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "name" TEXT NOT NULL,
  "price" DECIMAL(10,2) DEFAULT 0.00 CHECK (price >= 0),
  "calories" INT DEFAULT 0 CHECK (calories >= 0),
  "icon" TEXT
);

CREATE TABLE "presets" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "name" TEXT NOT NULL,
  "category" TEXT NOT NULL CHECK (category IN ('smoothie', 'salad')),
  "price" DECIMAL(10,2) DEFAULT 0.00 CHECK (price >= 0),
  "calories" INT DEFAULT 0 CHECK (calories >= 0),
  "description" TEXT,
  "image" TEXT,
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "preset_ingredients" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "preset_id" UUID NOT NULL,
  "ingredient_id" UUID NOT NULL,
  "percent" INT NOT NULL CHECK (percent >= 0 AND percent <= 100),
  "grams_used" INT DEFAULT 0 CHECK (grams_used >= 0),
  "calories" INT DEFAULT 0 CHECK (calories >= 0),
  FOREIGN KEY ("preset_id") REFERENCES "presets" ("id") ON DELETE CASCADE,
  FOREIGN KEY ("ingredient_id") REFERENCES "ingredients" ("id") ON DELETE CASCADE
);

CREATE TABLE "orders" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "user_id" UUID,
  "machine_id" UUID,
  "total_price" DECIMAL(10,2) DEFAULT 0.00 CHECK (total_price >= 0),
  "total_calories" INT DEFAULT 0 CHECK (total_calories >= 0),
  "status" TEXT DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed', 'cancelled')),
  "session_id" TEXT,
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE SET NULL,
  FOREIGN KEY ("machine_id") REFERENCES "vending_machines" ("id") ON DELETE SET NULL
);

CREATE TABLE "order_items" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "order_id" UUID NOT NULL,
  "ingredient_id" UUID,
  "qty_ml" INT DEFAULT 0 CHECK (qty_ml >= 0),
  "grams_used" INT DEFAULT 0 CHECK (grams_used >= 0),
  "calories" INT DEFAULT 0 CHECK (calories >= 0),
  FOREIGN KEY ("order_id") REFERENCES "orders" ("id") ON DELETE CASCADE,
  FOREIGN KEY ("ingredient_id") REFERENCES "ingredients" ("id") ON DELETE SET NULL
);

CREATE TABLE "order_addons" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "order_id" UUID NOT NULL,
  "addon_id" UUID,
  "qty" INT DEFAULT 1 CHECK (qty > 0),
  "calories" INT DEFAULT 0 CHECK (calories >= 0),
  FOREIGN KEY ("order_id") REFERENCES "orders" ("id") ON DELETE CASCADE,
  FOREIGN KEY ("addon_id") REFERENCES "addons" ("id") ON DELETE SET NULL
);

-- 2.1 Create machine_ingredients: ingredient stock per machine
CREATE TABLE IF NOT EXISTS "machine_ingredients" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "machine_id" UUID NOT NULL,
  "ingredient_id" UUID NOT NULL,
  "qty_available_g" INT DEFAULT 0 CHECK (qty_available_g >= 0),
  "low_stock_threshold_g" INT DEFAULT 0 CHECK (low_stock_threshold_g >= 0),
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("machine_id", "ingredient_id"),
  FOREIGN KEY ("machine_id")
    REFERENCES "vending_machines" ("id") ON DELETE CASCADE,
  FOREIGN KEY ("ingredient_id")
    REFERENCES "ingredients" ("id") ON DELETE RESTRICT
);

-- 2.2 Create machine_addons: addon stock per machine
CREATE TABLE IF NOT EXISTS "machine_addons" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "machine_id" UUID NOT NULL,
  "addon_id" UUID NOT NULL,
  "qty_available" INT DEFAULT 0 CHECK (qty_available >= 0),
  "low_stock_threshold" INT DEFAULT 0 CHECK (low_stock_threshold >= 0),
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("machine_id", "addon_id"),
  FOREIGN KEY ("machine_id")
    REFERENCES "vending_machines" ("id") ON DELETE CASCADE,
  FOREIGN KEY ("addon_id")
    REFERENCES "addons" ("id") ON DELETE RESTRICT
);

-- Performance Indexes
CREATE INDEX idx_presets_category ON presets(category);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_machine_id ON orders(machine_id);
CREATE INDEX idx_orders_session_id ON orders(session_id);
CREATE INDEX idx_preset_ingredients_preset_id ON preset_ingredients(preset_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_addons_order_id ON order_addons(order_id);
CREATE INDEX idx_machine_ingredients_machine_id ON machine_ingredients(machine_id);
CREATE INDEX idx_machine_ingredients_ingredient_id ON machine_ingredients(ingredient_id);
CREATE INDEX idx_machine_addons_machine_id ON machine_addons(machine_id);
CREATE INDEX idx_machine_addons_addon_id ON machine_addons(addon_id);

-- Sample Data for Development/Testing
INSERT INTO "vending_machines" ("location", "status", "cups_qty", "bowls_qty") VALUES
('Main Campus - Building A', 'active', 100, 50),
('Student Center', 'active', 75, 25);

INSERT INTO "ingredients" ("name", "emoji", "min_qty_g", "max_percent_limit", "calories_per_g", "price_per_gram") VALUES
-- Smoothie Base Ingredients
('Banana', '🍌', 50, 40, 1, 0.0015),
('Strawberry', '🍓', 30, 35, 1, 0.0020),
('Blueberry', '🫐', 25, 30, 1, 0.0025),
('Mango', '🥭', 40, 35, 1, 0.0022),
('Pineapple', '🍍', 35, 30, 1, 0.0018),
('Spinach', '🥬', 20, 25, 0, 0.0012),
('Kale', '🥬', 20, 25, 0, 0.0014),
('Coconut Water', '🥥', 100, 50, 0, 0.0008),
('Almond Milk', '🥛', 150, 60, 0, 0.0010),
('Greek Yogurt', '🥛', 50, 40, 1, 0.0016),

-- Salad Base Ingredients
('Mixed Greens', '🥗', 30, 40, 0, 0.0020),
('Cherry Tomatoes', '🍅', 25, 30, 0, 0.0025),
('Cucumber', '🥒', 30, 35, 0, 0.0015),
('Carrots', '🥕', 25, 30, 0, 0.0018),
('Bell Peppers', '🫑', 20, 25, 0, 0.0022),
('Red Onion', '🧅', 15, 20, 0, 0.0014),
('Feta Cheese', '🧀', 20, 25, 3, 0.0035),
('Chickpeas', '🫘', 30, 30, 2, 0.0028),
('Avocado', '🥑', 25, 25, 2, 0.0040),
('Olive Oil', '🫒', 10, 15, 9, 0.0050);

INSERT INTO "addons" ("name", "price", "calories", "icon") VALUES
('Protein Powder', 2.50, 120, '💪'),
('Chia Seeds', 1.00, 60, '🌱'),
('Honey', 0.75, 64, '🍯'),
('Nuts Mix', 1.50, 90, '🥜'),
('Extra Dressing', 0.50, 45, '🥗');

INSERT INTO "presets" ("name", "category", "price", "calories", "description", "image") VALUES
-- Smoothie Presets
('Tropical Paradise', 'smoothie', 8.99, 280, 'Mango, pineapple, coconut water blend', '/images/tropical-smoothie.jpg'),
('Green Goddess', 'smoothie', 9.49, 220, 'Spinach, banana, almond milk powerhouse', '/images/green-smoothie.jpg'),
('Berry Blast', 'smoothie', 8.75, 250, 'Mixed berries with Greek yogurt', '/images/berry-smoothie.jpg'),

-- Salad Presets
('Mediterranean Mix', 'salad', 10.99, 320, 'Fresh greens with feta and olives', '/images/mediterranean-salad.jpg'),
('Garden Fresh', 'salad', 9.99, 180, 'Crisp vegetables with house dressing', '/images/garden-salad.jpg'),
('Protein Power', 'salad', 12.49, 450, 'Chickpeas, avocado, and mixed greens', '/images/protein-salad.jpg');

-- Preset Ingredients for Tropical Paradise Smoothie
INSERT INTO "preset_ingredients" ("preset_id", "ingredient_id", "percent", "grams_used", "calories") VALUES
((SELECT id FROM presets WHERE name = 'Tropical Paradise'), (SELECT id FROM ingredients WHERE name = 'Mango'), 30, 150, 90),
((SELECT id FROM presets WHERE name = 'Tropical Paradise'), (SELECT id FROM ingredients WHERE name = 'Pineapple'), 25, 125, 60),
((SELECT id FROM presets WHERE name = 'Tropical Paradise'), (SELECT id FROM ingredients WHERE name = 'Coconut Water'), 45, 225, 130);

-- Preset Ingredients for Mediterranean Mix Salad
INSERT INTO "preset_ingredients" ("preset_id", "ingredient_id", "percent", "grams_used", "calories") VALUES
((SELECT id FROM presets WHERE name = 'Mediterranean Mix'), (SELECT id FROM ingredients WHERE name = 'Mixed Greens'), 40, 100, 20),
((SELECT id FROM presets WHERE name = 'Mediterranean Mix'), (SELECT id FROM ingredients WHERE name = 'Cherry Tomatoes'), 25, 60, 15),
((SELECT id FROM presets WHERE name = 'Mediterranean Mix'), (SELECT id FROM ingredients WHERE name = 'Feta Cheese'), 20, 50, 150),
((SELECT id FROM presets WHERE name = 'Mediterranean Mix'), (SELECT id FROM ingredients WHERE name = 'Olive Oil'), 15, 15, 135);



--below are some changes to the schema after the initial creation.
ALTER TABLE "preset_ingredients"
DROP CONSTRAINT preset_ingredients_ingredient_id_fkey;

ALTER TABLE "preset_ingredients"
ADD CONSTRAINT preset_ingredients_ingredient_id_fkey
FOREIGN KEY ("ingredient_id")
REFERENCES "ingredients" ("id")
ON DELETE RESTRICT;


-- Sample data for machine_ingredients (stock per machine)
INSERT INTO "machine_ingredients" ("machine_id", "ingredient_id", "qty_available_g", "low_stock_threshold_g") VALUES
-- Main Campus - Building A (first machine)
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Banana'), 4500, 500),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Strawberry'), 2800, 300),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Blueberry'), 1800, 250),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Mango'), 2200, 400),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Pineapple'), 1900, 350),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Spinach'), 1400, 200),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Kale'), 1100, 200),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Coconut Water'), 7500, 1000),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Almond Milk'), 5500, 1500),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Greek Yogurt'), 2800, 500),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Mixed Greens'), 1800, 300),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Cherry Tomatoes'), 1400, 250),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Cucumber'), 1900, 300),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Carrots'), 1700, 250),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Bell Peppers'), 1100, 200),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Red Onion'), 750, 150),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Feta Cheese'), 900, 200),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Chickpeas'), 1400, 300),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Avocado'), 1100, 250),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM ingredients WHERE name = 'Olive Oil'), 450, 100),

-- Student Center (second machine)
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Banana'), 3200, 500),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Strawberry'), 2100, 300),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Blueberry'), 1500, 250),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Mango'), 1800, 400),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Pineapple'), 1600, 350),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Spinach'), 1000, 200),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Kale'), 900, 200),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Coconut Water'), 5500, 1000),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Almond Milk'), 4200, 1500),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Greek Yogurt'), 2100, 500),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Mixed Greens'), 1300, 300),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Cherry Tomatoes'), 1100, 250),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Cucumber'), 1400, 300),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Carrots'), 1200, 250),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Bell Peppers'), 800, 200),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Red Onion'), 550, 150),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Feta Cheese'), 700, 200),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Chickpeas'), 1100, 300),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Avocado'), 850, 250),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM ingredients WHERE name = 'Olive Oil'), 350, 100);

-- Sample data for machine_addons (addon stock per machine)
INSERT INTO "machine_addons" ("machine_id", "addon_id", "qty_available", "low_stock_threshold") VALUES
-- Main Campus - Building A addons
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM addons WHERE name = 'Protein Powder'), 25, 5),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM addons WHERE name = 'Chia Seeds'), 40, 8),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM addons WHERE name = 'Honey'), 30, 6),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM addons WHERE name = 'Nuts Mix'), 35, 7),
((SELECT id FROM vending_machines WHERE location = 'Main Campus - Building A'), (SELECT id FROM addons WHERE name = 'Extra Dressing'), 50, 10),

-- Student Center addons
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM addons WHERE name = 'Protein Powder'), 18, 5),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM addons WHERE name = 'Chia Seeds'), 28, 8),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM addons WHERE name = 'Honey'), 22, 6),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM addons WHERE name = 'Nuts Mix'), 26, 7),
((SELECT id FROM vending_machines WHERE location = 'Student Center'), (SELECT id FROM addons WHERE name = 'Extra Dressing'), 35, 10);

-- ==============================================
-- VIEWS FOR EASY DATA ACCESS AND UNDERSTANDING
-- ==============================================

-- 1. Machine Inventory Status View (Ingredients)
CREATE VIEW "v_machine_ingredient_inventory" AS
SELECT 
    vm.id as machine_id,
    vm.location as machine_location,
    vm.status as machine_status,
    i.id as ingredient_id,
    i.name as ingredient_name,
    i.emoji as ingredient_emoji,
    i.price_per_gram,
    i.calories_per_g,
    i.max_percent_limit,
    mi.qty_available_g,
    mi.low_stock_threshold_g,
    CASE 
        WHEN mi.qty_available_g = 0 THEN 'OUT_OF_STOCK'
        WHEN mi.qty_available_g <= mi.low_stock_threshold_g THEN 'LOW_STOCK'
        ELSE 'AVAILABLE'
    END as stock_status,
    ROUND((mi.qty_available_g::DECIMAL / NULLIF(mi.low_stock_threshold_g, 0)) * 100, 2) as stock_percentage,
    mi.created_at as inventory_updated_at
FROM machine_ingredients mi
JOIN vending_machines vm ON mi.machine_id = vm.id
JOIN ingredients i ON mi.ingredient_id = i.id
ORDER BY vm.location, i.name;

-- 2. Machine Addon Inventory View
CREATE VIEW "v_machine_addon_inventory" AS
SELECT 
    vm.id as machine_id,
    vm.location as machine_location,
    vm.status as machine_status,
    a.id as addon_id,
    a.name as addon_name,
    a.icon as addon_icon,
    a.price as addon_price,
    a.calories as addon_calories,
    ma.qty_available,
    ma.low_stock_threshold,
    CASE 
        WHEN ma.qty_available = 0 THEN 'OUT_OF_STOCK'
        WHEN ma.qty_available <= ma.low_stock_threshold THEN 'LOW_STOCK'
        ELSE 'AVAILABLE'
    END as stock_status,
    ROUND((ma.qty_available::DECIMAL / NULLIF(ma.low_stock_threshold, 0)) * 100, 2) as stock_percentage,
    ma.created_at as inventory_updated_at
FROM machine_addons ma
JOIN vending_machines vm ON ma.machine_id = vm.id
JOIN addons a ON ma.addon_id = a.id
ORDER BY vm.location, a.name;

-- 3. Complete Machine Inventory (Combined View)
CREATE VIEW "v_complete_machine_inventory" AS
SELECT 
    machine_id,
    machine_location,
    machine_status,
    'ingredient' as item_type,
    ingredient_id as item_id,
    ingredient_name as item_name,
    ingredient_emoji as item_icon,
    price_per_gram as item_price,
    calories_per_g as item_calories,
    qty_available_g as quantity_available,
    low_stock_threshold_g as low_stock_threshold,
    stock_status,
    stock_percentage,
    inventory_updated_at,
    max_percent_limit
FROM v_machine_ingredient_inventory
UNION ALL
SELECT 
    machine_id,
    machine_location,
    machine_status,
    'addon' as item_type,
    addon_id as item_id,
    addon_name as item_name,
    addon_icon as item_icon,
    addon_price as item_price,
    addon_calories as item_calories,
    qty_available as quantity_available,
    low_stock_threshold as low_stock_threshold,
    stock_status,
    stock_percentage,
    inventory_updated_at,
    NULL as max_percent_limit
FROM v_machine_addon_inventory
ORDER BY machine_location, item_type, item_name;

-- 4. Preset Details with Ingredients View
CREATE VIEW "v_preset_details" AS
SELECT 
    p.id as preset_id,
    p.name as preset_name,
    p.category as preset_category,
    p.price as preset_price,
    p.calories as preset_total_calories,
    p.description as preset_description,
    p.image as preset_image,
    p.created_at as preset_created_at,
    i.id as ingredient_id,
    i.name as ingredient_name,
    i.emoji as ingredient_emoji,
    i.price_per_gram as ingredient_price_per_gram,
    i.calories_per_g as ingredient_calories_per_g,
    pi.percent as ingredient_percent,
    pi.grams_used as ingredient_grams_used,
    pi.calories as ingredient_calories_in_preset,
    ROUND((pi.grams_used * i.price_per_gram), 4) as ingredient_cost_in_preset
FROM presets p
JOIN preset_ingredients pi ON p.id = pi.preset_id
JOIN ingredients i ON pi.ingredient_id = i.id
ORDER BY p.name, pi.percent DESC;

-- 5. Order Summary View
CREATE VIEW "v_order_summary" AS
SELECT 
    o.id as order_id,
    o.session_id,
    o.status as order_status,
    o.total_price,
    o.total_calories,
    o.created_at as order_date,
    u.id as user_id,
    u.name as customer_name,
    u.email as customer_email,
    u.phone as customer_phone,
    vm.id as machine_id,
    vm.location as machine_location,
    vm.status as machine_status
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
LEFT JOIN vending_machines vm ON o.machine_id = vm.id
ORDER BY o.created_at DESC;

-- 6. Order Items with Details View
CREATE VIEW "v_order_items_details" AS
SELECT 
    oi.id as order_item_id,
    o.id as order_id,
    o.session_id,
    o.status as order_status,
    o.created_at as order_date,
    vm.location as machine_location,
    i.id as ingredient_id,
    i.name as ingredient_name,
    i.emoji as ingredient_emoji,
    i.price_per_gram,
    oi.qty_ml,
    oi.grams_used,
    oi.calories as calories_from_ingredient,
    ROUND((oi.grams_used * i.price_per_gram), 4) as ingredient_cost,
    u.name as customer_name
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
LEFT JOIN ingredients i ON oi.ingredient_id = i.id
LEFT JOIN users u ON o.user_id = u.id
LEFT JOIN vending_machines vm ON o.machine_id = vm.id
ORDER BY o.created_at DESC, oi.id;

-- 7. Order Addons with Details View
CREATE VIEW "v_order_addons_details" AS
SELECT 
    oa.id as order_addon_id,
    o.id as order_id,
    o.session_id,
    o.status as order_status,
    o.created_at as order_date,
    vm.location as machine_location,
    a.id as addon_id,
    a.name as addon_name,
    a.icon as addon_icon,
    a.price as addon_unit_price,
    a.calories as addon_unit_calories,
    oa.qty as addon_quantity,
    oa.calories as total_calories_from_addon,
    ROUND((a.price * oa.qty), 2) as total_addon_cost,
    u.name as customer_name
FROM order_addons oa
JOIN orders o ON oa.order_id = o.id
LEFT JOIN addons a ON oa.addon_id = a.id
LEFT JOIN users u ON o.user_id = u.id
LEFT JOIN vending_machines vm ON o.machine_id = vm.id
ORDER BY o.created_at DESC, oa.id;

-- 8. Complete Order Details View (Everything in one view)
CREATE VIEW "v_complete_order_details" AS
SELECT 
    o.id as order_id,
    o.session_id,
    o.status as order_status,
    o.total_price,
    o.total_calories,
    o.created_at as order_date,
    u.name as customer_name,
    u.email as customer_email,
    vm.location as machine_location,
    
    -- Ingredient details
    STRING_AGG(DISTINCT i.name || ' (' || oi.grams_used || 'g)', ', ') as ingredients_used,
    
    -- Addon details  
    STRING_AGG(DISTINCT a.name || ' (x' || oa.qty || ')', ', ') as addons_used,
    
    -- Counts
    COUNT(DISTINCT oi.id) as total_ingredients,
    COUNT(DISTINCT oa.id) as total_addons,
    
    -- Totals from components
    COALESCE(SUM(DISTINCT oi.calories), 0) as calories_from_ingredients,
    COALESCE(SUM(DISTINCT oa.calories), 0) as calories_from_addons,
    COALESCE(SUM(DISTINCT oi.grams_used * i.price_per_gram), 0) as cost_from_ingredients,
    COALESCE(SUM(DISTINCT a.price * oa.qty), 0) as cost_from_addons
    
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
LEFT JOIN vending_machines vm ON o.machine_id = vm.id
LEFT JOIN order_items oi ON o.id = oi.order_id
LEFT JOIN ingredients i ON oi.ingredient_id = i.id
LEFT JOIN order_addons oa ON o.id = oa.order_id
LEFT JOIN addons a ON oa.addon_id = a.id
GROUP BY o.id, o.session_id, o.status, o.total_price, o.total_calories, o.created_at, 
         u.name, u.email, vm.location
ORDER BY o.created_at DESC;

-- 9. Machine Performance Dashboard View
CREATE VIEW "v_machine_dashboard" AS
SELECT 
    vm.id as machine_id,
    vm.location as machine_location,
    vm.status as machine_status,
    vm.cups_qty,
    vm.bowls_qty,
    
    -- Inventory counts
    COUNT(DISTINCT mi.ingredient_id) as total_ingredients,
    COUNT(DISTINCT ma.addon_id) as total_addons,
    
    -- Stock status counts
    COUNT(DISTINCT mi.ingredient_id) FILTER (WHERE mi.qty_available_g > mi.low_stock_threshold_g) as ingredients_in_stock,
    COUNT(DISTINCT mi.ingredient_id) FILTER (WHERE mi.qty_available_g <= mi.low_stock_threshold_g AND mi.qty_available_g > 0) as ingredients_low_stock,
    COUNT(DISTINCT mi.ingredient_id) FILTER (WHERE mi.qty_available_g = 0) as ingredients_out_of_stock,
    
    COUNT(DISTINCT ma.addon_id) FILTER (WHERE ma.qty_available > ma.low_stock_threshold) as addons_in_stock,
    COUNT(DISTINCT ma.addon_id) FILTER (WHERE ma.qty_available <= ma.low_stock_threshold AND ma.qty_available > 0) as addons_low_stock,
    COUNT(DISTINCT ma.addon_id) FILTER (WHERE ma.qty_available = 0) as addons_out_of_stock,
    
    -- Order statistics (last 30 days)
    COUNT(DISTINCT o.id) FILTER (WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days') as orders_last_30_days,
    COALESCE(SUM(o.total_price) FILTER (WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days'), 0) as revenue_last_30_days,
    
    -- Recent order info
    MAX(o.created_at) as last_order_date,
    COUNT(DISTINCT o.id) FILTER (WHERE o.created_at >= CURRENT_DATE) as orders_today
    
FROM vending_machines vm
LEFT JOIN machine_ingredients mi ON vm.id = mi.machine_id
LEFT JOIN machine_addons ma ON vm.id = ma.machine_id
LEFT JOIN orders o ON vm.id = o.machine_id
GROUP BY vm.id, vm.location, vm.status, vm.cups_qty, vm.bowls_qty
ORDER BY vm.location;

-- 10. Low Stock Alert View
CREATE VIEW "v_low_stock_alerts" AS
SELECT 
    'ingredient' as item_type,
    vm.location as machine_location,
    i.name as item_name,
    i.emoji as item_icon,
    mi.qty_available_g as current_stock,
    mi.low_stock_threshold_g as threshold,
    'grams' as unit,
    CASE 
        WHEN mi.qty_available_g = 0 THEN 'CRITICAL - OUT OF STOCK'
        WHEN mi.qty_available_g <= mi.low_stock_threshold_g THEN 'WARNING - LOW STOCK'
    END as alert_level,
    CASE 
        WHEN mi.qty_available_g = 0 THEN 1 
        ELSE 2 
    END as priority_order,
    mi.created_at as last_updated
FROM machine_ingredients mi
JOIN vending_machines vm ON mi.machine_id = vm.id
JOIN ingredients i ON mi.ingredient_id = i.id
WHERE mi.qty_available_g <= mi.low_stock_threshold_g

UNION ALL

SELECT 
    'addon' as item_type,
    vm.location as machine_location,
    a.name as item_name,
    a.icon as item_icon,
    ma.qty_available as current_stock,
    ma.low_stock_threshold as threshold,
    'units' as unit,
    CASE 
        WHEN ma.qty_available = 0 THEN 'CRITICAL - OUT OF STOCK'
        WHEN ma.qty_available <= ma.low_stock_threshold THEN 'WARNING - LOW STOCK'
    END as alert_level,
    CASE 
        WHEN ma.qty_available = 0 THEN 1 
        ELSE 2 
    END as priority_order,
    ma.created_at as last_updated
FROM machine_addons ma
JOIN vending_machines vm ON ma.machine_id = vm.id
JOIN addons a ON ma.addon_id = a.id
WHERE ma.qty_available <= ma.low_stock_threshold

ORDER BY priority_order, machine_location, item_type, item_name;

-- 11. Available Items per Machine View (for frontend)
CREATE VIEW "v_available_items_per_machine" AS
SELECT 
    machine_id,
    machine_location,
    machine_status,
    item_type,
    item_id,
    item_name,
    item_icon,
    item_price,
    item_calories,
    quantity_available,
    max_percent_limit
FROM v_complete_machine_inventory
WHERE stock_status = 'AVAILABLE' 
  AND machine_status = 'active'
ORDER BY machine_location, item_type, item_name;

-- 12. Preset Availability per Machine View
CREATE VIEW "v_preset_availability_per_machine" AS
SELECT DISTINCT
    vm.id as machine_id,
    vm.location as machine_location,
    p.id as preset_id,
    p.name as preset_name,
    p.category as preset_category,
    p.price as preset_price,
    p.calories as preset_calories,
    p.description as preset_description,
    p.image as preset_image,
    
    -- Check if all ingredients are available
    CASE 
        WHEN COUNT(pi.ingredient_id) = COUNT(mi.ingredient_id) FILTER (WHERE mi.qty_available_g >= pi.grams_used)
        THEN 'AVAILABLE'
        ELSE 'UNAVAILABLE'
    END as availability_status,
    
    -- List missing ingredients
    STRING_AGG(
        CASE 
            WHEN mi.qty_available_g < pi.grams_used OR mi.qty_available_g IS NULL 
            THEN i.name 
        END, 
        ', '
    ) as missing_ingredients
    
FROM vending_machines vm
CROSS JOIN presets p
JOIN preset_ingredients pi ON p.id = pi.preset_id
JOIN ingredients i ON pi.ingredient_id = i.id
LEFT JOIN machine_ingredients mi ON vm.id = mi.machine_id AND pi.ingredient_id = mi.ingredient_id
WHERE vm.status = 'active'
GROUP BY vm.id, vm.location, p.id, p.name, p.category, p.price, p.calories, p.description, p.image
ORDER BY vm.location, p.category, p.name;
