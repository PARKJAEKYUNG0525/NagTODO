from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, Enum, func, Date, Integer, ForeignKey, Boolean, text
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .todo import Todo
    from .friend import Friend
    from .friend_todo_view import FriendTodoView
    # from .recommend import Recommend
    from .pw_history import PwHistory
    # from .homepage import Homepage
    from .cloth import Cloth
    from .img import Img
    from .music import Music
    from .notification import Notification

class User(Base):
    __tablename__ = "user"

    user_id:         Mapped[int]                = mapped_column(Integer, primary_key=True, autoincrement=True)
    email:           Mapped[str]                = mapped_column(String(255), unique=True, nullable=False)
    pw:              Mapped[str]                = mapped_column(String(255), nullable=False)
    username:        Mapped[str]                = mapped_column(String(50), nullable=False)
    userimage_url:   Mapped[Optional[str]]      = mapped_column(String(500), nullable=True)
    created_at:      Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)
    updated_at:      Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=True)
    birthday:        Mapped[Date]               = mapped_column(Date, nullable=False)
    state:           Mapped[bool]               = mapped_column(Boolean, nullable=False, server_default=text('1')) # 1은 회원, 0은 탈퇴
    refresh_token:   Mapped[Optional[str]]      = mapped_column(String(255), nullable=True)
    status_message:  Mapped[Optional[str]]      = mapped_column(String(500), nullable=True)
    role:            Mapped[str]                = mapped_column(String(20),  nullable=False, server_default=text("'user'")) # 기본값은 일반 유저

    cloth_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("cloth.cloth_id"),
        nullable=True
    )
    music_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("music.music_id"),
        nullable=True
    )
    img_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("img.img_id"),
        nullable=True
    )

    cloths:           Mapped[Optional["Cloth"]]      = relationship("Cloth")
    music:            Mapped[Optional["Music"]]      = relationship("Music")
    img:              Mapped[Optional["Img"]]        = relationship("Img")

    todos:            Mapped[List["Todo"]]           = relationship("Todo", back_populates="user", cascade="all, delete-orphan")
    friends_sent:     Mapped[List["Friend"]]         = relationship("Friend", foreign_keys="Friend.requester_id", back_populates="requester", cascade="all, delete-orphan")
    friends_received: Mapped[List["Friend"]]         = relationship("Friend", foreign_keys="Friend.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
    friend_todo_views:Mapped[List["FriendTodoView"]] = relationship("FriendTodoView", back_populates="user", cascade="all, delete-orphan")
    pw_histories:     Mapped[List["PwHistory"]]      = relationship("PwHistory", back_populates="user", cascade="all, delete-orphan")
    notifications:    Mapped[List["Notification"]]   = relationship("Notification", back_populates="user", cascade="all, delete-orphan")