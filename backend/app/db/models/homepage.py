# from app.db.database import Base
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy import String, ForeignKey,Integer
# from typing import List, TYPE_CHECKING, Optional
#
# if TYPE_CHECKING:
#     from .user import User
#     from .img import Img
#     from .music import Music
#
# class Homepage(Base):
#     __tablename__ = "homepage"
#
#     homepage_id: Mapped[str] = mapped_column(String(100), primary_key=True)
#     user_id:     Mapped[int] = mapped_column(Integer, ForeignKey("user.user_id"), nullable=False)
#
#     music_id: Mapped[Optional[str]] = mapped_column(
#         String(100),
#         ForeignKey("music.music_id"),
#         nullable=True
#     )
#     img_id: Mapped[Optional[str]] = mapped_column(
#         String(100),
#         ForeignKey("img.img_id"),
#         nullable=True
#     )
#
#     user:  Mapped["User"]        = relationship("User", back_populates="homepages")
#     img:   Mapped[List["Img"]]   = relationship("Img", back_populates="homepage")
#     music: Mapped[List["Music"]] = relationship("Music", back_populates="homepage")