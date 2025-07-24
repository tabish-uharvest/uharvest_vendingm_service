#!/usr/bin/env python3
"""
Test script to verify that admin product CRUD operations work after fixing DAO calls
"""
import requests
import json
import sys
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1/admin"

def test_ingredient_crud():
    """Test ingredient create and update operations"""
    print("🧪 Testing Ingredient CRUD...")
    
    # Test create
    print("  📝 Testing ingredient create...")
    create_data = {
        "name": "Test Baigan",
        "emoji": "🍆",
        "min_qty_g": 50,
        "max_percent_limit": 100,
        "calories_per_g": 1,
        "price_per_gram": 0.01
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ingredients", json=create_data)
        if response.status_code == 201:
            ingredient = response.json()
            ingredient_id = ingredient['id']
            print(f"    ✅ Create successful: {ingredient['name']} (ID: {ingredient_id})")
            
            # Test update
            print("  ✏️  Testing ingredient update...")
            update_data = {
                "name": "Updated Baigan Name"
            }
            
            response = requests.put(f"{BASE_URL}/ingredients/{ingredient_id}", json=update_data)
            if response.status_code == 200:
                updated_ingredient = response.json()
                print(f"    ✅ Update successful: {updated_ingredient['name']}")
                
                # Test delete (cleanup)
                print("  🗑️  Cleaning up...")
                delete_response = requests.delete(f"{BASE_URL}/ingredients/{ingredient_id}")
                if delete_response.status_code == 204:
                    print("    ✅ Delete successful")
                else:
                    print(f"    ⚠️  Delete failed: {delete_response.status_code}")
                    
            else:
                print(f"    ❌ Update failed: {response.status_code} - {response.text}")
        else:
            print(f"    ❌ Create failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"    ❌ Error: {e}")

def test_addon_crud():
    """Test addon create and update operations"""
    print("\n🧪 Testing Addon CRUD...")
    
    # Test create
    print("  📝 Testing addon create...")
    create_data = {
        "name": "Test Sauce",
        "price": 0.50,
        "calories": 25,
        "icon": "🥫"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/addons", json=create_data)
        if response.status_code == 201:
            addon = response.json()
            addon_id = addon['id']
            print(f"    ✅ Create successful: {addon['name']} (ID: {addon_id})")
            
            # Test update
            print("  ✏️  Testing addon update...")
            update_data = {
                "name": "Updated Test Sauce",
                "price": 0.75
            }
            
            response = requests.put(f"{BASE_URL}/addons/{addon_id}", json=update_data)
            if response.status_code == 200:
                updated_addon = response.json()
                print(f"    ✅ Update successful: {updated_addon['name']} - ${updated_addon['price']}")
                
                # Test delete (cleanup)
                print("  🗑️  Cleaning up...")
                delete_response = requests.delete(f"{BASE_URL}/addons/{addon_id}")
                if delete_response.status_code == 204:
                    print("    ✅ Delete successful")
                else:
                    print(f"    ⚠️  Delete failed: {delete_response.status_code}")
                    
            else:
                print(f"    ❌ Update failed: {response.status_code} - {response.text}")
        else:
            print(f"    ❌ Create failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"    ❌ Error: {e}")

def test_preset_crud():
    """Test preset create and update operations"""
    print("\n🧪 Testing Preset CRUD...")
    
    # Test create
    print("  📝 Testing preset create...")
    create_data = {
        "name": "Test Salad",
        "category": "healthy",
        "price": 5.99,
        "calories": 150,
        "description": "A test salad preset"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/presets", json=create_data)
        if response.status_code == 201:
            preset = response.json()
            preset_id = preset['id']
            print(f"    ✅ Create successful: {preset['name']} (ID: {preset_id})")
            
            # Test update
            print("  ✏️  Testing preset update...")
            update_data = {
                "name": "Updated Test Salad",
                "price": 6.99
            }
            
            response = requests.put(f"{BASE_URL}/presets/{preset_id}", json=update_data)
            if response.status_code == 200:
                updated_preset = response.json()
                print(f"    ✅ Update successful: {updated_preset['name']} - ${updated_preset['price']}")
                
                # Test delete (cleanup)
                print("  🗑️  Cleaning up...")
                delete_response = requests.delete(f"{BASE_URL}/presets/{preset_id}")
                if delete_response.status_code == 204:
                    print("    ✅ Delete successful")
                else:
                    print(f"    ⚠️  Delete failed: {delete_response.status_code}")
                    
            else:
                print(f"    ❌ Update failed: {response.status_code} - {response.text}")
        else:
            print(f"    ❌ Create failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"    ❌ Error: {e}")

def main():
    print("🚀 Testing Admin Product CRUD Operations After DAO Fix\n")
    
    # Test server connectivity
    try:
        response = requests.get(f"{BASE_URL}/ingredients")
        if response.status_code != 200:
            print(f"❌ Server not accessible: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        sys.exit(1)
    
    print("✅ Server is accessible")
    
    # Run CRUD tests
    test_ingredient_crud()
    test_addon_crud()
    test_preset_crud()
    
    print("\n🎉 All CRUD tests completed!")

if __name__ == "__main__":
    main()
