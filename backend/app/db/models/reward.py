from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from .user import User
    from .cloth import Cloth

class Reward(Base):
    __tablename__ = "reward"

    user_id:     Mapped[int]      = mapped_column(Integer, ForeignKey("user.user_id"), primary_key=True)
    cloth_id:    Mapped[str]      = mapped_column(String(100), ForeignKey("cloth.cloth_id"), primary_key=True)
    unlocked_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    user:  Mapped["User"]  = relationship("User", back_populates="reward")
    cloth: Mapped["Cloth"] = relationship("Cloth")