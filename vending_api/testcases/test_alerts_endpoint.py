#!/usr/bin/env python3
"""
Test script for inventory alerts endpoint
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_inventory_alerts():
    """Test the inventory alerts endpoint"""
    
    machine_id = "c2d72758-ad10-4906-bea7-5b44530f036a"
    
    print("Testing inventory alerts endpoint...")
    print(f"Request URL: {BASE_URL}/admin/inventory/alerts?machine_id={machine_id}&skip=0&limit=100")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/inventory/alerts",
            params={
                "machine_id": machine_id,
                "skip": 0,
                "limit": 100
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Inventory alerts endpoint working!")
        else:
            print("❌ Inventory alerts endpoint failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_alerts_without_machine_filter():
    """Test alerts endpoint without machine filter"""
    
    print("\nTesting alerts endpoint without machine filter...")
    print(f"Request URL: {BASE_URL}/admin/inventory/alerts?skip=0&limit=10")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/inventory/alerts",
            params={
                "skip": 0,
                "limit": 10
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ All alerts endpoint working!")
        else:
            print("❌ All alerts endpoint failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_inventory_alerts()
    test_alerts_without_machine_filter()
