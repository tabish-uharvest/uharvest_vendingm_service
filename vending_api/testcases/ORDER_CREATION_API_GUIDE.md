# Order Creation API Guide

## Overview

The Urban Harvest Vending Machine API provides two endpoints for creating orders:

1. **Multi-machine mode**: `/orders` - requires `machine_id` in the request body
2. **Single-machine mode**: `/machine/orders` - uses configured machine ID

## Order Creation Endpoints

### POST /orders
Creates an order for any machine (multi-machine deployment).

### POST /machine/orders  
Creates an order for the current configured machine (single-machine deployment).

## Required Schema

### OrderCreateRequest

```json
{
  "machine_id": "uuid",        // Required for /orders endpoint, ignored for /machine/orders
  "total_price": 15.75,        // Required: Total price calculated by UI
  "ingredients": [             // Required: 1-20 ingredients
    {
      "ingredient_id": "uuid", // Required: Valid ingredient UUID
      "grams_used": 150        // Required: 1-1000 grams
    }
  ],
  "addons": [                  // Optional: 0-10 addons
    {
      "addon_id": "uuid",      // Required: Valid addon UUID  
      "qty": 2                 // Optional: 1-10 quantity (defaults to 1)
    }
  ]
}
```

## Sample Request Bodies

### Basic Smoothie Order

```json
{
  "machine_id": "123e4567-e89b-12d3-a456-426614174000",
  "total_price": 12.50,
  "ingredients": [
    {
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440001",
      "grams_used": 200
    },
    {
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440002", 
      "grams_used": 150
    },
    {
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440003",
      "grams_used": 100
    }
  ],
  "addons": [
    {
      "addon_id": "660e8400-e29b-41d4-a716-446655440001",
      "qty": 1
    }
  ]
}
```

### Salad Order with Multiple Addons

```json
{
  "machine_id": "123e4567-e89b-12d3-a456-426614174000",
  "ingredients": [
    {
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440010",
      "grams_used": 100
    },
    {
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440011",
      "grams_used": 80
    },
    {
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440012",
      "grams_used": 50
    },
    {
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440013",
      "grams_used": 30
    }
  ],
  "addons": [
    {
      "addon_id": "660e8400-e29b-41d4-a716-446655440010",
      "qty": 2
    },
    {
      "addon_id": "660e8400-e29b-41d4-a716-446655440011",
      "qty": 1
    }
  ]
}
```

### Minimal Order (Single Ingredient)

```json
{
  "machine_id": "123e4567-e89b-12d3-a456-426614174000",
  "ingredients": [
    {
      "ingredient_id": "550e8400-e29b-41d4-a716-446655440001",
      "grams_used": 250
    }
  ],
  "addons": []
}
```

## Query Parameters

### session_id (Optional)
- **Type**: String
- **Description**: Customer session identifier for tracking
- **Usage**: `?session_id=customer-session-123`

Example:
```
POST /orders?session_id=mobile-app-session-456
```

## Session ID Usage

The `session_id` parameter serves several purposes:

### 1. Customer Journey Tracking
- Links multiple API calls to the same customer session
- Useful for analytics and customer behavior analysis
- Helps track order abandonment and completion rates

### 2. Mobile/Web App Integration
```javascript
// Example: Generate session ID on app start
const sessionId = `mobile-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

