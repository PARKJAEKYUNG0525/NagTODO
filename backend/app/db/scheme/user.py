from pydantic import BaseModel, Field
from datetime import datetime, timezone, date
from typing import Annotated

# Password = Annotated[str, Field(min_length=8, max_length=30,
#                                 pattern=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&]).*$",
#                                 description="8~30자, 영문/숫자/특수문자 포함"
#                                 )]

Password = Annotated[
    str,
    Field(
        min_length=8,
        max_length=255,
        description="8~30자, 영문/숫자/특수문자 포함"
    )
]

class UserBase(BaseModel):
    email : str
    username : str
    pw : Password

class UserCreate(UserBase):
    birthday : date

class UserPasswordUpdate(BaseModel):
    current_pw: str
    new_pw: str
    confirm_pw: str

class UserLogin(BaseModel):
    email : str
    pw : Password

class UserUpdate(BaseModel):
    email : str | None = None
    pw : Password | None = None
    username : str | None = None
    userimage_url : str | None = None
    birthday : date | None = None
    cloth_id: str | None = None
    img_id : str | None = None
    music_id : str | None = None
    status_message: str | None = None

class UserInDB(UserBase):
    user_id: int
    email: str
    username: str
    userimage_url: str | None = None  # Optional로 변경
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    birthday: date
    cloth_id: str | None = None
    img_id : str | None = None
    music_id : str | None = None
    status_message: str | None = None

    class Config:
        from_attributes = True

class UserRead(UserInDB):
    pass