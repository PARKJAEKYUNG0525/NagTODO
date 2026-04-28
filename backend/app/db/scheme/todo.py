from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Annotated, Optional

class TodoBase(BaseModel):
    title: str
    todo_status: str = "시작전"
    detail: str
    visibility: str = "친구공개"
    category_id: str

class TodoCreate(TodoBase):
    user_id: int
    category_id: Annotated[str, Field(max_length=100)]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TodoUpdate(BaseModel):
    title: str | None = None
    todo_status: str | None = None
    detail: str | None = None
    visibility: str | None = None
    category_id: str | None = None
    user_id: int | None = None

class TodoInDB(TodoBase):
    todo_id: str
    user_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True

class TodoRead(TodoInDB):
    pass


class InterferenceResult(BaseModel):
    global_rate: float | None
    personal_rate: float | None
    similar_count: int
    feedback: str
    similar_failures: list[str]


class TodoCreateResponse(TodoRead):
    interference: InterferenceResult | None = None


class CategoryStat(BaseModel):
    total: int
    completed: int
    rate: float


class MonthlyStatsResponse(BaseModel):
    user_success_rate: float
    all_users_success_rate: float
    category_stats: dict[str, CategoryStat]