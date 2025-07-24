#!/usr/bin/env python3
"""
Test the machine orders endpoint after fixing the greenlet spawn issue
"""

import requests
import json

def test_machine_orders_endpoint():
    """Test the machine orders endpoint"""
    
    machine_id = "c2d72758-ad10-4906-bea7-5b44530f036a"
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("TESTING MACHINE ORDERS ENDPOINT")
    print("=" * 60)
    print(f"Machine ID: {machine_id}")
    
    # Test with different parameters
    test_cases = [
        {
            "name": "Basic request (skip=0, limit=20)",
            "params": {"skip": 0, "limit": 20}
        },
        {
            "name": "Smaller limit (skip=0, limit=5)",
            "params": {"skip": 0, "limit": 5}
        },
        {
            "name": "With status filter (completed orders)",
            "params": {"skip": 0, "limit": 10, "status": "completed"}
        },
        {
            "name": "With status filter (processing orders)",
            "params": {"skip": 0, "limit": 10, "status": "processing"}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)
        
        endpoint = f"{base_url}/api/v1/machines/{machine_id}/orders"
        
        print(f"URL: {endpoint}")
        print(f"Params: {test_case['params']}")
        
        try:
            response = requests.get(
                endpoint,
                params=test_case['params'],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                orders = response.json()
                print(f"✅ SUCCESS - Retrieved {len(orders)} orders")
                
                if orders:
                    print("Sample order data:")
                    sample_order = orders[0]
                    print(f"  Order ID: {sample_order.get('id')}")
                    print(f"  Status: {sample_order.get('status')}")
                    print(f"  Total Price: ${sample_order.get('total_price')}")
                    print(f"  Items Count: {len(sample_order.get('items', []))}")
                    print(f"  Created At: {sample_order.get('created_at')}")
                else:
                    print("  No orders found for this machine")
                    
            else:
                print("❌ ERROR")
                try:
                    error_data = response.json()
                    print("Error Details:")
                    print(json.dumps(error_data, indent=2))
                except:
                    print("Raw error response:")
                    print(response.text)
                    
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error")
            print("Make sure the FastAPI server is running on http://localhost:8000")
            break
            
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")


def test_order_status_update():
    """Test order status update as well"""
    
    print("\n" + "=" * 60)
    print("TESTING ORDER STATUS UPDATE")
    print("=" * 60)
    
    # This assumes we have an order to update
    order_id = "101bc4e8-9c55-4a35-a701-496ab68604a2"  # Replace with actual order ID
    base_url = "http://localhost:8000"
    
    test_data = {"status": "completed"}
    
    try:
        response = requests.put(
            f"{base_url}/api/v1/orders/{order_id}/status",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Update Response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS - Status updated to: {result.get('status')}")
        else:
            print("❌ ERROR")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_machine_orders_endpoint()
    test_order_status_update()
    
    print("\n" + "=" * 60)
    print("SUMMARY OF FIXES")
    print("=" * 60)
    print("✅ Added eager loading for all relationships in order queries")
    print("✅ Improved error handling in order response conversion")
    print("✅ Added safe attribute access to prevent None reference errors")
    print("✅ Enabled autoflush in SQLAlchemy session configuration")
    print("✅ Added fallback responses to prevent complete failures")
    print()
    print("If you still get greenlet_spawn errors, the issue might be:")
    print("• SQLAlchemy version compatibility")
    print("• Database driver version")
    print("• Event loop configuration in FastAPI")
    print("• PostgreSQL async driver (asyncpg) version")
