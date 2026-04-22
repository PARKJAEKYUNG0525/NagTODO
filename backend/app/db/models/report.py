from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text

class Report(Base):
    __tablename__ = "report"

    report_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    title:     Mapped[str] = mapped_column(String(255), nullable=False)
    date:      Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    detail:    Mapped[str] = mapped_column(Text, nullable=False)