from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Annotated, Optional

class FriendBase(BaseModel):
    status: str = "대기"

class FriendCreate(BaseModel):
    receiver_id: int

class FriendUpdate(BaseModel):
    receiver_id: int | None = None
    status: str | None = None

class FriendInDB(FriendBase):
    friend_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    receiver_id: int
    requester_id: int

    class Config:
        from_attributes = True

class FriendRead(FriendInDB):
    requester_username: str | None = None
    receiver_username: str | None = None
    requester_status_message: str | None = None
    receiver_status_message: str | None = None
    requester_file_url: str | None = None
    receiver_file_url: str | None = None

    @classmethod
    def from_orm_with_users(cls, friend):
        return cls(
            friend_id=friend.friend_id,
            status=friend.status,
            created_at=friend.created_at,
            receiver_id=friend.receiver_id,
            requester_id=friend.requester_id,
            requester_username=friend.requester.username if friend.requester else None,
            receiver_username=friend.receiver.username if friend.receiver else None,
            requester_status_message=friend.requester.status_message if friend.requester else None,
            receiver_status_message=friend.receiver.status_message if friend.receiver else None,
            requester_file_url=friend.requester.cloths.file_url if friend.requester and friend.requester.cloths else None,
            receiver_file_url=friend.receiver.cloths.file_url if friend.receiver and friend.receiver.cloths else None,
        )
