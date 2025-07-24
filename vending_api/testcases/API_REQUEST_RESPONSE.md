# Urban Harvest Vending Machine API - Request/Response Bodies

## API Base URL: `/api/v1`

---

## 🟦 CUSTOMER/PUBLIC ENDPOINTS

### 1. Machine Inventory

#### `GET /api/v1/machines/{machine_id}/inventory`

**Request:**
- Path Parameters: `machine_id` (UUID)
- Query Parameters: None

**Response:**
```json
{
  "machine_id": "550e8400-e29b-41d4-a716-446655440000",
  "machine_location": "Main Campus - Building A",
  "machine_status": "active",
  "ingredients": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Banana",
      "item_type": "ingredient",
      "emoji": "🍌",
      "qty_available": 4500,
      "qty_available_unit": "grams",
      "low_stock_threshold": 500,
      "is_low_stock": false,
      "is_available": true,
      "price_per_unit": 0.0015,
      "calories_per_unit": 1,
      "min_qty": 50,
      "max_percent_limit": 40
    }
  ],
  "addons": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "name": "Protein Powder",
      "item_type": "addon",
      "icon": "💪",
      "qty_available": 25,
      "qty_available_unit": "units",
      "low_stock_threshold": 5,
      "is_low_stock": false,
      "is_available": true,
      "price_per_unit": 2.50,
      "calories_per_unit": 120
    }
  ],
  "last_updated": "2025-07-04T10:30:00Z"
}
```

### 2. Machine Presets

#### `GET /api/v1/machines/{machine_id}/presets`

**Request:**
- Path Parameters: `machine_id` (UUID)
- Query Parameters: 
  - `category` (optional): "smoothie" or "salad"

**Response:**
```json
{
  "presets": [
    {
      "id": "789e0123-e89b-12d3-a456-426614174002",
      "name": "Tropical Paradise",
      "category": "smoothie",
      "price": 8.99,
      "calories": 280,
      "description": "Mango, pineapple, coconut water blend",
      "image": "/images/tropical-smoothie.jpg",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-07-04T10:30:00Z"
    }
  ]
}
```

### 3. Create Order

#### `POST /api/v1/orders`

**Request:**
```json
{
  "machine_id": "550e8400-e29b-41d4-a716-446655440000",
  "ingredients": [
    {
      "ingredient_id": "123e4567-e89b-12d3-a456-426614174000",
      "grams_used": 150
    },
    {
      "ingredient_id": "234e5678-e89b-12d3-a456-426614174001",
      "grams_used": 125
    }
  ],
  "addons": [
    {
      "addon_id": "456e7890-e89b-12d3-a456-426614174001",
      "qty": 1
    }
  ],
  "payment_method": "card",
  "notes": "Extra blended please"
}
```

**Response:**
```json
{
  "id": "890e1234-e89b-12d3-a456-426614174003",
  "machine_id": "550e8400-e29b-41d4-a716-446655440000",
  "machine_location": "Main Campus - Building A",
  "user_id": null,
  "session_id": "sess_123456789",
  "status": "pending",
  "total_price": 11.49,
  "total_calories": 400,
  "payment_method": "card",
  "payment_status": "pending",
  "notes": "Extra blended please",
  "created_at": "2025-07-04T10:35:00Z",
  "updated_at": "2025-07-04T10:35:00Z",
  "items": [
    {
      "id": "901e2345-e89b-12d3-a456-426614174004",
      "ingredient_id": "123e4567-e89b-12d3-a456-426614174000",
      "ingredient_name": "Banana",
      "ingredient_emoji": "🍌",
      "grams_used": 150,
      "price": 2.25,
      "calories": 150
    }
  ],
  "addons": [
    {
      "id": "012e3456-e89b-12d3-a456-426614174005",
      "addon_id": "456e7890-e89b-12d3-a456-426614174001",
      "addon_name": "Protein Powder",
      "addon_icon": "💪",
      "qty": 1,
      "price": 2.50,
      "calories": 120
    }
  ]
}
```

### 4. Get Order Status

#### `GET /api/v1/orders/{order_id}`

**Request:**
- Path Parameters: `order_id` (UUID)

**Response:** Same as create order response above

