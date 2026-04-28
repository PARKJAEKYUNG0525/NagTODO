from pydantic import BaseModel

class NotificationBase(BaseModel):
    title: str
    content: str
    user_id: int

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_read: bool | None = None

class NotificationInDB(NotificationBase):
    notification_id: int
    is_read: bool

    class Config:
        from_attributes = True

class NotificationResponse(NotificationInDB):
    pass