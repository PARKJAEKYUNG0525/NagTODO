from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Annotated, Optional

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: str | None = None

class CategoryInDB(CategoryBase):
    category_id: str
    
    class Config:
        from_attributes = True

class TodoRead(CategoryInDB):
    pass