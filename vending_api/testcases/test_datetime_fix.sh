#!/bin/bash

# Simple curl test for the datetime serialization fix

BASE_URL="http://localhost:8000/api/v1"

echo "Testing Datetime Serialization Fix"
echo "=================================="
echo ""

# Test 1: /orders/stats endpoint
echo "1. Testing /orders/stats endpoint..."
echo "curl -X GET \"$BASE_URL/orders/stats?machine_id=c2d72758-ad10-4906-bea7-5b44530f036a\""
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  "$BASE_URL/orders/stats?machine_id=c2d72758-ad10-4906-bea7-5b44530f036a"
echo ""

# Test 2: /orders/popular-items endpoint  
echo "2. Testing /orders/popular-items endpoint..."
echo "curl -X GET \"$BASE_URL/orders/popular-items\""
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  "$BASE_URL/orders/popular-items"
echo ""

echo "Test completed!"
echo ""
echo "Expected behavior:"
echo "- Should return 200 with valid JSON (if there's data)"
echo "- Should return 500 with proper error JSON (if there's a backend error)"
echo "- Should NOT crash with 'datetime is not JSON serializable' error"
