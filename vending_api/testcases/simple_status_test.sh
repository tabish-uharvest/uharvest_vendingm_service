# Simple curl command to test order status update after fixing greenlet spawn issue

# Test 1: Update status to completed
curl -X PUT "http://localhost:8000/api/v1/orders/101bc4e8-9c55-4a35-a701-496ab68604a2/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Expected response: 200 OK with order details

# Test 2: Update status to failed  
curl -X PUT "http://localhost:8000/api/v1/orders/101bc4e8-9c55-4a35-a701-496ab68604a2/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "failed"}'

# Test 3: Get order details to verify status
curl -X GET "http://localhost:8000/api/v1/orders/101bc4e8-9c55-4a35-a701-496ab68604a2" \
  -H "Content-Type: application/json"
