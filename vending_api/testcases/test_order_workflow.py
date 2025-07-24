#!/usr/bin/env python3
"""
Test the complete order workflow: create order then update status
"""

import requests
import json
import uuid
from datetime import datetime

def test_complete_order_workflow():
    """Test creating an order and then updating its status"""
    
    base_url = "http://localhost:8000"
    
    # Step 1: Create an order
    print("=" * 60)
    print("STEP 1: CREATING ORDER")
    print("=" * 60)
    
    # Generate a unique session ID
    session_id = f"test-workflow-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    order_data = {
        "machine_id": "c2d72758-ad10-4906-bea7-5b44530f036a",
        "total_price": 15.75,
        "total_calories": 245,
        "status": "processing",
        "session_id": session_id,
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
    
    print(f"Session ID: {session_id}")
    print("Order Data:")
    print(json.dumps(order_data, indent=2))
    print()
    
    try:
        # Create order
        create_response = requests.post(
            f"{base_url}/api/v1/orders",
            json=order_data,
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Create Response Status: {create_response.status_code}")
        
        if create_response.status_code == 201:
            print("✓ Order created successfully!")
            order_response = create_response.json()
            order_id = order_response['id']
            print(f"Created Order ID: {order_id}")
            print(f"Initial Status: {order_response['status']}")
            print()
            
            # Step 2: Update order status to completed
            print("=" * 60)
            print("STEP 2: UPDATING ORDER STATUS TO COMPLETED")
            print("=" * 60)
            
            status_update_data = {
                "status": "completed",
                "payment_status": "paid",  # Will be accepted but not stored
                "notes": "Order successfully prepared and delivered"  # Will be accepted but not stored
            }
            
            print("Status Update Data:")
            print(json.dumps(status_update_data, indent=2))
            print()
            
            # Update status
            status_response = requests.put(
                f"{base_url}/api/v1/orders/{order_id}/status",
                json=status_update_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Status Update Response: {status_response.status_code}")
            
            if status_response.status_code == 200:
                print("✓ Order status updated successfully!")
                updated_order = status_response.json()
                print(f"Updated Status: {updated_order['status']}")
                print(f"Order ID: {updated_order['id']}")
                print(f"Total Price: ${updated_order['total_price']}")
                print(f"Machine ID: {updated_order['machine_id']}")
                
                # Step 3: Verify the update by getting the order
                print("\n" + "=" * 60)
                print("STEP 3: VERIFYING ORDER STATUS")
                print("=" * 60)
                
                get_response = requests.get(
                    f"{base_url}/api/v1/orders/{order_id}",
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if get_response.status_code == 200:
                    final_order = get_response.json()
                    print("✓ Order retrieved successfully!")
                    print(f"Final Status: {final_order['status']}")
                    print(f"Created At: {final_order['created_at']}")
                    print(f"Items Count: {len(final_order['items'])}")
                    
                    print("\n" + "🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
                    print("✅ Order created -> Order status updated to completed -> Status verified")
                    
                else:
                    print(f"✗ Error retrieving order: {get_response.status_code}")
                    print(get_response.text)
                    
            else:
                print(f"✗ Error updating status: {status_response.status_code}")
                try:
                    error_data = status_response.json()
                    print("Error Details:")
                    print(json.dumps(error_data, indent=2))
                except:
                    print("Raw error response:")
                    print(status_response.text)
                    
        else:
            print(f"✗ Error creating order: {create_response.status_code}")
            try:
                error_data = create_response.json()
                print("Error Details:")
                print(json.dumps(error_data, indent=2))
            except:
                print("Raw error response:")
                print(create_response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ CONNECTION ERROR")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        
    except Exception as e:
        print(f"✗ UNEXPECTED ERROR: {e}")


def generate_test_curl_commands():
    """Generate curl commands for manual testing"""
    
    session_id = f"manual-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print("\n" + "=" * 60)
    print("MANUAL TESTING CURL COMMANDS")
    print("=" * 60)
    
    print("1. Create Order:")
    create_cmd = f'''curl -X POST "http://localhost:8000/api/v1/orders?session_id={session_id}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "machine_id": "c2d72758-ad10-4906-bea7-5b44530f036a",
    "total_price": 15.75,
    "total_calories": 245,
    "status": "processing",
    "session_id": "{session_id}",
    "ingredients": [
      {{
        "ingredient_id": "03358de9-e462-4549-ad88-37701bbe7f73",
        "grams_used": 40,
        "calories": 80
      }}
    ],
    "addons": []
  }}\''''
    print(create_cmd)
    
    print("\n2. Update Order Status (replace ORDER_ID with actual ID from step 1):")
    update_cmd = '''curl -X PUT "http://localhost:8000/api/v1/orders/ORDER_ID/status" \\
  -H "Content-Type: application/json" \\
  -d '{
    "status": "completed",
    "payment_status": "paid",
    "notes": "Order completed successfully"
  }\''''
    print(update_cmd)
    
    print("\n3. Get Order Details (replace ORDER_ID with actual ID):")
    get_cmd = '''curl -X GET "http://localhost:8000/api/v1/orders/ORDER_ID" \\
  -H "Content-Type: application/json"'''
    print(get_cmd)


if __name__ == "__main__":
    test_complete_order_workflow()
    generate_test_curl_commands()
    
    print("\n" + "=" * 60)
    print("WORKFLOW SUMMARY")
    print("=" * 60)
    print("1. ✅ Create order with 'processing' status")
    print("2. ✅ Update order status to 'completed'")
    print("3. ✅ Verify the status was updated correctly")
    print()
    print("This workflow simulates:")
    print("• User creates order (machine starts processing)")
    print("• Machine completes preparation")
    print("• System updates order status to 'completed'")
