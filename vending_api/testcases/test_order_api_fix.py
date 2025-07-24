#!/usr/bin/env python3
"""
Test script to verify the complete order creation fix
Tests the actual endpoint with real data
"""

import requests
import json
import uuid
from datetime import datetime

def test_order_creation_api():
    """Test the actual order creation API endpoint"""
    
    # Test data from the user's request
    order_data = {
        "machine_id": "c2d72758-ad10-4906-bea7-5b44530f036a",
        "total_price": 15.75,  # Total price calculated by UI
        "total_calories": 245,  # Total calories calculated by UI
        "status": "processing",
        "session_id": "ui-test-session-001",
        "ingredients": [
            {
                "ingredient_id": "03358de9-e462-4549-ad88-37701bbe7f73",
                "grams_used": 40,
                "calories": 80  # UI calculated calories for this ingredient
            },
            {
                "ingredient_id": "b028ed10-419c-4fe4-9ec9-0f206cf58cff",
                "grams_used": 35,
                "calories": 70  # UI calculated calories for this ingredient
            },
            {
                "ingredient_id": "d60fdcf9-b25c-4c7e-98be-85de96b58f1d",
                "grams_used": 35,
                "calories": 95  # UI calculated calories for this ingredient
            }
        ],
        "addons": []
    }
    
    # Generate a test session ID
    session_id = f"test-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    print("=" * 60)
    print("TESTING ORDER CREATION API FIX")
    print("=" * 60)
    print(f"Session ID: {session_id}")
    print("Order Data:")
    print(json.dumps(order_data, indent=2))
    print()
    
    # Test the endpoint
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/orders"
    
    try:
        print(f"Making request to: {endpoint}")
        print(f"Session ID parameter: {session_id}")
        
        response = requests.post(
            endpoint,
            json=order_data,
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print("Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print()
        
        if response.status_code == 201:
            print("✓ SUCCESS - Order created successfully!")
            response_data = response.json()
            print("Response Data:")
            print(json.dumps(response_data, indent=2, default=str))
            
            # Validate response structure
            required_fields = ['id', 'machine_id', 'status', 'total_price', 'total_calories', 'items']
            missing_fields = [field for field in required_fields if field not in response_data]
            
            if missing_fields:
                print(f"⚠ Warning: Missing response fields: {missing_fields}")
            else:
                print("✓ Response structure is complete")
                
            # Validate items
            if len(response_data.get('items', [])) == len(order_data['ingredients']):
                print("✓ All ingredients were processed")
            else:
                print(f"⚠ Warning: Expected {len(order_data['ingredients'])} items, got {len(response_data.get('items', []))}")
            
        elif response.status_code == 422:
            print("✗ VALIDATION ERROR")
            error_data = response.json()
            print("Error Details:")
            print(json.dumps(error_data, indent=2))
            
        elif response.status_code == 404:
            print("✗ NOT FOUND ERROR")
            error_data = response.json()
            print("Error Details:")
            print(json.dumps(error_data, indent=2))
            print("\nThis might indicate that the machine or ingredients don't exist in the database.")
            
        elif response.status_code >= 500:
            print("✗ SERVER ERROR")
            try:
                error_data = response.json()
                print("Error Details:")
                print(json.dumps(error_data, indent=2))
            except:
                print("Raw error response:")
                print(response.text)
                
        else:
            print(f"✗ UNEXPECTED STATUS CODE: {response.status_code}")
            print("Response:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("✗ CONNECTION ERROR")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        print("Start it with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        
    except requests.exceptions.Timeout:
        print("✗ TIMEOUT ERROR")
        print("The request took too long. The server might be overloaded.")
        
    except Exception as e:
        print(f"✗ UNEXPECTED ERROR: {e}")


def test_curl_command_generation():
    """Generate curl command for manual testing"""
    
    order_data = {
        "machine_id": "c2d72758-ad10-4906-bea7-5b44530f036a",
        "total_price": 15.75,  # Total price calculated by UI
        "total_calories": 245,  # Total calories calculated by UI
        "status": "processing",
        "session_id": "curl-test-session-001",
        "ingredients": [
            {
                "ingredient_id": "03358de9-e462-4549-ad88-37701bbe7f73",
                "grams_used": 40,
                "calories": 80
            },
            {
                "ingredient_id": "b028ed10-419c-4fe4-9ec9-0f206cf58cff",
                "grams_used": 35,
                "calories": 70
            },
            {
                "ingredient_id": "d60fdcf9-b25c-4c7e-98be-85de96b58f1d",
                "grams_used": 35,
                "calories": 95
            }
        ],
        "addons": []
    }
    
    session_id = f"curl-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print("\n" + "=" * 60)
    print("CURL COMMAND FOR MANUAL TESTING")
    print("=" * 60)
    
    curl_command = f"""curl -X POST "http://localhost:8000/api/v1/orders?session_id={session_id}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(order_data)}'"""
    
    print(curl_command)
    print()


def main():
    """Run all tests"""
    test_order_creation_api()
    test_curl_command_generation()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("1. If you see a 201 response, the fix was successful!")
    print("2. If you see a 404, check that the machine and ingredients exist in the database")
    print("3. If you see a 422, there might be validation issues with the data")
    print("4. If you see a 500, there might still be code issues to fix")
    print("5. Use the curl command above for manual testing")


if __name__ == "__main__":
    main()
