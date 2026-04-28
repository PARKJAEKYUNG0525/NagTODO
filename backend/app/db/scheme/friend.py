from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Annotated, Optional

class FriendBase(BaseModel):
    status: str = "대기"

class FriendCreate(BaseModel):
    receiver_id: int

class FriendUpdate(BaseModel):
    status: str | None = None

class FriendInDB(FriendBase):
    friend_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    receiver_id: int
    requester_id: int

    class Config:
        from_attributes = True

class FriendRead(FriendInDB):
    pass