// Use in all API calls for this customer session
fetch('/api/orders', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(orderData)
} + `?session_id=${sessionId}`);
```

### 3. Order Correlation
- Allows backend to correlate orders with customer sessions
- Useful for customer support and order tracking
- Enables session-based discounts or promotions

### 4. Analytics and Reporting
```sql
-- Example: Track orders per session
SELECT session_id, COUNT(*) as order_count, SUM(total_price) as session_value
FROM orders 
WHERE session_id IS NOT NULL
GROUP BY session_id;
```

## Response Schema

### OrderResponse

```json
{
  "id": "uuid",
  "machine_id": "uuid",
  "machine_location": "string",
  "user_id": "uuid",
  "session_id": "string",
  "status": "processing|completed|failed|cancelled",
  "total_price": "decimal",
  "total_calories": 0,
  "created_at": "2023-12-07T10:30:00Z",
  "items": [
    {
      "id": "uuid",
      "ingredient_id": "uuid",
      "ingredient_name": "string",
      "ingredient_emoji": "🥬",
      "qty_ml": 0,
      "grams_used": 150,
      "calories": 30
    }
  ],
  "addons": [
    {
      "id": "uuid", 
      "addon_id": "uuid",
      "addon_name": "string",
      "addon_icon": "string",
      "qty": 1,
      "calories": 50
    }
  ]
}
```

## Order Processing Flow

1. **Validation**
   - Machine exists and is available
   - All ingredients and addons exist
   - Stock availability check
   - Quantity constraints validation

2. **Calculation**
   - Total price calculation (ingredients + addons)
   - Total calories calculation
   - Stock deduction

3. **Creation**
   - Order record creation
   - Order items creation
   - Order addons creation
   - Stock update

4. **Response**
   - Complete order details with relationships
   - Real-time pricing and calorie information

## Error Handling

### Common Error Cases

#### 404 - Machine Not Found
```json
{
  "detail": "Machine 123e4567-e89b-12d3-a456-426614174000 not found and auto-registration is disabled"
}
```

#### 422 - Validation Error
```json
{
  "detail": "Ingredient 550e8400-e29b-41d4-a716-446655440999 not found"
}
```

#### 422 - Stock Insufficient
```json
{
  "detail": "Insufficient stock for ingredient: Spinach. Available: 50g, Requested: 200g"
}
```

#### 422 - Constraint Violation
```json
{
  "detail": "grams_used must be between 1 and 1000"
}
```

## Testing Examples

### Using curl

```bash
# Basic order creation
curl -X POST "http://localhost:8000/api/orders?session_id=test-session-123" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "123e4567-e89b-12d3-a456-426614174000",
    "ingredients": [
      {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440001",
        "grams_used": 200
      }
    ],
    "addons": []
  }'

# Single-machine mode
curl -X POST "http://localhost:8000/api/machine/orders?session_id=test-session-456" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": [
      {
        "ingredient_id": "550e8400-e29b-41d4-a716-446655440001", 
        "grams_used": 150
      }
    ],
    "addons": []
  }'
```

### Using Python requests

```python
import requests
import uuid

# Generate session ID
session_id = f"python-test-{uuid.uuid4().hex[:8]}"

# Order data
order_data = {
    "machine_id": "123e4567-e89b-12d3-a456-426614174000",
    "ingredients": [
        {
            "ingredient_id": "550e8400-e29b-41d4-a716-446655440001",
            "grams_used": 200
        },
        {
            "ingredient_id": "550e8400-e29b-41d4-a716-446655440002",
            "grams_used": 150
        }
    ],
    "addons": [
        {
            "addon_id": "660e8400-e29b-41d4-a716-446655440001",
            "qty": 1
        }
    ]
}

# Create order
response = requests.post(
    f"http://localhost:8000/api/orders?session_id={session_id}",
    json=order_data
)

if response.status_code == 201:
    order = response.json()
    print(f"Order created: {order['id']}")
    print(f"Total: ${order['total_price']}")
    print(f"Calories: {order['total_calories']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

## Best Practices

### 1. Session Management
- Generate unique session IDs for each customer session
- Include session ID in all related API calls
- Use meaningful session ID patterns for debugging

### 2. Error Handling
- Always check response status codes
- Handle 422 validation errors gracefully
- Provide user-friendly error messages

### 3. Data Validation
- Validate UUIDs before sending requests
- Check ingredient/addon availability before ordering
- Validate quantity constraints on the client side

### 4. Performance
- Batch multiple ingredient/addon lookups when possible
- Cache machine information to avoid repeated validation
- Use appropriate request timeouts

### 5. User Experience
- Show real-time pricing during order building
- Display stock availability warnings
- Provide order confirmation with estimated preparation time

## Related Endpoints

- `GET /ingredients` - List available ingredients
- `GET /addons` - List available addons  
- `GET /machines` - List available machines
- `GET /orders/{order_id}` - Get order details
- `PUT /orders/{order_id}/status` - Update order status
- `GET /dashboard/analytics` - Order analytics and insights
