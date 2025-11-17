from sqlalchemy import Column, Integer, String
from .db import Base

class Item(Base):
    """SQLAlchemy model for the items table"""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False)