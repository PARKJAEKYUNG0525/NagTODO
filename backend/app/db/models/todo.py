import uuid
from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TIMESTAMP, Enum, Text,func,ForeignKey,Integer
from datetime import datetime
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .category import Category
    from .friend_todo_view import FriendTodoView
    from .history import History

class Todo(Base):
    __tablename__ = "todo"

    todo_id:     Mapped[str]      = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title:       Mapped[str]      = mapped_column(String(255), nullable=False)
    todo_status: Mapped[str]      = mapped_column(Enum("대기중", "완료", "실패"), nullable=False, default="대기중")
    detail:      Mapped[str]      = mapped_column(Text, nullable=False)
    visibility:  Mapped[str]      = mapped_column(Enum("친구공개", "비공개"), nullable=False, default="친구공개")
    created_at:  Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at:  Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    user_id:     Mapped[str]      = mapped_column(Integer, ForeignKey("user.user_id"), nullable=False)
    category_id: Mapped[str]      = mapped_column(String(100), ForeignKey("category.category_id"), nullable=False)

    user:              Mapped["User"]                  = relationship("User", back_populates="todos")
    category:          Mapped["Category"]              = relationship("Category", back_populates="todos")
    friend_todo_views: Mapped[List["FriendTodoView"]]  = relationship("FriendTodoView", back_populates="todo", cascade="all, delete-orphan")
    histories:         Mapped[List["History"]]         = relationship("History", back_populates="todo", cascade="all, delete-orphan")