### 5. Update Order Status

#### `PUT /api/v1/orders/{order_id}/status`

**Request:**
```json
{
  "status": "processing",
  "payment_status": "paid",
  "notes": "Payment confirmed, preparing order"
}
```

**Response:** Same as create order response above

### 6. Get Products

#### `GET /api/v1/ingredients`

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Banana",
    "emoji": "🍌",
    "image": "/images/banana.jpg",
    "min_qty_g": 50,
    "max_percent_limit": 40,
    "calories_per_g": 1.0,
    "price_per_gram": 0.0015,
    "category": "fruit",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-07-04T10:30:00Z"
  }
]
```

#### `GET /api/v1/addons`

**Response:**
```json
[
  {
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "name": "Protein Powder",
    "price": 2.50,
    "calories": 120,
    "icon": "💪",
    "description": "High-quality whey protein",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-07-04T10:30:00Z"
  }
]
```

---

## 🟨 ADMIN ENDPOINTS

### 7. List Machines

#### `GET /api/v1/admin/machines`

**Request:**
- Query Parameters:
  - `skip` (default: 0): Number of items to skip
  - `limit` (default: 50): Number of items to return
  - `status` (optional): Filter by status

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "location": "Main Campus - Building A",
    "status": "active",
    "cups_qty": 100,
    "bowls_qty": 50,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-07-04T10:30:00Z"
  }
]
```

### 8. Create Machine

#### `POST /api/v1/admin/machines`

**Request:**
```json
{
  "location": "Student Center - Ground Floor",
  "status": "active",
  "cups_qty": 100,
  "bowls_qty": 50
}
```

**Response:** Same as list machines item above

### 9. Update Machine

#### `PUT /api/v1/admin/machines/{machine_id}`

**Request:**
```json
{
  "location": "Updated Location Name",
  "status": "maintenance",
  "cups_qty": 75,
  "bowls_qty": 25
}
```

**Response:** Same as list machines item above

### 10. Update Machine Status

#### `PUT /api/v1/admin/machines/{machine_id}/status`

**Request:**
```json
{
  "status": "maintenance"
}
```

**Response:**
```json
{
  "message": "Machine status updated successfully",
  "data": {
    "machine_id": "550e8400-e29b-41d4-a716-446655440000",
    "old_status": "active",
    "new_status": "maintenance"
  },
  "timestamp": "2025-07-04T10:40:00Z"
}
```

### 11. Update Ingredient Stock

#### `PUT /api/v1/admin/machines/{machine_id}/ingredients/{ingredient_id}/stock`

**Request:**
```json
{
  "qty_available_g": 5000,
  "low_stock_threshold_g": 500
}
```

**Response:**
```json
{
  "message": "Ingredient stock updated successfully",
  "data": {
    "machine_id": "550e8400-e29b-41d4-a716-446655440000",
    "ingredient_id": "123e4567-e89b-12d3-a456-426614174000",
    "ingredient_name": "Banana",
    "old_qty": 4500,
    "new_qty": 5000,
    "updated_at": "2025-07-04T10:45:00Z"
  },
  "timestamp": "2025-07-04T10:45:00Z"
}
```

### 12. Bulk Restock

#### `POST /api/v1/admin/machines/{machine_id}/restock`

**Request:**
```json
{
  "items": [
    {
      "item_id": "123e4567-e89b-12d3-a456-426614174000",
      "item_type": "ingredient",
      "qty_to_add": 2000
    },
    {
      "item_id": "456e7890-e89b-12d3-a456-426614174001",
      "item_type": "addon",
      "qty_to_add": 15
    }
  ]
}
```

**Response:**
```json
{
  "message": "Bulk restock completed successfully",
  "data": {
    "machine_id": "550e8400-e29b-41d4-a716-446655440000",
    "items_updated": 2,
    "total_items": 2,
    "details": [
      {
        "item_id": "123e4567-e89b-12d3-a456-426614174000",
        "item_name": "Banana",
        "item_type": "ingredient",
        "old_qty": 4500,
        "new_qty": 6500,
        "qty_added": 2000
      }
    ]
  },
  "timestamp": "2025-07-04T10:50:00Z"
}
```

