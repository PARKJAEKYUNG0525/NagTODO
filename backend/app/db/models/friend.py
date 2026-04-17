from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, TIMESTAMP, Enum, ForeignKey, func
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class Friend(Base):
    __tablename__ = "friend"

    friend_id:    Mapped[int] = mapped_column(primary_key=True)
    status:       Mapped[str] = mapped_column(Enum("대기", "수락", "거절", "차단"), nullable=False, default="대기")
    created_at:   Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    receiver_id:  Mapped[str] = mapped_column(String(100), ForeignKey("user.user_id"), unique=True, nullable=False)
    requester_id: Mapped[str] = mapped_column(String(100), ForeignKey("user.user_id"), unique=True, nullable=False)

    requester: Mapped["User"] = relationship("User", foreign_keys=[requester_id], back_populates="friends_sent")
    receiver:  Mapped["User"] = relationship("User", foreign_keys=[receiver_id],  back_populates="friends_received")