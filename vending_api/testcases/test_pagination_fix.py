#!/usr/bin/env python3
"""
Test script for pagination fix in admin product endpoints
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_ingredients_pagination():
    """Test the admin ingredients pagination fix"""
    
    print("Testing admin ingredients pagination fix...")
    print(f"Request URL: {BASE_URL}/admin/ingredients?skip=0&limit=50&search=Avocado")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/ingredients",
            params={
                "skip": 0,
                "limit": 50,
                "search": "Avocado"
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Body: {json.dumps(data, indent=2, default=str)}")
            
            # Check if pagination fields are present
            required_fields = ['items', 'total', 'page', 'size', 'pages']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Admin ingredients pagination working! All required fields present.")
                print(f"   - Total items: {data['total']}")
                print(f"   - Page: {data['page']}")
                print(f"   - Size: {data['size']}")
                print(f"   - Total pages: {data['pages']}")
                print(f"   - Items found: {len(data['items'])}")
            else:
                print(f"❌ Missing fields: {missing_fields}")
        else:
            print("❌ Admin ingredients endpoint failed!")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_addons_pagination():
    """Test the admin addons pagination"""
    
    print("\nTesting admin addons pagination...")
    print(f"Request URL: {BASE_URL}/admin/addons?skip=0&limit=10")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/addons",
            params={
                "skip": 0,
                "limit": 10
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Body: {json.dumps(data, indent=2, default=str)}")
            
            # Check if pagination fields are present
            required_fields = ['items', 'total', 'page', 'size', 'pages']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Admin addons pagination working!")
            else:
                print(f"❌ Missing fields: {missing_fields}")
        else:
            print("❌ Admin addons endpoint failed!")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_presets_pagination():
    """Test the admin presets pagination"""
    
    print("\nTesting admin presets pagination...")
    print(f"Request URL: {BASE_URL}/admin/presets?skip=0&limit=10")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/presets",
            params={
                "skip": 0,
                "limit": 10
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Body: {json.dumps(data, indent=2, default=str)}")
            
            # Check if pagination fields are present
            required_fields = ['items', 'total', 'page', 'size', 'pages']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Admin presets pagination working!")
            else:
                print(f"❌ Missing fields: {missing_fields}")
        else:
            print("❌ Admin presets endpoint failed!")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ingredients_pagination()
    test_addons_pagination() 
    test_presets_pagination()
