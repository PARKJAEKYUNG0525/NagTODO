from datetime import datetime

from pydantic import BaseModel
from typing import Annotated

# models 작성한 거 보면서 작성
class BoardBase(BaseModel):
    title: str
    description: str | None = None
    category: str

class BoardCreate(BoardBase):
    pass

class BoardInDB(BoardBase):
    board_id: int
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True

class BoardRead(BoardInDB):
    pass