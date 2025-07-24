from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from .settings import settings

logger = logging.getLogger(__name__)

# Async Database Engine
async_engine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    echo=settings.debug,
    future=True
)

# Sync Database Engine (for migrations and admin operations)
sync_engine = create_engine(
    settings.database_url_sync,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    echo=settings.debug,
    future=True
)

# Session makers
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False
)

# Base class for all models
Base = declarative_base()

# Dependency to get async database session
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

# Dependency to get sync database session (for admin operations)
def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Sync database session error: {e}")
        raise
    finally:
        db.close()

# Context manager for async transactions
@asynccontextmanager
async def get_async_transaction() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Transaction error: {e}")
                raise

# Context manager for sync transactions
@asynccontextmanager
async def get_sync_transaction():
    db = SyncSessionLocal()
    transaction = db.begin()
    try:
        yield db
        transaction.commit()
    except Exception as e:
        transaction.rollback()
        logger.error(f"Sync transaction error: {e}")
        raise
    finally:
        db.close()
