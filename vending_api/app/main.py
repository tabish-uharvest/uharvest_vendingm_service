from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from contextlib import asynccontextmanager
import logging
import time
import uuid
from typing import Any, Dict

from app.config.settings import settings
from app.config.database import async_engine, get_async_db
from app.utils.exceptions import VendingAPIException
from app.schemas.common import ErrorResponse, HealthStatus

# Import controllers
from app.controllers.health_controller import router as health_router
from app.controllers.machine_controller import router as machine_router
from app.controllers.order_controller import router as order_router
from app.controllers.product_controller import router as product_router

# Import admin controllers
from app.controllers.admin.machine_admin_controller import router as admin_machine_router
from app.controllers.admin.inventory_admin_controller import router as admin_inventory_router
from app.controllers.admin.product_admin_controller import router as admin_product_router
from app.controllers.admin.order_admin_controller import router as admin_order_router
from app.controllers.admin.dashboard_controller import router as admin_dashboard_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events"""
    # Startup
    logger.info("Starting Urban Harvest Vending API...")
    
    # Test database connection
    try:
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Urban Harvest Vending API...")
    await async_engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="Urban Harvest Vending Machine API",
    description="FastAPI backend service for Urban Harvest Vending Machine system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )


# Request ID middleware for tracing
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add request ID for tracing"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request details
    logger.info(
        f"Request {request_id}: {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Time: {process_time:.3f}s"
    )
    
    return response


# Global exception handlers
@app.exception_handler(VendingAPIException)
async def vending_api_exception_handler(request: Request, exc: VendingAPIException):
    """Handle custom API exceptions"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(
        f"Request {request_id}: {exc.error_code} - {exc.message}",
        extra={"details": exc.details}
    )
    
    status_code_map = {
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "CONFLICT": status.HTTP_409_CONFLICT,
        "BUSINESS_RULE_VIOLATION": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "INSUFFICIENT_STOCK": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "MACHINE_UNAVAILABLE": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ORDER_PROCESSING_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "PAYMENT_ERROR": status.HTTP_402_PAYMENT_REQUIRED,
        "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
        "EXTERNAL_SERVICE_ERROR": status.HTTP_502_BAD_GATEWAY,
        "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
    }
    
    status_code = status_code_map.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details
        ).model_dump(mode='json')
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(f"Request {request_id}: Validation error - {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={
                "validation_errors": exc.errors(),
                "request_id": request_id
            }
        ).model_dump(mode='json')
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(f"Request {request_id}: HTTP {exc.status_code} - {exc.detail}")
    
    error_response = ErrorResponse(
        error_code="HTTP_ERROR",
        message=exc.detail,
        details={"request_id": request_id}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json')
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.exception(f"Request {request_id}: Unexpected error - {str(exc)}")
    
    error_response = ErrorResponse(
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred" if not settings.debug else str(exc),
        details={
            "request_id": request_id,
            "error_type": type(exc).__name__ if settings.debug else None
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode='json')
    )


# Include routers with proper API versioning

# Customer/Public API endpoints
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(machine_router, prefix="/api/v1", tags=["Machines"])
app.include_router(order_router, prefix="/api/v1", tags=["Orders"])
app.include_router(product_router, prefix="/api/v1", tags=["Products"])

# Admin API endpoints
app.include_router(admin_machine_router, prefix="/api/v1/admin", tags=["Admin - Machines"])
app.include_router(admin_inventory_router, prefix="/api/v1/admin", tags=["Admin - Inventory"])
app.include_router(admin_product_router, prefix="/api/v1/admin", tags=["Admin - Products"])
app.include_router(admin_order_router, prefix="/api/v1/admin", tags=["Admin - Orders"])
app.include_router(admin_dashboard_router, prefix="/api/v1/admin", tags=["Admin - Dashboard"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API overview"""
    return {
        "service": "Urban Harvest Vending Machine API",
        "version": "1.0.0",
        "status": "active",
        "api_version": "v1",
        "documentation": "/docs",
        "endpoints": {
            "customer_apis": {
                "machines": "/api/v1/machines/{machine_id}/inventory",
                "presets": "/api/v1/machines/{machine_id}/presets", 
                "orders": "/api/v1/orders",
                "products": "/api/v1/ingredients, /api/v1/addons, /api/v1/presets"
            },
            "admin_apis": {
                "machines": "/api/v1/admin/machines",
                "inventory": "/api/v1/admin/machines/{machine_id}/inventory",
                "products": "/api/v1/admin/ingredients, /api/v1/admin/addons, /api/v1/admin/presets",
                "orders": "/api/v1/admin/orders",
                "dashboard": "/api/v1/admin/dashboard",
                "reports": "/api/v1/admin/reports/{type}"
            }
        },
        "deployment_pattern": "Single Backend + Multiple UI instances"
    }


# Dependency for request context
def get_request_context(request: Request) -> Dict[str, Any]:
    """Get request context for services"""
    return {
        "request_id": getattr(request.state, 'request_id', 'unknown'),
        "user_agent": request.headers.get("User-Agent"),
        "client_ip": request.client.host if request.client else None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
