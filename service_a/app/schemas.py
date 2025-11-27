from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

class ItemList(BaseModel):
    """Pydantic model for returning a list of Items"""
    items: List[Item]
