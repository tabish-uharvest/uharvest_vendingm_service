from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, insert, and_, or_, func, text
from sqlalchemy.exc import IntegrityError, NoResultFound
from typing import TypeVar, Generic, Type, List, Optional, Dict, Any, Union
from uuid import UUID
import logging

from app.config.database import Base
from app.utils.exceptions import (
    DatabaseError, 
    NotFoundError, 
    ValidationError, 
    ConflictError
)

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseDAO(Generic[ModelType]):
    """Base Data Access Object with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def create(self, session: AsyncSession, **kwargs) -> ModelType:
        """Create a new record"""
        try:
            db_obj = self.model(**kwargs)
            session.add(db_obj)
            await session.flush()
            await session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error creating {self.model.__name__}: {e}")
            raise ConflictError(f"Duplicate or invalid data for {self.model.__name__}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to create {self.model.__name__}")
    
    async def get_by_id(self, session: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Get record by ID"""
        try:
            result = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by ID {id}: {e}")
            raise DatabaseError(f"Failed to get {self.model.__name__}")
    
    async def get_by_id_or_404(self, session: AsyncSession, id: UUID) -> ModelType:
        """Get record by ID or raise NotFoundError"""
        obj = await self.get_by_id(session, id)
        if not obj:
            raise NotFoundError(f"{self.model.__name__} with ID {id} not found")
        return obj
    
    async def get_all(
        self, 
        session: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """Get all records with optional filtering and pagination"""
        try:
            query = select(self.model)
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.where(getattr(self.model, field) == value)
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))
            else:
                query = query.order_by(self.model.created_at.desc())
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} list: {e}")
            raise DatabaseError(f"Failed to get {self.model.__name__} list")
    
    async def get_count(
        self, 
        session: AsyncSession, 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Get count of records with optional filtering"""
        try:
            query = select(func.count(self.model.id))
            
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.where(getattr(self.model, field) == value)
            
            result = await session.execute(query)
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to count {self.model.__name__}")
    
    async def update(
        self, 
        session: AsyncSession, 
        id: UUID, 
        **kwargs
    ) -> Optional[ModelType]:
        """Update record by ID"""
        try:
            # Remove None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return await self.get_by_id(session, id)
            
            await session.execute(
                update(self.model)
                .where(self.model.id == id)
                .values(**update_data)
            )
            
            return await self.get_by_id(session, id)
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error updating {self.model.__name__} {id}: {e}")
            raise ConflictError(f"Invalid data for {self.model.__name__} update")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating {self.model.__name__} {id}: {e}")
            raise DatabaseError(f"Failed to update {self.model.__name__}")
    
    async def delete(self, session: AsyncSession, id: UUID) -> bool:
        """Delete record by ID"""
        try:
            result = await session.execute(
                delete(self.model).where(self.model.id == id)
            )
            return result.rowcount > 0
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Integrity error deleting {self.model.__name__} {id}: {e}")
            raise ConflictError(f"Cannot delete {self.model.__name__} - it's referenced by other records")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting {self.model.__name__} {id}: {e}")
            raise DatabaseError(f"Failed to delete {self.model.__name__}")
    
    async def exists(self, session: AsyncSession, id: UUID) -> bool:
        """Check if record exists"""
        try:
            result = await session.execute(
                select(func.count(self.model.id)).where(self.model.id == id)
            )
            return result.scalar() > 0
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__} {id}: {e}")
            raise DatabaseError(f"Failed to check {self.model.__name__} existence")
    
    async def execute_raw_sql(
        self, 
        session: AsyncSession, 
        sql: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute raw SQL query"""
        try:
            result = await session.execute(text(sql), params or {})
            return result
        except Exception as e:
            logger.error(f"Error executing raw SQL: {e}")
            raise DatabaseError("Failed to execute query")
