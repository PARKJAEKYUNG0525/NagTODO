from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Annotated, Optional

class ClothBase(BaseModel):
    cloth_id: str
    user_id: int
    title: str

class ClothCreate(ClothBase):
    pass 

class ClothUpdate(BaseModel):
    cloth_id: str | None = None
    user_id: int | None = None
    title: str | None = None

class ClothInDB(ClothBase):
    pass 

    class Config:
        from_attributes = True

class ClothRead(ClothInDB):
    pass