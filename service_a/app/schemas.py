from pydantic import BaseModel
from typing import List, Optional

class ItemBase(BaseModel):
    """Base Pydantic model for Item"""
    value: str

class ItemCreate(ItemBase):
    """Pydantic model for creating an Item"""
    pass

class Item(ItemBase):
    """Pydantic model for returning an Item"""
    id: int

    class Config:
        """Configuration for Pydantic model"""
        orm_mode = True

class ItemList(BaseModel):
    """Pydantic model for returning a list of Items"""
    items: List[Item]