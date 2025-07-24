# Urban Harvest Vending Machine - UI + Backend Deployment Pattern

## Deployment Architecture

This system is designed for the following deployment pattern:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  UI Instance 1  │    │  UI Instance 2  │    │  UI Instance N  │
│  (Machine A)    │    │  (Machine B)    │    │  (Machine C)    │
│                 │    │                 │    │                 │
│ machine_id:     │    │ machine_id:     │    │ machine_id:     │
│ 550e8400-e29b   │    │ 661f9511-f3ac   │    │ 772g0622-g4bd   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     Single Backend        │
                    │    FastAPI Service        │
                    │                           │
                    │  - Validates machine_ids  │
                    │  - Auto-registers new     │
                    │  - Manages all inventory  │
                    │  - Processes all orders   │
                    └─────────────┬─────────────┘
                                  │
                      ┌───────────▼───────────┐
                      │    PostgreSQL DB     │
                      │                      │
                      │ - All machine data   │
                      │ - All inventories    │
                      │ - All orders         │
                      └──────────────────────┘
```

## How It Works

### 1. UI Configuration
Each UI instance is configured with a unique `machine_id`:

```javascript
// UI Environment/Config
const MACHINE_ID = "550e8400-e29b-41d4-a716-446655440000";

// All API calls include this machine_id
fetch('/api/v1/orders', {
  method: 'POST',
  body: JSON.stringify({
    machine_id: MACHINE_ID,
    items: [...],
    addons: [...]
  })
});
```

### 2. Backend Configuration
Single backend configured for multi-machine mode:

```bash
# .env
MULTI_MACHINE_MODE=true
AUTO_REGISTER_MACHINE=true
DEFAULT_CUPS_QTY=100
DEFAULT_BOWLS_QTY=50
```

### 3. Machine Auto-Registration
When a UI sends a request with a new `machine_id`:
1. Backend checks if machine exists in database
2. If not found and `AUTO_REGISTER_MACHINE=true`:
   - Creates new machine record with the provided UUID
   - Sets default inventory levels
   - Sets default container quantities
3. Processes the request normally

### 4. API Flow Example

```http
POST /api/v1/orders
{
  "machine_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": [
    {"ingredient_id": "...", "grams_used": 150},
    {"ingredient_id": "...", "grams_used": 100}
  ],
  "addons": [
    {"addon_id": "...", "quantity": 1}
  ]
}
```

Backend processing:
1. Validates `machine_id` exists (auto-registers if needed)
2. Checks machine status and availability
3. Validates ingredient stock for this specific machine
4. Creates order and deducts stock
5. Returns order confirmation

## Benefits

- ✅ **Single Backend**: One service to maintain and deploy
- ✅ **Multiple UIs**: Each machine has its own interface
- ✅ **Auto-Discovery**: New machines register automatically
- ✅ **Independent Inventory**: Each machine tracks its own stock
- ✅ **Centralized Management**: All data in one database
- ✅ **Scalable**: Easy to add new machines
- ✅ **Admin-Friendly**: Single dashboard for all machines

## UI Deployment Checklist

For each new vending machine:
1. Deploy UI instance with unique `MACHINE_ID`
2. Configure UI to point to central backend API
3. Machine will auto-register on first API call
4. Admin can configure initial inventory via admin dashboard

## Backend Configuration

```bash
# Required settings for this pattern
MULTI_MACHINE_MODE=true
AUTO_REGISTER_MACHINE=true

# Optional defaults for new machines
DEFAULT_CUPS_QTY=100
DEFAULT_BOWLS_QTY=50
```

This pattern provides the best of both worlds: distributed UIs for each machine and centralized backend management.
