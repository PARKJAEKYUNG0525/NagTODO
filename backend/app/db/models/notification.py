from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer, Boolean
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class Notification(Base):
    __tablename__ = "notification"

    notification_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title:           Mapped[str] = mapped_column(String(255), nullable=False)
    content:         Mapped[str] = mapped_column(String(500), nullable=False)
    is_read:         Mapped[bool] = mapped_column(Boolean, default=False)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.user_id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="notifications")