#!/usr/bin/env python3
"""
Test script for Order Creation API
Demonstrates various order creation scenarios with sample data
"""

import asyncio
import uuid
import json
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional

# Import the actual API components for testing
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.schemas.order import OrderCreateRequest, OrderItemRequest, OrderAddonRequest
from app.services.order_service import OrderService
from app.config.database import get_async_db


class OrderCreationTester:
    """Test class for order creation scenarios"""
    
    def __init__(self):
        self.order_service = OrderService()
        
    async def test_basic_smoothie_order(self) -> Dict[str, Any]:
        """Test creating a basic smoothie order"""
        print("\n=== Testing Basic Smoothie Order ===")
        
        # Sample UUIDs (in real scenarios, these would come from the database)
        machine_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        
        order_request = OrderCreateRequest(
            machine_id=machine_id,
            ingredients=[
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),
                    grams_used=200  # Banana
                ),
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440002"), 
                    grams_used=150  # Strawberry
                ),
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440003"),
                    grams_used=100  # Yogurt
                )
            ],
            addons=[
                OrderAddonRequest(
                    addon_id=uuid.UUID("660e8400-e29b-41d4-a716-446655440001"),
                    qty=1  # Protein powder
                )
            ]
        )
        
        session_id = f"test-smoothie-{uuid.uuid4().hex[:8]}"
        
        print(f"Session ID: {session_id}")
        print("Order Request:")
        print(json.dumps(order_request.dict(), indent=2, default=str))
        
        return {
            "test_name": "basic_smoothie_order",
            "session_id": session_id,
            "order_request": order_request,
            "description": "3 ingredients (banana, strawberry, yogurt) + protein powder"
        }

    async def test_salad_order(self) -> Dict[str, Any]:
        """Test creating a salad order with multiple addons"""
        print("\n=== Testing Salad Order ===")
        
        machine_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        
        order_request = OrderCreateRequest(
            machine_id=machine_id,
            ingredients=[
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440010"),
                    grams_used=100  # Mixed greens
                ),
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440011"),
                    grams_used=80   # Cherry tomatoes
                ),
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440012"),
                    grams_used=50   # Cucumber
                ),
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440013"),
                    grams_used=30   # Red onion
                )
            ],
            addons=[
                OrderAddonRequest(
                    addon_id=uuid.UUID("660e8400-e29b-41d4-a716-446655440010"),
                    qty=2  # Croutons (double portion)
                ),
                OrderAddonRequest(
                    addon_id=uuid.UUID("660e8400-e29b-41d4-a716-446655440011"),
                    qty=1  # Caesar dressing
                )
            ]
        )
        
        session_id = f"test-salad-{uuid.uuid4().hex[:8]}"
        
        print(f"Session ID: {session_id}")
        print("Order Request:")
        print(json.dumps(order_request.dict(), indent=2, default=str))
        
        return {
            "test_name": "salad_order",
            "session_id": session_id,
            "order_request": order_request,
            "description": "4 ingredients (greens, tomatoes, cucumber, onion) + croutons + dressing"
        }

    async def test_minimal_order(self) -> Dict[str, Any]:
        """Test creating a minimal order with single ingredient"""
        print("\n=== Testing Minimal Order ===")
        
        machine_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        
        order_request = OrderCreateRequest(
            machine_id=machine_id,
            ingredients=[
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),
                    grams_used=250  # Just banana
                )
            ],
            addons=[]  # No addons
        )
        
        session_id = f"test-minimal-{uuid.uuid4().hex[:8]}"
        
        print(f"Session ID: {session_id}")
        print("Order Request:")
        print(json.dumps(order_request.dict(), indent=2, default=str))
        
        return {
            "test_name": "minimal_order",
            "session_id": session_id,
            "order_request": order_request,
            "description": "Single ingredient (banana), no addons"
        }

    async def test_complex_order(self) -> Dict[str, Any]:
        """Test creating a complex order with many ingredients and addons"""
        print("\n=== Testing Complex Order ===")
        
        machine_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        
        order_request = OrderCreateRequest(
            machine_id=machine_id,
            ingredients=[
                # Smoothie base
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),
                    grams_used=150  # Banana
                ),
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440002"),
                    grams_used=100  # Strawberry
                ),
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440004"),
                    grams_used=120  # Mango
                ),
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440005"),
                    grams_used=80   # Blueberry
                ),
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440003"),
                    grams_used=100  # Greek yogurt
                ),
                OrderItemRequest(
                    ingredient_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440006"),
                    grams_used=50   # Spinach (green smoothie)
                )
            ],
            addons=[
                OrderAddonRequest(
                    addon_id=uuid.UUID("660e8400-e29b-41d4-a716-446655440001"),
                    qty=1  # Protein powder
                ),
                OrderAddonRequest(
                    addon_id=uuid.UUID("660e8400-e29b-41d4-a716-446655440002"),
                    qty=2  # Chia seeds (double)
                ),
                OrderAddonRequest(
                    addon_id=uuid.UUID("660e8400-e29b-41d4-a716-446655440003"),
                    qty=1  # Flax seeds
                )
            ]
        )
        
        session_id = f"test-complex-{uuid.uuid4().hex[:8]}"
        
        print(f"Session ID: {session_id}")
        print("Order Request:")
        print(json.dumps(order_request.dict(), indent=2, default=str))
        
        return {
            "test_name": "complex_order",
            "session_id": session_id,
            "order_request": order_request,
            "description": "6 ingredients (multi-fruit green smoothie) + 3 addons"
        }

    def generate_curl_commands(self, test_cases: list) -> None:
        """Generate curl commands for testing"""
        print("\n" + "="*60)
        print("CURL COMMANDS FOR TESTING")
        print("="*60)
        
        base_url = "http://localhost:8000/api"
        
        for test_case in test_cases:
            print(f"\n# {test_case['description']}")
            print(f"# Test: {test_case['test_name']}")
            
            # Multi-machine endpoint
            order_json = json.dumps(test_case['order_request'].dict(), default=str)
            print(f"curl -X POST \"{base_url}/orders?session_id={test_case['session_id']}\" \\")
            print(f"  -H \"Content-Type: application/json\" \\")
            print(f"  -d '{order_json}'")
            
            # Single-machine endpoint (without machine_id)
            single_machine_data = test_case['order_request'].dict()
            single_machine_data.pop('machine_id', None)
            single_machine_json = json.dumps(single_machine_data, default=str)
            print(f"\n# Same order for single-machine mode:")
            print(f"curl -X POST \"{base_url}/machine/orders?session_id={test_case['session_id']}-single\" \\")
            print(f"  -H \"Content-Type: application/json\" \\")
            print(f"  -d '{single_machine_json}'")

    def generate_python_examples(self, test_cases: list) -> None:
        """Generate Python code examples"""
        print("\n" + "="*60)
        print("PYTHON REQUESTS EXAMPLES")
        print("="*60)
        
        print("""
import requests
import uuid
import json

base_url = "http://localhost:8000/api"

""")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"# Example {i}: {test_case['description']}")
            print(f"def create_{test_case['test_name']}():")
            print(f"    session_id = \"{test_case['session_id']}\"")
            print(f"    ")
            order_dict = test_case['order_request'].dict()
            print(f"    order_data = {json.dumps(order_dict, indent=8, default=str)}")
            print(f"    ")
            print(f"    response = requests.post(")
            print(f"        f\"{{base_url}}/orders?session_id={{session_id}}\",")
            print(f"        json=order_data")
            print(f"    )")
            print(f"    ")
            print(f"    if response.status_code == 201:")
            print(f"        order = response.json()")
            print(f"        print(f\"Order created: {{order['id']}}\")")
            print(f"        print(f\"Total: ${{order['total_price']}}\")")
            print(f"        print(f\"Calories: {{order['total_calories']}}\")")
            print(f"        return order")
            print(f"    else:")
            print(f"        print(f\"Error: {{response.status_code}} - {{response.text}}\")")
            print(f"        return None")
            print()

    async def generate_all_examples(self) -> None:
        """Generate all test examples"""
        print("URBAN HARVEST VENDING MACHINE - ORDER CREATION EXAMPLES")
        print("="*60)
        
        # Generate test cases
        test_cases = []
        test_cases.append(await self.test_basic_smoothie_order())
        test_cases.append(await self.test_salad_order()) 
        test_cases.append(await self.test_minimal_order())
        test_cases.append(await self.test_complex_order())
        
        # Generate curl commands
        self.generate_curl_commands(test_cases)
        
        # Generate Python examples
        self.generate_python_examples(test_cases)
        
        # Generate validation examples
        print("\n" + "="*60)
        print("VALIDATION EXAMPLES")
        print("="*60)
        
        print("""
# Examples of validation errors:

# 1. Invalid ingredient_id (non-existent UUID)
{
  "machine_id": "123e4567-e89b-12d3-a456-426614174000",
  "ingredients": [
    {
      "ingredient_id": "00000000-0000-0000-0000-000000000000",  # Invalid
      "grams_used": 200
    }
  ]
}
# Expected: 422 - "Ingredient 00000000-0000-0000-0000-000000000000 not found"

# 2. Invalid grams_used (too high)
{
  "machine_id": "123e4567-e89b-12d3-a456-426614174000", 
  "ingredients": [
    {
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440001",
      "grams_used": 1500  # Over 1000 limit
    }
  ]
}
# Expected: 422 - Validation error

# 3. Too many ingredients (over 20)
{
  "machine_id": "123e4567-e89b-12d3-a456-426614174000",
  "ingredients": [
    # ... 21 ingredients ...
  ]
}
# Expected: 422 - "max_items=20"

# 4. No ingredients
{
  "machine_id": "123e4567-e89b-12d3-a456-426614174000",
  "ingredients": []
}
# Expected: 422 - "min_items=1"
""")

    def print_schema_reference(self) -> None:
        """Print schema reference"""
        print("\n" + "="*60)
        print("SCHEMA REFERENCE")
        print("="*60)
        
        print("""
OrderCreateRequest:
├── machine_id: UUID (required)
├── ingredients: List[OrderItemRequest] (1-20 items)
│   ├── ingredient_id: UUID (required)
│   └── grams_used: int (1-1000, required)
└── addons: List[OrderAddonRequest] (0-10 items)
    ├── addon_id: UUID (required)
    └── qty: int (1-10, optional, default=1)

OrderResponse:
├── id: UUID
├── machine_id: UUID
├── machine_location: string
├── user_id: UUID (nullable)
├── session_id: string (nullable)
├── status: string (processing|completed|failed|cancelled)
├── total_price: Decimal
├── total_calories: int
├── created_at: datetime
├── items: List[OrderItemResponse]
│   ├── id: UUID
│   ├── ingredient_id: UUID
│   ├── ingredient_name: string
│   ├── ingredient_emoji: string
│   ├── qty_ml: int
│   ├── grams_used: int
│   └── calories: int
└── addons: List[OrderAddonResponse]
    ├── id: UUID
    ├── addon_id: UUID
    ├── addon_name: string
    ├── addon_icon: string
    ├── qty: int
    └── calories: int
""")


async def main():
    """Main function to run all examples"""
    tester = OrderCreationTester()
    await tester.generate_all_examples()
    tester.print_schema_reference()
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Start the FastAPI server:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

2. Ensure you have sample data in the database:
   - At least one vending machine
   - Several ingredients with valid UUIDs
   - Several addons with valid UUIDs

3. Test with the curl commands above or use the Python examples

4. Check the response format and adjust your frontend accordingly

5. Implement proper error handling for validation failures

6. Consider implementing session management in your client application
""")


if __name__ == "__main__":
    asyncio.run(main())
