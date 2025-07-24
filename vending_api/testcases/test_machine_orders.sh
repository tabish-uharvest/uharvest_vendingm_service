# Test machine orders endpoint after greenlet spawn fix

# Test 1: Basic machine orders request
curl -X GET "http://localhost:8000/api/v1/machines/c2d72758-ad10-4906-bea7-5b44530f036a/orders?skip=0&limit=5" \
  -H "Content-Type: application/json"

# Test 2: Orders with status filter
curl -X GET "http://localhost:8000/api/v1/machines/c2d72758-ad10-4906-bea7-5b44530f036a/orders?skip=0&limit=10&status=completed" \
  -H "Content-Type: application/json"

# Test 3: Orders with processing status
curl -X GET "http://localhost:8000/api/v1/machines/c2d72758-ad10-4906-bea7-5b44530f036a/orders?skip=0&limit=10&status=processing" \
  -H "Content-Type: application/json"

# Test 4: Order status update (to make sure both endpoints work)
curl -X PUT "http://localhost:8000/api/v1/orders/101bc4e8-9c55-4a35-a701-496ab68604a2/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
