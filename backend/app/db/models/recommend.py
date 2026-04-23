from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, ForeignKey,Integer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class Recommend(Base):
    __tablename__ = "recommend"

    recommend_id: Mapped[int]  = mapped_column(primary_key=True)
    content:      Mapped[str]  = mapped_column(Text, nullable=False)
    basis:        Mapped[str]  = mapped_column(String(255), nullable=False)
    is_read:      Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    user_id:      Mapped[int]  = mapped_column(Integer, ForeignKey("user.user_id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="recommends")