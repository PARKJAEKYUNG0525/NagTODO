from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TIMESTAMP, ForeignKey, func,Integer
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class PwHistory(Base):
    __tablename__ = "pw_history"

    pw_history_id: Mapped[str]      = mapped_column(String(100), primary_key=True)
    user_id:       Mapped[int]      = mapped_column(Integer, ForeignKey("user.user_id"))
    pw:            Mapped[str]      = mapped_column(String(255), nullable=False)
    updated_at:    Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="pw_histories")