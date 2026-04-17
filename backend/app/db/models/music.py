from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .homepage import Homepage

class Music(Base):
    __tablename__ = "music"

    music_id:    Mapped[str] = mapped_column(String(100), primary_key=True)
    title:       Mapped[str] = mapped_column(String(255), nullable=False)
    homepage_id: Mapped[str] = mapped_column(String(100), ForeignKey("homepage.homepage_id"), nullable=False)

    homepage: Mapped["Homepage"] = relationship("Homepage", back_populates="musics")