### 13. Low Stock Alerts

#### `GET /api/v1/admin/inventory/alerts`

**Request:**
- Query Parameters:
  - `machine_id` (optional): Filter by machine
  - `severity` (optional): "low" or "out"

**Response:**
```json
[
  {
    "machine_id": "550e8400-e29b-41d4-a716-446655440000",
    "machine_location": "Main Campus - Building A",
    "item_id": "234e5678-e89b-12d3-a456-426614174001",
    "item_name": "Strawberry",
    "item_type": "ingredient",
    "current_qty": 200,
    "threshold": 300,
    "percentage_remaining": 15.5,
    "priority": "warning",
    "last_updated": "2025-07-04T10:30:00Z"
  }
]
```

### 14. Create Product (Ingredient)

#### `POST /api/v1/admin/ingredients`

**Request:**
```json
{
  "name": "Mango",
  "emoji": "🥭",
  "image": "/images/mango.jpg",
  "min_qty_g": 40,
  "max_percent_limit": 35,
  "calories_per_g": 1.2,
  "price_per_gram": 0.0022,
  "category": "fruit"
}
```

**Response:**
```json
{
  "id": "345e6789-e89b-12d3-a456-426614174002",
  "name": "Mango",
  "emoji": "🥭",
  "image": "/images/mango.jpg",
  "min_qty_g": 40,
  "max_percent_limit": 35,
  "calories_per_g": 1.2,
  "price_per_gram": 0.0022,
  "category": "fruit",
  "created_at": "2025-07-04T11:00:00Z",
  "updated_at": "2025-07-04T11:00:00Z"
}
```

### 15. Create Preset

#### `POST /api/v1/admin/presets`

**Request:**
```json
{
  "name": "Green Power",
  "category": "smoothie",
  "price": 9.49,
  "calories": 220,
  "description": "Spinach, kale, banana powerhouse",
  "image": "/images/green-smoothie.jpg",
  "ingredients": [
    {
      "ingredient_id": "123e4567-e89b-12d3-a456-426614174000",
      "grams_used": 100,
      "percentage": 40
    },
    {
      "ingredient_id": "567e8901-e89b-12d3-a456-426614174003",
      "grams_used": 75,
      "percentage": 30
    }
  ]
}
```

**Response:**
```json
{
  "id": "678e9012-e89b-12d3-a456-426614174004",
  "name": "Green Power",
  "category": "smoothie",
  "price": 9.49,
  "calories": 220,
  "description": "Spinach, kale, banana powerhouse",
  "image": "/images/green-smoothie.jpg",
  "ingredients": [
    {
      "ingredient_id": "123e4567-e89b-12d3-a456-426614174000",
      "ingredient_name": "Banana",
      "ingredient_emoji": "🍌",
      "grams_used": 100,
      "percentage": 40,
      "calories": 100,
      "price": 1.50
    }
  ],
  "created_at": "2025-07-04T11:10:00Z",
  "updated_at": "2025-07-04T11:10:00Z"
}
```

### 16. Admin Orders List

#### `GET /api/v1/admin/orders`

**Request:**
- Query Parameters:
  - `skip` (default: 0)
  - `limit` (default: 50)
  - `machine_id` (optional)
  - `status` (optional)
  - `start_date` (optional): YYYY-MM-DD
  - `end_date` (optional): YYYY-MM-DD

**Response:**
```json
{
  "items": [
    {
      "id": "890e1234-e89b-12d3-a456-426614174003",
      "machine_id": "550e8400-e29b-41d4-a716-446655440000",
      "machine_location": "Main Campus - Building A",
      "user_id": null,
      "session_id": "sess_123456789",
      "status": "completed",
      "total_price": 11.49,
      "total_calories": 400,
      "payment_method": "card",
      "payment_status": "paid",
      "created_at": "2025-07-04T10:35:00Z",
      "items_count": 2,
      "addons_count": 1
    }
  ],
  "total": 156,
  "page": 1,
  "size": 50,
  "pages": 4
}
```

### 17. Order Statistics

#### `GET /api/v1/admin/orders/stats`

**Request:**
- Query Parameters:
  - `machine_id` (optional)
  - `start_date` (optional)
  - `end_date` (optional)

