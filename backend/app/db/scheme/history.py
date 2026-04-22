from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Annotated, Optional

class HistoryBase(BaseModel):
    user_id: str
    title: str
    todo_status: str
    archived_at: str

class HistoryCreate(HistoryBase):
    todo_id: Annotated[str, Field(max_length=100)]

class HistoryUpdate(BaseModel):
    user_id: str | None = None
    title: str | None = None
    todo_status: str | None = None
    archived_at: str | None = None
    todo_id: str | None = None

class HistoryInDB(BaseModel):
    history_id: str
    user_id: str
    title: str
    todo_status: str
    archived_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    todo_id: str

    class Config:
        from_attributes = True

class HistoryRead(HistoryInDB):
    pass