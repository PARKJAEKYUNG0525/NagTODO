from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.user import User
from app.db.scheme.user import UserCreate, UserUpdate

class UserCrud:

    # C 생성
    @staticmethod
    async def create_user(db: AsyncSession, data: UserCreate) -> User:
        user = User(**data.model_dump())
        db.add(user)
        await db.flush()
        return user

    # R 조회 - user 확인
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    # R 조회 - username 확인
    @staticmethod
    async def get_username(db: AsyncSession, username: str) -> User | None:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    # R 조회 - email 확인
    @staticmethod
    async def get_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    # R 조회 - 전체 조회
    @staticmethod
    async def get_all_users(db: AsyncSession) -> list[User]:
        result = await db.execute(select(User))
        return list(result.scalars().all())

    # U 수정
    @staticmethod
    async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        await db.flush()
        return user

    # R 조회 - 닉네임 또는 이메일로 검색
    @staticmethod
    async def search_users(db: AsyncSession, query: str, current_user_id: int) -> list[User]:
        result = await db.execute(
            select(User).where(
                (User.username.ilike(f"%{query}%") | User.email.ilike(f"%{query}%")),
                User.user_id != current_user_id  # 본인 제외
            )
        )
        return list(result.scalars().all())

    # D 삭제
    @staticmethod
    async def delete_user(db: AsyncSession, user: User) -> None:
        await db.delete(user)
        await db.flush()

    # refresh_token 업데이트
    @staticmethod
    async def update_refresh_token_by_id(db:AsyncSession, user_id: int, refresh_token: str):
        db_user = await db.get(User, user_id)
        if db_user:
            db_user.refresh_token = refresh_token
            await db.flush()
        return db_user