**Response:**
```json
{
  "total_orders": 1250,
  "completed_orders": 1125,
  "cancelled_orders": 75,
  "failed_orders": 25,
  "pending_orders": 15,
  "processing_orders": 10,
  "total_revenue": 12450.75,
  "avg_order_value": 9.96,
  "avg_calories": 320.5,
  "completion_rate": 90.0
}
```

### 18. Dashboard Overview

#### `GET /api/v1/admin/dashboard`

**Response:**
```json
{
  "metrics": {
    "total_machines": 5,
    "active_machines": 4,
    "total_orders_today": 45,
    "total_revenue_today": 425.50,
    "total_orders_this_month": 1250,
    "total_revenue_this_month": 12450.75,
    "avg_order_value": 9.96,
    "completion_rate": 90.0,
    "low_stock_alerts": 3,
    "out_of_stock_alerts": 0
  },
  "machines": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "location": "Main Campus - Building A",
      "status": "active",
      "orders_today": 18,
      "revenue_today": 189.25,
      "low_stock_items": 1,
      "last_order_time": "2025-07-04T11:45:00Z"
    }
  ],
  "recent_orders": [
    {
      "id": "890e1234-e89b-12d3-a456-426614174003",
      "machine_location": "Main Campus - Building A",
      "total_price": 11.49,
      "status": "completed",
      "created_at": "2025-07-04T11:45:00Z"
    }
  ],
  "top_selling_items": [
    {
      "name": "Banana",
      "emoji": "🍌",
      "type": "ingredient",
      "orders_count": 125,
      "revenue": 187.50
    }
  ],
  "alerts": [
    {
      "type": "low_stock",
      "message": "Strawberry running low at Main Campus",
      "severity": "warning",
      "timestamp": "2025-07-04T10:30:00Z"
    }
  ],
  "timestamp": "2025-07-04T12:00:00Z"
}
```

### 19. Sales Report

#### `GET /api/v1/admin/reports/sales`

**Request:**
- Query Parameters:
  - `start_date` (required): YYYY-MM-DD
  - `end_date` (required): YYYY-MM-DD
  - `machine_id` (optional)
  - `group_by` (default: "day"): "hour", "day", "week", "month"

**Response:**
```json
{
  "start_date": "2025-07-01",
  "end_date": "2025-07-04",
  "machine_id": null,
  "machine_location": null,
  "total_orders": 185,
  "total_revenue": 1845.50,
  "avg_order_value": 9.98,
  "completion_rate": 92.4,
  "data_points": [
    {
      "period": "2025-07-01",
      "orders_count": 42,
      "revenue": 425.50,
      "avg_order_value": 10.13,
      "completion_rate": 95.2
    },
    {
      "period": "2025-07-02",
      "orders_count": 38,
      "revenue": 389.75,
      "avg_order_value": 10.26,
      "completion_rate": 89.5
    }
  ],
  "top_products": [
    {
      "name": "Tropical Paradise",
      "type": "preset",
      "orders_count": 25,
      "revenue": 224.75
    }
  ],
  "generated_at": "2025-07-04T12:05:00Z"
}
```

---

## 🔴 ERROR RESPONSES

### Standard Error Format
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": {
    "field_errors": [
      {
        "field": "machine_id",
        "message": "Machine ID is required"
      }
    ],
    "request_id": "req_123456789"
  },
  "timestamp": "2025-07-04T12:00:00Z"
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request / Validation Error
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity / Business Rule Violation
- `500` - Internal Server Error

### Common Error Codes
- `VALIDATION_ERROR` - Request validation failed
- `NOT_FOUND` - Resource not found
- `CONFLICT` - Resource conflict
- `BUSINESS_RULE_VIOLATION` - Business rule violated
- `INSUFFICIENT_STOCK` - Not enough inventory
- `MACHINE_UNAVAILABLE` - Machine not available
- `ORDER_PROCESSING_ERROR` - Order processing failed
- `DATABASE_ERROR` - Database operation failed

---

This documentation covers all the major request/response patterns for the Urban Harvest Vending Machine API. All endpoints follow consistent patterns with proper validation, error handling, and comprehensive response data.
