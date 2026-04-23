import uuid
from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TIMESTAMP, Enum, ForeignKey,Integer
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .todo import Todo

class History(Base):
    __tablename__ = "history"

    history_id:  Mapped[str]      = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id:     Mapped[str]      = mapped_column(Integer, nullable=False)
    title:       Mapped[str]      = mapped_column(String(255), nullable=False)
    todo_status: Mapped[str]      = mapped_column(Enum("완료", "실패"), nullable=False)
    archived_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    todo_id:     Mapped[str]      = mapped_column(String(100), ForeignKey("todo.todo_id"), nullable=False)

    todo: Mapped["Todo"] = relationship("Todo", back_populates="histories")