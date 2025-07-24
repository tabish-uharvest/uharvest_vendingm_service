from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    name = Column(Text)
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    
    # Relationships
    orders = relationship("Order", back_populates="user")
