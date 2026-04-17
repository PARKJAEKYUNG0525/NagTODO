from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, func
from typing import Optional, List, TYPE_CHECKING

# 서로 import(=순환 참조) 할 때 문제 발생할 수 있기에
# DB 연결할 때 때 한 쪽은 그냥 from ~ import를 했으면 한 쪽은 TYPE_CHECKING 하도록
# => 타입 검사 시에만 import해서 Board 인식만 가능하게 하는 것
# Q. 근데 양쪽 다 하면 안 되나
if TYPE_CHECKING:
    from .board import Board

#orm타입힌트 -> 새로운 타입 힌트방식 -> Mapped => 각필드의 특정타입을 좀 더 명확히 정의가능
class User(Base):
    __tablename__="users2"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] =mapped_column(String(40), nullable=False)
    email: Mapped[str] =mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] =mapped_column(String(300), nullable=False)
    refresh_token: Mapped[Optional[str]] =mapped_column(String(255), nullable=True)
    created_at: Mapped[Optional[datetime]] =mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)

    boards: Mapped[List["Board"]] = relationship("Board", back_populates="users2", cascade="all, delete-orphan")

    