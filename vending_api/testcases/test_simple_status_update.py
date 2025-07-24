#!/usr/bin/env python3
"""
Simple test for order status update after removing payment_status and notes fields
"""

import requests
import json

def test_order_status_update():
    """Test the order status update endpoint"""
    
    order_id = "101bc4e8-9c55-4a35-a701-496ab68604a2"
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/orders/{order_id}/status"
    
    # Test data - only status is required, other fields will be ignored
    test_data = {
        "status": "completed",
        "payment_status": "paid",  # This will be accepted but not stored
        "notes": "Order successfully prepared and delivered"  # This will be accepted but not stored
    }
    
    print("=" * 60)
    print("TESTING ORDER STATUS UPDATE (SIMPLIFIED)")
    print("=" * 60)
    print(f"Order ID: {order_id}")
    print(f"Endpoint: {endpoint}")
    print()
    print("Request Data:")
    print(json.dumps(test_data, indent=2))
    print()
    
    try:
        response = requests.put(
            endpoint,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ SUCCESS - Order status updated!")
            response_data = response.json()
            print("Updated Order:")
            print(f"  Status: {response_data.get('status')}")
            print(f"  Total Price: ${response_data.get('total_price')}")
            print(f"  Machine ID: {response_data.get('machine_id')}")
            if 'items' in response_data:
                print(f"  Items Count: {len(response_data['items'])}")
            print()
            
        elif response.status_code == 404:
            print("✗ ORDER NOT FOUND")
            print("The order ID does not exist in the database.")
            
        elif response.status_code == 422:
            print("✗ VALIDATION ERROR")
            error_data = response.json()
            print("Error Details:")
            print(json.dumps(error_data, indent=2))
            
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
        
    except Exception as e:
        print(f"✗ UNEXPECTED ERROR: {e}")

def test_simple_status_update():
    """Test with only the status field"""
    
    order_id = "101bc4e8-9c55-4a35-a701-496ab68604a2"
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/orders/{order_id}/status"
    
    # Minimal test data - only status
    test_data = {
        "status": "completed"
    }
    
    print("\n" + "=" * 60)
    print("TESTING SIMPLE STATUS UPDATE (STATUS ONLY)")
    print("=" * 60)
    print(f"Order ID: {order_id}")
    print("Request Data:")
    print(json.dumps(test_data, indent=2))
    print()
    
    try:
        response = requests.put(
            endpoint,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ SUCCESS - Order status updated!")
            response_data = response.json()
            print(f"New Status: {response_data.get('status')}")
        else:
            print(f"✗ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_order_status_update()
    test_simple_status_update()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("• payment_status and notes fields have been removed from the Order model")
    print("• They are still accepted in the API request but are not stored")
    print("• Only the status field is actually updated in the database")
    print("• This maintains API compatibility while simplifying the data model")
