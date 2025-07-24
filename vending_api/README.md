# Urban Harvest Vending Machine API

A production-ready FastAPI backend service for the Urban Harvest Vending Machine system, providing comprehensive customer ordering and admin management capabilities with robust transaction support.

## Features

### Customer Features
- 🥤 **Machine Inventory**: Real-time ingredient and addon availability
- 🍓 **Preset Recipes**: Pre-configured smoothie and salad combinations
- 🛒 **Order Creation**: Custom orders with stock validation and automatic deduction
- 📊 **Order Tracking**: Real-time order status updates
- 💳 **Payment Integration**: Multiple payment method support

### Admin Features
- 🏪 **Machine Management**: Full CRUD operations for vending machines
- 📦 **Inventory Control**: Real-time stock management with low-stock alerts
- 🥗 **Product Management**: Manage ingredients, addons, and presets
- 📋 **Order Monitoring**: Comprehensive order tracking and statistics
- 📈 **Analytics Dashboard**: Sales reports and machine performance metrics
- 🔄 **Bulk Operations**: Efficient restocking and inventory updates

## Architecture

### Technology Stack
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **Authentication**: JWT tokens with python-jose
- **Testing**: pytest with async support
- **Documentation**: Auto-generated OpenAPI/Swagger

### Design Patterns
- **Clean Architecture**: Separation of concerns with layers (Controllers → Services → DAOs → Models)
- **Repository Pattern**: Database abstraction through DAOs
- **Transaction Management**: ACID compliance with async transactions
- **Dependency Injection**: FastAPI's built-in DI system
- **Exception Handling**: Custom exception hierarchy with proper HTTP status codes

## Project Structure

```
vending_api/
├── app/
│   ├── config/           # Configuration and database setup
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── dao/              # Data Access Objects with transactions
│   ├── services/         # Business logic layer
│   ├── controllers/      # FastAPI route handlers
│   │   └── admin/        # Admin-specific endpoints
│   ├── transformers/     # Data transformation utilities
│   └── utils/            # Utilities and exceptions
├── requirements.txt      # Python dependencies
├── .env.example         # Environment configuration template
└── run_server.py        # Server startup script
```

## Quick Start

### 1. Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### 2. Installation

```bash
# Clone the repository
cd c:\Work\uharvest_vendingm_service\vending_api

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your database credentials
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb uharvest_vending

# Run the schema.sql file in your database
psql -d uharvest_vending -f ..\database\schema.sql
```

### 4. Configuration

Edit `.env` file:
```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/uharvest_vending
DATABASE_URL_SYNC=postgresql://username:password@localhost:5432/uharvest_vending
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=True
```

### 5. Start the Server

```bash
# Development mode with auto-reload
python run_server.py --reload --debug

# Production mode
python run_server.py --workers 4
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### Customer Endpoints (v1)
```
GET    /api/v1/machines/{machine_id}/inventory     # Available ingredients/addons
GET    /api/v1/machines/{machine_id}/presets       # Available preset recipes  
GET    /api/v1/machines/{machine_id}/status        # Machine status
POST   /api/v1/orders                              # Create new order
GET    /api/v1/orders/{order_id}                   # Get order status
PUT    /api/v1/orders/{order_id}/status            # Update order status
GET    /api/v1/ingredients                         # List ingredients
GET    /api/v1/addons                              # List addons
GET    /api/v1/presets                             # List preset recipes
```

### Admin Endpoints (v1)
```
# Machine Management
GET    /api/v1/admin/machines                      # List all machines
POST   /api/v1/admin/machines                      # Create machine
PUT    /api/v1/admin/machines/{id}                 # Update machine
DELETE /api/v1/admin/machines/{id}                 # Delete machine

# Inventory Management  
GET    /api/v1/admin/machines/{id}/inventory       # Full inventory details
PUT    /api/v1/admin/machines/{id}/ingredients/{ingredient_id}/stock
PUT    /api/v1/admin/machines/{id}/addons/{addon_id}/stock
POST   /api/v1/admin/machines/{id}/restock         # Bulk restock
GET    /api/v1/admin/inventory/alerts              # Low stock alerts

