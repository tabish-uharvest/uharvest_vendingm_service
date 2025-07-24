-- Migration to add payment_status and notes fields to orders table
-- Run this SQL script on your database

-- Add payment_status column
ALTER TABLE "orders" 
ADD COLUMN "payment_status" VARCHAR(20);

-- Add notes column  
ALTER TABLE "orders" 
ADD COLUMN "notes" TEXT;

-- Update the status constraint to include 'pending'
ALTER TABLE "orders" 
DROP CONSTRAINT IF EXISTS check_order_status;

ALTER TABLE "orders" 
ADD CONSTRAINT check_order_status 
CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'));

-- Optional: Add constraint for payment_status
ALTER TABLE "orders" 
ADD CONSTRAINT check_payment_status 
CHECK (payment_status IS NULL OR payment_status IN ('pending', 'paid', 'failed', 'refunded'));

-- Create index on payment_status for better query performance
CREATE INDEX IF NOT EXISTS idx_orders_payment_status ON orders(payment_status);

-- Create index on notes for text search if needed
-- CREATE INDEX IF NOT EXISTS idx_orders_notes ON orders USING gin(to_tsvector('english', notes));
