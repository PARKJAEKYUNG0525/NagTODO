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
<<<<<<< HEAD
    file_url: str | None = None
=======
    
>>>>>>> 7f46033850a0a3392f3d9917f929d8bcc71f5f7c

    class Config:
        from_attributes = True

class UserRead(UserInDB):
<<<<<<< HEAD
    @classmethod
    def from_orm_custom(cls, user):
        final_url = getattr(user, "userimage_url", None)
        
        if not final_url:
            cloth_obj = getattr(user, "cloths", None)

            if cloth_obj and hasattr(cloth_obj, "file_url"):
                final_url = cloth_obj.file_url
        
        if not final_url:
            final_url = "/static/default_profile.png"

        return cls(
            user_id=user.user_id,
            email=user.email,
            username=user.username,
            pw=user.pw,
            birthday=user.birthday,
            status_message=user.status_message,
            cloth_id=user.cloth_id,
            file_url=final_url,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
=======
    pass
>>>>>>> 7f46033850a0a3392f3d9917f929d8bcc71f5f7c
