from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.cloth import Cloth
from app.db.models.user import User
from app.db.scheme.cloth import ClothCreate, ClothUpdate

class ClothCrud:

    # C 생성
    @staticmethod
    async def create_cloth(db: AsyncSession, data: ClothCreate) -> Cloth:
        cloth = Cloth(**data.model_dump())
        db.add(cloth)
        await db.flush()
        return cloth

    # R 조회 - user 존재 확인
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    # R 조회 - cloth 단일 조회
    @staticmethod
    async def get_cloth(db: AsyncSession, cloth_id: str) -> Cloth | None:
        result = await db.execute(select(Cloth).where(Cloth.cloth_id == cloth_id))
        return result.scalar_one_or_none()

    # R 조회 - cloth 전체 조회 (user 기준)
    @staticmethod
    async def get_all_cloths(db: AsyncSession, user_id: int) -> list[Cloth]:
        result = await db.execute(select(Cloth).where(Cloth.user_id == user_id))
        return list(result.scalars().all())

    # U 수정
    @staticmethod
    async def update_cloth(db: AsyncSession, cloth: Cloth, data: ClothUpdate) -> Cloth:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(cloth, key, value)
        await db.flush()
        return cloth

    # D 삭제
    @staticmethod
    async def delete_cloth(db: AsyncSession, cloth: Cloth) -> None:
        await db.delete(cloth)
        await db.flush()