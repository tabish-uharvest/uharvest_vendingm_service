#!/usr/bin/env python3
"""
Final test for order creation with UI-calculated total price
Tests the exact request from the user
"""

import requests
import json
from decimal import Decimal

def test_user_order_request():
    """Test the exact order from user's request with total price"""
    
    # Exact data from user's request with added total_price
    order_data = {
        "machine_id": "c2d72758-ad10-4906-bea7-5b44530f036a",
        "total_price": 15.75,  # UI calculated total price
        "ingredients": [
            {
                "ingredient_id": "03358de9-e462-4549-ad88-37701bbe7f73",
                "grams_used": 40
            },
            {
                "ingredient_id": "b028ed10-419c-4fe4-9ec9-0f206cf58cff",
                "grams_used": 35
            },
            {
                "ingredient_id": "d60fdcf9-b25c-4c7e-98be-85de96b58f1d",
                "grams_used": 35
            }
        ],
        "addons": []
    }
    
    session_id = "ui-test-session-001"
    
    print("=" * 60)
    print("TESTING USER'S EXACT ORDER REQUEST")
    print("=" * 60)
    print("Order Data:")
    print(json.dumps(order_data, indent=2))
    print(f"Session ID: {session_id}")
    print()
    
    endpoint = "http://localhost:8000/api/v1/orders"
    
    try:
        response = requests.post(
            endpoint,
            json=order_data,
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ SUCCESS! Order created successfully")
            result = response.json()
            print("\nOrder Details:")
            print(f"  Order ID: {result.get('id')}")
            print(f"  Total Price: ${result.get('total_price')}")
            print(f"  Total Calories: {result.get('total_calories')}")
            print(f"  Status: {result.get('status')}")
            print(f"  Items Count: {len(result.get('items', []))}")
            print(f"  Session ID: {result.get('session_id')}")
            
            return True
            
        else:
            print("❌ FAILED")
            error = response.json()
            print("Error:")
            print(json.dumps(error, indent=2))
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Server not running")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def generate_curl_command():
    """Generate curl command for the exact request"""
    
    order_data = {
        "machine_id": "c2d72758-ad10-4906-bea7-5b44530f036a",
        "total_price": 15.75,
        "ingredients": [
            {
                "ingredient_id": "03358de9-e462-4549-ad88-37701bbe7f73",
                "grams_used": 40
            },
            {
                "ingredient_id": "b028ed10-419c-4fe4-9ec9-0f206cf58cff",
                "grams_used": 35
            },
            {
                "ingredient_id": "d60fdcf9-b25c-4c7e-98be-85de96b58f1d",
                "grams_used": 35
            }
        ],
        "addons": []
    }
    
    print("\n" + "=" * 60)
    print("CURL COMMAND")
    print("=" * 60)
    
    curl_command = f"""curl -X POST "http://localhost:8000/api/v1/orders?session_id=ui-test-session-001" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(order_data)}'"""
    
    print(curl_command)
    

def main():
    print("Testing Order Creation with UI-Calculated Total Price")
    print("=" * 60)
    
    success = test_user_order_request()
    generate_curl_command()
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if success:
        print("✅ Test PASSED - Order creation is working!")
        print("\nThe UI should now:")
        print("1. Calculate total_price based on ingredients + addons")
        print("2. Include total_price in the request body")
        print("3. Send the order to the API")
        print("4. Handle the response with order details")
    else:
        print("❌ Test FAILED - Check server logs for details")
        print("\nNext steps:")
        print("1. Make sure the FastAPI server is running")
        print("2. Check that the machine and ingredients exist in DB")
        print("3. Review server logs for specific errors")


if __name__ == "__main__":
    main()
