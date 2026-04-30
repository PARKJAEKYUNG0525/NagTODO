import uuid
from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, TIMESTAMP, Enum, Integer
from datetime import datetime

class History(Base):
    __tablename__ = "history"

    history_id:    Mapped[str]      = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id:       Mapped[int]      = mapped_column(Integer, nullable=False)
    title:         Mapped[str]      = mapped_column(String(255), nullable=False)
    todo_status:   Mapped[str]      = mapped_column(Enum("시작전", "진행중", "완료"), nullable=False)
    archived_at:   Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    category_name: Mapped[str]      = mapped_column(String(50), nullable=False)
