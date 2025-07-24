#!/usr/bin/env python3
"""
Test script for threshold update endpoint
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_threshold_update():
    """Test the threshold update endpoint with correct format"""
    
    # Correct format: wrap the array in an object with 'items' property
    threshold_data = {
        "items": [
            {
                "item_id": "3a0b1590-8601-4925-bb00-21f1fb24bfc5",
                "item_type": "ingredient", 
                "threshold": 400
            }
        ]
    }
    
    print("Testing threshold update endpoint...")
    print(f"Request URL: {BASE_URL}/admin/inventory/thresholds")
    print(f"Request body: {json.dumps(threshold_data, indent=2)}")
    
    try:
        response = requests.put(
            f"{BASE_URL}/admin/inventory/thresholds",
            json=threshold_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Threshold update successful!")
        else:
            print("❌ Threshold update failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_multiple_thresholds():
    """Test updating multiple thresholds at once"""
    
    threshold_data = {
        "items": [
            {
                "item_id": "3a0b1590-8601-4925-bb00-21f1fb24bfc5",
                "item_type": "ingredient",
                "threshold": 400
            },
            {
                "item_id": "another-ingredient-id-here",
                "item_type": "ingredient", 
                "threshold": 300
            },
            {
                "item_id": "some-addon-id-here",
                "item_type": "addon",
                "threshold": 50
            }
        ]
    }
    
    print("\nTesting multiple threshold updates...")
    print(f"Request URL: {BASE_URL}/admin/inventory/thresholds")
    print(f"Request body: {json.dumps(threshold_data, indent=2)}")
    
    try:
        response = requests.put(
            f"{BASE_URL}/admin/inventory/thresholds",
            json=threshold_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_threshold_update()
    test_multiple_thresholds()
