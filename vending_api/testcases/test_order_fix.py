#!/usr/bin/env python3
"""
Quick test to verify order creation fix
"""

import json
from app.schemas.order import OrderCreateRequest, OrderItemRequest, OrderAddonRequest
import uuid

def test_order_creation_schema():
    """Test that order creation schema works correctly"""
    
    # Sample order data
    order_data = {
        "machine_id": "c2d72758-ad10-4906-bea7-5b44530f036a",
        "ingredients": [
            {
                "ingredient_id": "03358de9-e462-4549-ad88-37701bbe7f73",
                "grams_used": 10
            },
            {
                "ingredient_id": "b028ed10-419c-4fe4-9ec9-0f206cf58cff",
                "grams_used": 12
            },
            {
                "ingredient_id": "e02995f0-de4a-4f37-91a5-db7fff6771f0",
                "grams_used": 13
            }
        ],
        "addons": []
    }
    
    try:
        # Create OrderCreateRequest from dict
        order_request = OrderCreateRequest(**order_data)
        print("✓ OrderCreateRequest creation successful")
        print(f"Machine ID: {order_request.machine_id}")
        print(f"Ingredients count: {len(order_request.ingredients)}")
        print(f"Addons count: {len(order_request.addons)}")
        
        # Test conversion to dict
        ingredients_dict = [item.dict() for item in order_request.ingredients]
        addons_dict = [addon.dict() for addon in order_request.addons]
        
        print("✓ Conversion to dictionaries successful")
        print(f"Ingredients dict: {ingredients_dict}")
        print(f"Addons dict: {addons_dict}")
        
        # Test accessing fields both ways
        for ingredient in order_request.ingredients:
            ingredient_id = ingredient.ingredient_id if hasattr(ingredient, 'ingredient_id') else ingredient['ingredient_id']
            grams_used = ingredient.grams_used if hasattr(ingredient, 'grams_used') else ingredient['grams_used']
            print(f"Ingredient {ingredient_id}: {grams_used}g")
        
        print("✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_order_creation_schema()
