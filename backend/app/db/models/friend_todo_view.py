from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey,Integer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .todo import Todo

class FriendTodoView(Base):
    __tablename__ = "friend_todo_view"

    friend_todo_view_id: Mapped[int] = mapped_column(primary_key=True)
    user_id:             Mapped[int] = mapped_column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    todo_id:             Mapped[str] = mapped_column(String(100), ForeignKey("todo.todo_id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="friend_todo_views")
    todo: Mapped["Todo"] = relationship("Todo", back_populates="friend_todo_views")