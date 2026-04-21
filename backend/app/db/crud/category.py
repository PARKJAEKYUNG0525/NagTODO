from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.category import Category
from app.db.scheme.category import CategoryCreate, CategoryUpdate

class CategoryCrud:

    # C 생성
    @staticmethod
    async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
        category = Category(**data.model_dump())
        db.add(category)
        await db.flush()
        return category

    # R 조회 - 단일 조회
    @staticmethod
    async def get_category(db: AsyncSession, category_id: str) -> Category | None:
        result = await db.execute(select(Category).where(Category.category_id == category_id))
        return result.scalar_one_or_none()

    # R 조회 - 전체 조회
    @staticmethod
    async def get_all_categories(db: AsyncSession) -> list[Category]:
        result = await db.execute(select(Category))
        return list(result.scalars().all())

    # U 수정
    @staticmethod
    async def update_category(db: AsyncSession, category: Category, data: CategoryUpdate) -> Category:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)
        await db.flush()
        return category

    # D 삭제
    @staticmethod
    async def delete_category(db: AsyncSession, category: Category) -> None:
        await db.delete(category)
        await db.flush()