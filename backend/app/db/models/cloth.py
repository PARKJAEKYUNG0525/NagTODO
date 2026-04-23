from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey,Integer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class Cloth(Base):
    __tablename__ = "cloth"

    cloth_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id:  Mapped[str] = mapped_column(Integer, ForeignKey("user.user_id"), nullable=False)
    title:    Mapped[str] = mapped_column(String(255), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="cloths")