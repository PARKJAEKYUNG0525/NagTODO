from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Annotated, Optional

class TodoBase(BaseModel):
    title: str
    todo_status: str = "대기중"
    detail: str
    visibility: str = "친구공개"
    category_id: str

class TodoCreate(TodoBase):
    title: str
    todo_status: str = "대기중"
    detail: str
    visibility: str = "친구공개"
    user_id: Annotated[str, Field(max_length=100)]
    category_id: Annotated[str, Field(max_length=100)]

class TodoUpdate(BaseModel):
    title: str | None = None
    todo_status: str | None = None
    detail: str | None = None
    visibility: str | None = None
    category_id: str | None = None

class TodoInDB(TodoBase):
    todo_id: str
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True

class TodoRead(TodoInDB):
    pass