# Order Status Update Test Commands
# 
# After removing payment_status and notes fields from Order model
# These commands should now work properly

# 1. Update order status to completed (with payment_status and notes - will be ignored)
curl -X PUT "http://localhost:8000/api/v1/orders/101bc4e8-9c55-4a35-a701-496ab68604a2/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "payment_status": "paid",
    "notes": "Order successfully prepared and delivered"
  }'

# 2. Simple status update (only status field)
curl -X PUT "http://localhost:8000/api/v1/orders/101bc4e8-9c55-4a35-a701-496ab68604a2/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'

# 3. Mark as failed
curl -X PUT "http://localhost:8000/api/v1/orders/101bc4e8-9c55-4a35-a701-496ab68604a2/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "failed"
  }'

# 4. Mark as cancelled  
curl -X PUT "http://localhost:8000/api/v1/orders/101bc4e8-9c55-4a35-a701-496ab68604a2/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "cancelled"
  }'

# 5. Check current order status (GET request)
curl -X GET "http://localhost:8000/api/v1/orders/101bc4e8-9c55-4a35-a701-496ab68604a2" \
  -H "Content-Type: application/json"
