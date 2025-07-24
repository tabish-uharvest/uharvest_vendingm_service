# Test script to verify FastAPI route ordering fix for /orders/stats endpoint
# This script tests that /orders/stats no longer conflicts with /orders/{order_id}

$BASE_URL = "http://localhost:8000"

Write-Host "Testing FastAPI Route Ordering Fix"
Write-Host "=================================="
Write-Host ""

# Test 1: /orders/stats endpoint (should work now)
Write-Host "1. Testing /orders/stats endpoint..."
Write-Host "Request: GET $BASE_URL/orders/stats"
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/orders/stats" -Method Get -ContentType "application/json"
    Write-Host "Response: $(($response | ConvertTo-Json -Depth 3).Substring(0, [Math]::Min(500, ($response | ConvertTo-Json -Depth 3).Length)))"
    Write-Host "HTTP Status: Success (200)"
} catch {
    Write-Host "HTTP Status: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error: $($_.Exception.Message)"
}
Write-Host ""

# Test 2: /orders/popular-items endpoint (should work now)
Write-Host "2. Testing /orders/popular-items endpoint..."
Write-Host "Request: GET $BASE_URL/orders/popular-items"
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/orders/popular-items" -Method Get -ContentType "application/json"
    Write-Host "Response: $(($response | ConvertTo-Json -Depth 3).Substring(0, [Math]::Min(500, ($response | ConvertTo-Json -Depth 3).Length)))"
    Write-Host "HTTP Status: Success (200)"
} catch {
    Write-Host "HTTP Status: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error: $($_.Exception.Message)"
}
Write-Host ""

# Test 3: /orders/{order_id} with a valid UUID (should still work)
Write-Host "3. Testing /orders/{order_id} with valid UUID..."
Write-Host "Request: GET $BASE_URL/orders/550e8400-e29b-41d4-a716-446655440000"
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/orders/550e8400-e29b-41d4-a716-446655440000" -Method Get -ContentType "application/json"
    Write-Host "Response: $(($response | ConvertTo-Json -Depth 3).Substring(0, [Math]::Min(500, ($response | ConvertTo-Json -Depth 3).Length)))"
    Write-Host "HTTP Status: Success (200)"
} catch {
    Write-Host "HTTP Status: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error: $($_.Exception.Message)"
}
Write-Host ""

# Test 4: /orders/{order_id} with invalid UUID (should give 422 validation error, not route conflict)
Write-Host "4. Testing /orders/{order_id} with invalid UUID..."
Write-Host "Request: GET $BASE_URL/orders/invalid-uuid"
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/orders/invalid-uuid" -Method Get -ContentType "application/json"
    Write-Host "Response: $(($response | ConvertTo-Json -Depth 3).Substring(0, [Math]::Min(500, ($response | ConvertTo-Json -Depth 3).Length)))"
    Write-Host "HTTP Status: Success (200)"
} catch {
    Write-Host "HTTP Status: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error: $($_.Exception.Message)"
}
Write-Host ""

Write-Host "Route ordering test completed!"
Write-Host ""
Write-Host "Expected results:"
Write-Host "- /orders/stats should return 200 with stats data (or 500 if no data)"
Write-Host "- /orders/popular-items should return 200 with items data (or 500 if no data)"
Write-Host "- /orders/{valid-uuid} should return 404 (order not found) or 200 if exists"
Write-Host "- /orders/{invalid-uuid} should return 422 validation error, NOT route conflict"
