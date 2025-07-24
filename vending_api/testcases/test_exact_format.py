#!/usr/bin/env python3
"""
Test the exact order creation format as requested by user
"""

import requests
import json

def test_exact_order_format():
    """Test with the exact format the user wants"""
    
    # Exact format based on user's database schema
    order_data = {
        # Main order fields (from orders table)
        "machine_id": "c2d72758-ad10-4906-bea7-5b44530f036a",
        "total_price": 15.75,    # UI calculated
        "total_calories": 245,   # UI calculated  
        "status": "processing",  # UI provided
        "session_id": "ui-test-session-001",  # UI provided
        
        # Order items (from order_items table)
        "ingredients": [
            {
                "ingredient_id": "03358de9-e462-4549-ad88-37701bbe7f73",
                "grams_used": 40,     # UI provided
                "calories": 80        # UI calculated per ingredient
            },
            {
                "ingredient_id": "b028ed10-419c-4fe4-9ec9-0f206cf58cff",
                "grams_used": 35,     # UI provided
                "calories": 70        # UI calculated per ingredient
            },
            {
                "ingredient_id": "d60fdcf9-b25c-4c7e-98be-85de96b58f1d",
                "grams_used": 35,     # UI provided
                "calories": 95        # UI calculated per ingredient
            }
        ],
        
        # Order addons (from order_addons table) - empty for this test
        "addons": []
    }
    
    print("=" * 60)
    print("TESTING EXACT ORDER FORMAT")
    print("=" * 60)
    print("Request Body:")
    print(json.dumps(order_data, indent=2))
    print()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/orders",
            json=order_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print("Response:")
        
        if response.status_code == 201:
            print("✅ SUCCESS!")
            result = response.json()
            print(json.dumps(result, indent=2, default=str))
        else:
            print("❌ FAILED")
            try:
                error = response.json()
                print(json.dumps(error, indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"Error: {e}")

def test_with_addons():
    """Test with addons included"""
    
    order_data = {
        "machine_id": "c2d72758-ad10-4906-bea7-5b44530f036a",
        "total_price": 18.50,
        "total_calories": 285,
        "status": "processing",
        "session_id": "addon-test-session",
        "ingredients": [
            {
                "ingredient_id": "03358de9-e462-4549-ad88-37701bbe7f73",
                "grams_used": 40,
                "calories": 80
            }
        ],
        "addons": [
            {
                "addon_id": "550e8400-e29b-41d4-a716-446655440001",  # Sample addon ID
                "qty": 2,
                "calories": 40  # UI calculated (2 * 20 calories per addon)
            }
        ]
    }
    
    print("\n" + "=" * 60)
    print("TESTING WITH ADDONS")
    print("=" * 60)
    print("Request Body:")
    print(json.dumps(order_data, indent=2))
    print()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/orders",
            json=order_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ SUCCESS with addons!")
            result = response.json()
            print(f"Order ID: {result.get('id')}")
            print(f"Total Price: ${result.get('total_price')}")
            print(f"Total Calories: {result.get('total_calories')}")
            print(f"Items: {len(result.get('items', []))}")
            print(f"Addons: {len(result.get('addons', []))}")
        else:
            print("❌ FAILED with addons")
            try:
                error = response.json()
                print(json.dumps(error, indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_exact_order_format()
    test_with_addons()
    
    print("\n" + "=" * 60)
    print("CURL COMMANDS")
    print("=" * 60)
    
    basic_order = {
        "machine_id": "c2d72758-ad10-4906-bea7-5b44530f036a",
        "total_price": 15.75,
        "total_calories": 245,
        "status": "processing",
        "session_id": "curl-test",
        "ingredients": [
            {"ingredient_id": "03358de9-e462-4549-ad88-37701bbe7f73", "grams_used": 40, "calories": 80},
            {"ingredient_id": "b028ed10-419c-4fe4-9ec9-0f206cf58cff", "grams_used": 35, "calories": 70},
            {"ingredient_id": "d60fdcf9-b25c-4c7e-98be-85de96b58f1d", "grams_used": 35, "calories": 95}
        ],
        "addons": []
    }
    
    print(f"""curl -X POST "http://localhost:8000/api/v1/orders" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(basic_order)}'""")
