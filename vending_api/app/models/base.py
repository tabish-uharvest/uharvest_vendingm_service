from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from app.config.database import Base
import uuid


class BaseModel(Base):
    """Base model with common fields for all tables"""
    __abstract__ = True
    
    @declared_attr
    def id(cls):
        return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    @declared_attr 
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.current_timestamp(), nullable=False)
    
    # @declared_attr
    # def updated_at(cls):
    #     return Column(DateTime(timezone=True), server_default=func.current_timestamp(), 
    #                  onupdate=func.current_timestamp(), nullable=False)
    
    # Temporarily removed until database schema is updated

    def to_dict(self):
        """Convert model instance to dictionary"""
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
