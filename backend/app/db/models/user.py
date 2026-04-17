from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from sqlalchemy import String, TIMESTAMP, Enum, func
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .todo import Todo
    from .friend import Friend
    from .friend_todo_view import FriendTodoView
    from .recommend import Recommend
    from .pw_history import PwHistory
    from .homepage import Homepage
    from .cloth import Cloth

class User(Base):
    __tablename__ = "user"

    user_id:         Mapped[str]           = mapped_column(String(100), primary_key=True)
    email:           Mapped[str]           = mapped_column(String(255), unique=True, nullable=False)
    pw:              Mapped[str]           = mapped_column(String(255), nullable=False)
    username:        Mapped[str]           = mapped_column(String(50), nullable=False)
    userimage_url:   Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    privacy_default: Mapped[str]           = mapped_column(Enum("친구공개", "비공개"), nullable=False, default="친구공개")
    created_at:      Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)
    updated_at:      Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=True)
    birthday:        Mapped[date]          = mapped_column(nullable=False)

    todos:            Mapped[List["Todo"]]           = relationship("Todo", back_populates="user", cascade="all, delete-orphan")
    friends_sent:     Mapped[List["Friend"]]         = relationship("Friend", foreign_keys="Friend.requester_id", back_populates="requester", cascade="all, delete-orphan")
    friends_received: Mapped[List["Friend"]]         = relationship("Friend", foreign_keys="Friend.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
    friend_todo_views:Mapped[List["FriendTodoView"]] = relationship("FriendTodoView", back_populates="user", cascade="all, delete-orphan")
    recommends:       Mapped[List["Recommend"]]      = relationship("Recommend", back_populates="user", cascade="all, delete-orphan")
    pw_histories:     Mapped[List["PwHistory"]]      = relationship("PwHistory", back_populates="user", cascade="all, delete-orphan")
    homepages:        Mapped[List["Homepage"]]       = relationship("Homepage", back_populates="user", cascade="all, delete-orphan")
    cloths:           Mapped[List["Cloth"]]          = relationship("Cloth", back_populates="user", cascade="all, delete-orphan")