# Product Management
GET    /api/v1/admin/ingredients                   # List ingredients
POST   /api/v1/admin/ingredients                   # Create ingredient
PUT    /api/v1/admin/ingredients/{id}              # Update ingredient
DELETE /api/v1/admin/ingredients/{id}              # Delete ingredient
GET    /api/v1/admin/addons                        # List addons
POST   /api/v1/admin/addons                        # Create addon
PUT    /api/v1/admin/addons/{id}                   # Update addon
DELETE /api/v1/admin/addons/{id}                   # Delete addon
GET    /api/v1/admin/presets                       # List presets
POST   /api/v1/admin/presets                       # Create preset
PUT    /api/v1/admin/presets/{id}                  # Update preset
DELETE /api/v1/admin/presets/{id}                  # Delete preset

# Order Management
GET    /api/v1/admin/orders                        # List orders with filters
GET    /api/v1/admin/orders/{id}                   # Order details
PUT    /api/v1/admin/orders/{id}/status            # Update order status
GET    /api/v1/admin/orders/stats                  # Order statistics

# Dashboard & Reports
GET    /api/v1/admin/dashboard                     # System overview
GET    /api/v1/admin/reports/sales                 # Sales reports
GET    /api/v1/admin/reports/inventory             # Inventory reports
GET    /api/v1/admin/reports/machine-performance   # Performance analytics
```

**Total: 42+ endpoints implemented with full v1 API versioning**

For complete endpoint documentation, see [API_ENDPOINTS.md](./API_ENDPOINTS.md)

## Transaction Management

The API implements robust transaction management for critical operations:

### Order Creation Flow
```python
async with get_async_transaction() as session:
    # 1. Validate machine availability
    # 2. Calculate pricing and calories  
    # 3. Validate stock availability
    # 4. Create order record
    # 5. Create order items and addons
    # 6. Deduct inventory stock
    # All steps are atomic - rollback on any failure
```

### Stock Management
- **Automatic Deduction**: Stock reduced immediately on order creation
- **Rollback Support**: Failed/cancelled orders restore stock automatically
- **Concurrent Safety**: Database-level constraints prevent overselling
- **Low Stock Alerts**: Configurable thresholds with priority levels

## Business Rules

### Order Processing
- Only one order per machine at a time
- Stock validation before deduction
- Minimum quantity constraints per ingredient
- Maximum percentage limits per ingredient
- Automatic pricing calculation

### Machine Management
- Independent inventory per machine
- Status-based availability (active/maintenance/inactive)
- Container quantity tracking (cups/bowls)
- Performance metrics and analytics

### Admin Operations
- Audit logging for all changes
- Bulk operations with transaction safety
- Data integrity constraints
- Cascading deletion protection

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Adding New Features

1. **Models**: Add SQLAlchemy models in `app/models/`
2. **Schemas**: Create Pydantic schemas in `app/schemas/`
3. **DAOs**: Implement data access in `app/dao/`
4. **Services**: Add business logic in `app/services/`
5. **Controllers**: Create API endpoints in `app/controllers/`

## Production Deployment

### Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/db_name
SECRET_KEY=production-secret-key-256-bits
DEBUG=False
ALLOWED_ORIGINS=["https://yourdomain.com"]
LOG_LEVEL=INFO
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run_server.py", "--workers", "4"]
```

### Production Checklist
- [ ] Set strong SECRET_KEY
- [ ] Configure production database
- [ ] Set DEBUG=False
- [ ] Configure CORS origins
- [ ] Set up SSL/TLS
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure backup strategy

## Monitoring and Logging

### Health Checks
- **Basic**: `/api/v1/health` - Database connectivity
- **Detailed**: `/api/v1/health/detailed` - System metrics

### Logging
- Request/response logging with request IDs
- Error tracking with stack traces
- Performance metrics
- Admin operation audit trails

### Metrics
- Order completion rates
- Machine performance statistics
- Inventory turnover
- Revenue analytics

## Security

### Authentication
- JWT token-based authentication
- Configurable token expiration
- Role-based access control (planned)

### Data Protection
- SQL injection prevention (parameterized queries)
- Input validation with Pydantic
- CORS configuration
- Request rate limiting (planned)

## Support

### Documentation
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Troubleshooting
1. **Database Connection Issues**: Check DATABASE_URL and PostgreSQL service
2. **Import Errors**: Ensure virtual environment is activated
3. **Port Conflicts**: Change port with `--port` argument
4. **Permission Errors**: Check database user permissions

### Common Commands
```bash
# Start development server
python run_server.py --reload

# Start with custom port
python run_server.py --port 9000

# Production mode
python run_server.py --workers 4 --log-level info

# Check database connection
python -c "from app.config.database import async_engine; print('DB Config OK')"
```

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use type hints
5. Follow PEP 8 style guidelines

## License

This project is part of the Urban Harvest Vending Machine system.
