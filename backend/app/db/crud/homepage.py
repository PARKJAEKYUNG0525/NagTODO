from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.user import User
from app.db.models.homepage import Homepage

class HomepageCrud:

    # C 생성
    @staticmethod
    async def create_homepage(db: AsyncSession, homepage_id: str, user_id: str) -> Homepage:
        homepage = Homepage(
            homepage_id=homepage_id,
            user_id=user_id
        )
        db.add(homepage)
        await db.flush()
        return homepage

    # R 조회 - user 존재 확인
    @staticmethod
    async def get_user(db: AsyncSession, user_id: str) -> User | None:
        result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    # R 조회 - 단일 조회
    @staticmethod
    async def get_homepage(db: AsyncSession, homepage_id: str) -> Homepage | None:
        result = await db.execute(
            select(Homepage).where(Homepage.homepage_id == homepage_id)
        )
        return result.scalar_one_or_none()

    # R 조회 - user 기준
    @staticmethod
    async def get_homepage_by_user(db: AsyncSession, user_id: str) -> Homepage | None:
        result = await db.execute(
            select(Homepage).where(Homepage.user_id == user_id)
        )
        return result.scalar_one_or_none()

    # R 전체 조회
    @staticmethod
    async def get_all_homepages(db: AsyncSession) -> list[Homepage]:
        result = await db.execute(select(Homepage))
        return list(result.scalars().all())

    # D 삭제
    @staticmethod
    async def delete_homepage(db: AsyncSession, homepage: Homepage) -> None:
        await db.delete(homepage)
        await db.flush()