#!/usr/bin/env python3
"""
Test script to verify that preset creation with ingredients works after fixing the schema and service
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1/admin"

def test_preset_creation():
    """Test preset creation with ingredients"""
    print("🧪 Testing Preset Creation with Ingredients...")
    
    # First, let's get an ingredient ID to use in our test
    print("  📋 Getting available ingredients...")
    try:
        response = requests.get(f"{BASE_URL}/ingredients")
        if response.status_code == 200:
            ingredients_data = response.json()
            if ingredients_data.get('items') and len(ingredients_data['items']) > 0:
                ingredient_id = ingredients_data['items'][0]['id']
                ingredient_name = ingredients_data['items'][0]['name']
                print(f"    ✅ Found ingredient: {ingredient_name} (ID: {ingredient_id})")
            else:
                print("    ❌ No ingredients found")
                return False
        else:
            print(f"    ❌ Failed to get ingredients: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ Error getting ingredients: {e}")
        return False
    
    # Test create preset with corrected field name
    print("  📝 Testing preset create with ingredients...")
    create_data = {
        "name": "Test Complete Salad",
        "category": "salad",
        "price": 12.50,
        "calories": 180,
        "description": "A complete test salad with ingredients",
        "image": "/images/test-salad.png",
        "ingredients": [
            {
                "ingredient_id": ingredient_id,
                "grams_used": 150,
                "percent": 80  # Changed from "percentage" to "percent"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/presets", json=create_data)
        if response.status_code == 201:
            preset = response.json()
            preset_id = preset['id']
            print(f"    ✅ Create successful: {preset['name']} (ID: {preset_id})")
            print(f"    📊 Ingredients count: {len(preset.get('ingredients', []))}")
            
            if preset.get('ingredients'):
                for ing in preset['ingredients']:
                    print(f"        - {ing['ingredient_name']}: {ing['grams_used']}g ({ing['percent']}%)")
            
            # Cleanup
            print("  🗑️  Cleaning up...")
            delete_response = requests.delete(f"{BASE_URL}/presets/{preset_id}")
            if delete_response.status_code == 204:
                print("    ✅ Delete successful")
            else:
                print(f"    ⚠️  Delete failed: {delete_response.status_code}")
                
            return True
        else:
            print(f"    ❌ Create failed: {response.status_code}")
            try:
                error_details = response.json()
                print(f"    📄 Error details: {json.dumps(error_details, indent=2)}")
            except:
                print(f"    📄 Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def test_simple_preset_creation():
    """Test simple preset creation without ingredients for comparison"""
    print("\n🧪 Testing Simple Preset Creation (no ingredients)...")
    
    create_data = {
        "name": "Simple Test Preset",
        "category": "smoothie",
        "price": 8.99,
        "calories": 120,
        "description": "A simple test preset",
        "ingredients": []  # Empty ingredients array
    }
    
    try:
        response = requests.post(f"{BASE_URL}/presets", json=create_data)
        if response.status_code == 201:
            preset = response.json()
            preset_id = preset['id']
            print(f"    ✅ Create successful: {preset['name']} (ID: {preset_id})")
            
            # Cleanup
            print("  🗑️  Cleaning up...")
            delete_response = requests.delete(f"{BASE_URL}/presets/{preset_id}")
            if delete_response.status_code == 204:
                print("    ✅ Delete successful")
            else:
                print(f"    ⚠️  Delete failed: {delete_response.status_code}")
                
            return True
        else:
            print(f"    ❌ Create failed: {response.status_code}")
            try:
                error_details = response.json()
                print(f"    📄 Error details: {json.dumps(error_details, indent=2)}")
            except:
                print(f"    📄 Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def main():
    print("🚀 Testing Preset Creation After Schema and Service Fixes\n")
    
    # Test server connectivity
    try:
        response = requests.get(f"{BASE_URL}/presets")
        if response.status_code != 200:
            print(f"❌ Server not accessible: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        sys.exit(1)
    
    print("✅ Server is accessible")
    
    # Run tests
    success1 = test_simple_preset_creation()
    success2 = test_preset_creation()
    
    if success1 and success2:
        print("\n🎉 All preset creation tests passed!")
    else:
        print("\n⚠️  Some tests failed - check logs above")

if __name__ == "__main__":
    main()
