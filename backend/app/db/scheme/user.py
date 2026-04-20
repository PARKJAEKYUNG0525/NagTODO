from pydantic import BaseModel, Field
from datetime import datetime, timezone, date
from typing import Annotated

Password = Annotated[str, Field(min_length=8, max_length=30,
                                pattern=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&]).*$",
                                description="8~30자, 영문/숫자/특수문자 포함"
                                )]

class UserBase(BaseModel):
    email : str
    pw : Password
    username : str

class UserCreate(UserBase):
    birthday : date

class UserLogin(BaseModel):
    pw : Password
    username : str

class Userupdate(BaseModel):
    email : str | None = None
    pw : Password | None = None
    username : str | None = None
    userimage_url : str | None = None
    birthday : date | None = None

class UserInDB(UserBase):
    user_id : int
    userimage_url : str
    created_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    birthday : date

    class Config:
        from_attributes = True

class UserRead(UserInDB):
    pass