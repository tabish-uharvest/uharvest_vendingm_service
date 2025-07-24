#!/usr/bin/env python3
"""
Simple test for order status update after fixing the greenlet spawn issue
"""

import requests
import json

def test_order_status_update_simple():
    """Test the simplified order status update"""
    
    # Use an existing order ID or create one first
    order_id = "101bc4e8-9c55-4a35-a701-496ab68604a2"  # Replace with actual order ID
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("TESTING SIMPLIFIED ORDER STATUS UPDATE")
    print("=" * 60)
    print(f"Order ID: {order_id}")
    
    # Test data - minimal request
    test_data = {
        "status": "completed"
    }
    
    print("Request Data:")
    print(json.dumps(test_data, indent=2))
    print()
    
    try:
        # Update order status
        response = requests.put(
            f"{base_url}/api/v1/orders/{order_id}/status",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS - Order status updated!")
            result = response.json()
            print(f"Updated Status: {result.get('status')}")
            print(f"Order ID: {result.get('id')}")
            print(f"Total Price: ${result.get('total_price')}")
            print(f"Machine ID: {result.get('machine_id')}")
            print(f"Items Count: {len(result.get('items', []))}")
            
        elif response.status_code == 404:
            print("❌ Order not found")
            print("Make sure the order ID exists in the database")
            
        elif response.status_code == 422:
            print("❌ Validation error")
            error_data = response.json()
            print(json.dumps(error_data, indent=2))
            
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


def test_different_statuses():
    """Test updating to different statuses"""
    
    order_id = "101bc4e8-9c55-4a35-a701-496ab68604a2"
    base_url = "http://localhost:8000"
    
    statuses_to_test = [
        "processing",
        "completed", 
        "failed",
        "cancelled"
    ]
    
    print("\n" + "=" * 60)
    print("TESTING DIFFERENT STATUS UPDATES")
    print("=" * 60)
    
    for status in statuses_to_test:
        print(f"\nTesting status: {status}")
        print("-" * 30)
        
        test_data = {"status": status}
        
        try:
            response = requests.put(
                f"{base_url}/api/v1/orders/{order_id}/status",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS - Status updated to: {result.get('status')}")
            else:
                print(f"❌ Error {response.status_code}")
                try:
                    error = response.json()
                    print(f"   {error.get('detail', 'Unknown error')}")
                except:
                    print(f"   {response.text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_order_status_update_simple()
    
    # Ask user if they want to test different statuses
    response = input("\nDo you want to test different statuses? (y/n): ").strip().lower()
    if response == 'y':
        test_different_statuses()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ Simplified the order status update process")
    print("✅ Removed complex transaction handling")
    print("✅ Direct database update with session.flush()")
    print("✅ Proper error handling and validation")
    print()
    print("If you still get the greenlet_spawn error, it might be:")
    print("• Database connection configuration issue")
    print("• SQLAlchemy version compatibility issue")
    print("• Async event loop issue in the FastAPI app")
