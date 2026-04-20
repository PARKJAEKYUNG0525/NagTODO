from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.user import User
from app.db.scheme.user import UserCreate, UserUpdate
from typing import Optional

class UserCrud:
    # C 생성
    async def create_user(db: Session, data: UserCreate) -> User:
        user = User(
            email=data.email,
            pw=data.pw,
            username=data.username,
            birthday=data.birthday,
        )
        await db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    # R 조회 - user 확인
    def get_user(db: Session, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.user_id == user_id)
        return db.scalar(stmt)

    # R 조회 - username 확인
    def get_username(db: Session, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        return db.scalar(stmt)

    # R 조회 - email 확인
    def get_email(db: Session, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return db.scalar(stmt)

    # R 조회 - 전체 조회
    def get_all_users(db: Session, user_id: str) -> list[User]:
        stmt = select(User).where(User.user_id == user_id)
        return list(db.scalars(stmt).all())

    # U 수정
    def update_user(db: Session, user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    # D 삭제
    def delete_user(db: Session, user: User) -> None:
        db.delete(user)
        db.commit()
