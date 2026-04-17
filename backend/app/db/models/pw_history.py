from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TIMESTAMP, ForeignKey, func
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class PwHistory(Base):
    __tablename__ = "pw_history"

    user_id:    Mapped[str]      = mapped_column(String(100), ForeignKey("user.user_id"), primary_key=True)
    pw:         Mapped[str]      = mapped_column(String(255), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="pw_histories")