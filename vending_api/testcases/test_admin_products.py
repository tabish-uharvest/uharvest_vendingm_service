#!/usr/bin/env python3
"""
Test script for admin product endpoints
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_list_ingredients():
    """Test the admin ingredients list endpoint"""
    
    print("Testing admin ingredients list endpoint...")
    print(f"Request URL: {BASE_URL}/admin/ingredients?skip=0&limit=50&category=smoothie")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/ingredients",
            params={
                "skip": 0,
                "limit": 50,
                "category": "smoothie"
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Admin ingredients endpoint working!")
        else:
            print("❌ Admin ingredients endpoint failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_list_addons():
    """Test the admin addons list endpoint"""
    
    print("\nTesting admin addons list endpoint...")
    print(f"Request URL: {BASE_URL}/admin/addons?skip=0&limit=50")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/addons",
            params={
                "skip": 0,
                "limit": 50
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Admin addons endpoint working!")
        else:
            print("❌ Admin addons endpoint failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_list_presets():
    """Test the admin presets list endpoint"""
    
    print("\nTesting admin presets list endpoint...")
    print(f"Request URL: {BASE_URL}/admin/presets?skip=0&limit=50")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/presets",
            params={
                "skip": 0,
                "limit": 50
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Admin presets endpoint working!")
        else:
            print("❌ Admin presets endpoint failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_create_ingredient():
    """Test creating a new ingredient"""
    
    ingredient_data = {
        "name": "Test Ingredient",
        "emoji": "🥕",
        "image": "test_ingredient.jpg",
        "min_qty_g": 50,
        "max_percent_limit": 30,
        "calories_per_g": 2.5,
        "price_per_gram": 0.05
    }
    
    print("\nTesting create ingredient endpoint...")
    print(f"Request URL: {BASE_URL}/admin/ingredients")
    print(f"Request body: {json.dumps(ingredient_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/ingredients",
            json=ingredient_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Create ingredient endpoint working!")
            return response.json().get("id")
        else:
            print("❌ Create ingredient endpoint failed!")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_list_ingredients()
    test_list_addons()
    test_list_presets()
    test_create_ingredient()
