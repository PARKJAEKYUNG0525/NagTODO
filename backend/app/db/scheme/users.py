from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Annotated

class UserBase(BaseModel):
    email: str
    username: str
    password: str

class UserCreate(UserBase):
    email: str
    username: str
    password: Annotated[str, Field(max_length=72)]

class UserLogin(BaseModel):
    email: str
    password: Annotated[str, Field(max_length=72)]

class UserUpdate(BaseModel):
    email: str | None = None
    username: str | None = None
    password: str | None = None

class UserInDB(UserBase):
    user_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # sqlalchemy 객체를 pydantic 모델로 변환할 때 사용
    class Config:
        from_attributes = True

# UserBase를 상속받은 UserInDB를 상속받았기 때문에
# UserBase의 email, username, password + UserInDB의 user_id, created_at, Config
# 이 모두를 가지고 있기 때문에 pass
class UserRead(UserInDB):
    pass
