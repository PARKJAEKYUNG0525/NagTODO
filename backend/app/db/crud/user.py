from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload

from app.db.models.user import User
from app.db.models.friend import Friend
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
        result = await db.execute(
            select(User)
            .options(selectinload(User.reward))
            .where(User.user_id == user_id))
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

    # U 수정 - state 변경
    @staticmethod
    async def update_state_by_id(db: AsyncSession, user_id: int, state: bool):
        user = await UserCrud.get_user(db, user_id)
        user.state = state
        return user

    # R 조회 - 닉네임 또는 이메일로 검색
    @staticmethod
    async def search_users(db: AsyncSession, query: str, current_user_id: int) -> list[User]:
        # 이미 친구 관계인 user_id 목록 조회
        friend_result = await db.execute(
            select(Friend).where(
                (Friend.requester_id == current_user_id) | (Friend.receiver_id == current_user_id),
                Friend.status.in_(["대기", "수락"])  # 대기 중이거나 수락된 친구 제외
            )
        )
        friends = friend_result.scalars().all()

        # 친구 id 목록 추출
        excluded_ids = set()
        for f in friends:
            if f.requester_id == current_user_id:
                excluded_ids.add(f.receiver_id)
            else:
                excluded_ids.add(f.requester_id)

        # 검색 쿼리
        result = await db.execute(
            select(User).where(
                (User.username.ilike(f"%{query}%") | User.email.ilike(f"%{query}%")),
                User.user_id != current_user_id,  # 본인 제외
                User.user_id.notin_(excluded_ids)  # 친구 제외
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