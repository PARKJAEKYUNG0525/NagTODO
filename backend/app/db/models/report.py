import uuid
from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Integer
from typing import Optional

class Report(Base):
    __tablename__ = "report"

    report_id:   Mapped[str]           = mapped_column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    title:       Mapped[str]           = mapped_column(String(255), nullable=False)
    date:        Mapped[DateTime]      = mapped_column(DateTime, nullable=False)
    detail:      Mapped[str]           = mapped_column(Text, nullable=False)
    user_id:     Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    month_start: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    month_end:   Mapped[Optional[str]] = mapped_column(String(10), nullable=True)