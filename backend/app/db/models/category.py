from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .todo import Todo

class Category(Base):
    __tablename__ = "category"

    category_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name:        Mapped[str] = mapped_column(String(50), nullable=False)

    todos: Mapped[List["Todo"]] = relationship("Todo", back_populates="category")