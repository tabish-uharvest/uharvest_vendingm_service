from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import time
import psutil
import os
from datetime import datetime

from app.config.database import get_async_db
from app.schemas.common import HealthStatus

router = APIRouter()

# Store startup time for uptime calculation
startup_time = time.time()


@router.get("/health", response_model=HealthStatus)
async def health_check(db: AsyncSession = Depends(get_async_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        result = await db.execute(text("SELECT 1"))
        db_status = "healthy" if result.scalar() == 1 else "unhealthy"
    except Exception:
        db_status = "unhealthy"
    
    # Calculate uptime
    uptime = time.time() - startup_time
    
    return HealthStatus(
        status="healthy" if db_status == "healthy" else "unhealthy",
        version="1.0.0",
        database=db_status,
        uptime=uptime
    )


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_async_db)):
    """Detailed health check with system metrics"""
    try:
        # Database health
        db_start = time.time()
        result = await db.execute(text("SELECT 1"))
        db_response_time = time.time() - db_start
        db_status = "healthy" if result.scalar() == 1 else "unhealthy"
    except Exception as e:
        db_status = "unhealthy"
        db_response_time = -1
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    uptime = time.time() - startup_time
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": uptime,
        "database": {
            "status": db_status,
            "response_time_ms": round(db_response_time * 1000, 2)
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available // 1024 // 1024,
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free // 1024 // 1024 // 1024
        },
        "process": {
            "pid": os.getpid(),
            "threads": psutil.Process().num_threads()
        }
    }
