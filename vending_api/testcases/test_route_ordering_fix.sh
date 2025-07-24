#!/bin/bash

# Test script to verify FastAPI route ordering fix for /orders/stats endpoint
# This script tests that /orders/stats no longer conflicts with /orders/{order_id}

BASE_URL="http://localhost:8000"

echo "Testing FastAPI Route Ordering Fix"
echo "=================================="
echo ""

# Test 1: /orders/stats endpoint (should work now)
echo "1. Testing /orders/stats endpoint..."
echo "Request: GET $BASE_URL/orders/stats"
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  "$BASE_URL/orders/stats" | head -20
echo ""

# Test 2: /orders/popular-items endpoint (should work now)
echo "2. Testing /orders/popular-items endpoint..."
echo "Request: GET $BASE_URL/orders/popular-items"
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  "$BASE_URL/orders/popular-items" | head -20
echo ""

# Test 3: /orders/{order_id} with a valid UUID (should still work)
echo "3. Testing /orders/{order_id} with valid UUID..."
echo "Request: GET $BASE_URL/orders/550e8400-e29b-41d4-a716-446655440000"
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  "$BASE_URL/orders/550e8400-e29b-41d4-a716-446655440000" | head -10
echo ""

# Test 4: /orders/{order_id} with invalid UUID (should give 422 validation error, not route conflict)
echo "4. Testing /orders/{order_id} with invalid UUID..."
echo "Request: GET $BASE_URL/orders/invalid-uuid"
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  "$BASE_URL/orders/invalid-uuid" | head -10
echo ""

echo "Route ordering test completed!"
echo ""
echo "Expected results:"
echo "- /orders/stats should return 200 with stats data (or 500 if no data)"
echo "- /orders/popular-items should return 200 with items data (or 500 if no data)"
echo "- /orders/{valid-uuid} should return 404 (order not found) or 200 if exists"
echo "- /orders/{invalid-uuid} should return 422 validation error, NOT route conflict"
