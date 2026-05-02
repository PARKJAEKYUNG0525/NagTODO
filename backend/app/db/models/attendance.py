from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from .user import User

class Attendance(Base):
    __tablename__ = "attendance"

    user_id:     Mapped[int]  = mapped_column(Integer, ForeignKey("user.user_id"), primary_key=True)
    attended_at: Mapped[date] = mapped_column(Date, primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="attendance")