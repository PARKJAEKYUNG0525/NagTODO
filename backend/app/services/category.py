from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.category import CategoryCrud 
from app.db.scheme.category import CategoryCreate, CategoryUpdate
from app.db.models.category import Category

class CategoryService:

    # C 생성
    @staticmethod
    async def create_category_svc(db: AsyncSession, data: CategoryCreate) -> Category:

        try:
            category = await CategoryCrud.create_category(db, data)
            await db.commit()
            await db.refresh(category)
            return category

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="카테고리 생성에 실패했습니다."
            )

    # R 조회 - category 단일 조회
    @staticmethod
    async def get_category_svc(db: AsyncSession, category_id: str) -> Category:
        category = await CategoryCrud.get_category(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"category_id '{category_id}'에 해당하는 카테고리가 없습니다."
            )
        return category

    # R 조회 - category 목록 조회
    @staticmethod
    async def get_all_categories_svc(db: AsyncSession) -> list[Category]:
        category = await CategoryCrud.get_all_categories(db)
        return category

    # U 수정
    @staticmethod
    async def update_category_svc(db: AsyncSession, category_id: str, data: CategoryUpdate) -> Category:
        category = await CategoryCrud.get_category(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"category_id '{category_id}'에 해당하는 카테고리가 없습니다."
            )

        try:
            updated = await CategoryCrud.update_category(db, category, data)
            await db.commit()
            await db.refresh(updated)
            return updated

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="카테고리 수정에 실패했습니다."
            )
        
    # D 삭제
    @staticmethod
    async def delete_category_svc(db: AsyncSession, category_id: str) -> dict:
        category = await CategoryCrud.get_category(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"category_id '{category_id}'에 해당하는 카테고리가 없습니다."
            )

        try:
            await CategoryCrud.delete_category(db, category)
            await db.commit()
            return {"message": f"category_id '{category_id}' 삭제 완료"}

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="카테고리 삭제에 실패했습니다."
            )