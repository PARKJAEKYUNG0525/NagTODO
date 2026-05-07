from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class Img(Base):
    __tablename__ = "img"

    img_id:      Mapped[str] = mapped_column(String(100), primary_key=True)
    title:       Mapped[str] = mapped_column(String(255), nullable=False)
    file_url:    Mapped[str] = mapped_column(String(255), nullable=False)