from pydantic import BaseModel
from typing import Literal

class NotificationBase(BaseModel):
    title: str
    content: str
    user_id: int
    type: Literal["friend", "system"] = "system"

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_read: bool | None = None
    type: Literal["friend", "system"] | None = None

class NotificationInDB(NotificationBase):
    notification_id: int
    is_read: bool

    class Config:
        from_attributes = True

class NotificationResponse(NotificationInDB):
    pass