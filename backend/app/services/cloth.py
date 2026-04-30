from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.cloth import ClothCrud as cloth_crud
from app.db.scheme.cloth import ClothCreate, ClothUpdate
from app.db.models.cloth import Cloth

class ClothService:

    # C 생성
    @staticmethod
    async def create_cloth_svc(db: AsyncSession, data: ClothCreate) -> Cloth:
        # user 존재 확인
        user = await cloth_crud.get_user(db, data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{data.user_id}'에 해당하는 유저가 없습니다."
            )
        
        try:
            cloth = await cloth_crud.create_cloth(db, data)
            await db.commit()
            await db.refresh(cloth)
            return cloth

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cloth 생성에 실패했습니다."
            )

    # R 조회 - 전체 조회
    @staticmethod
    async def get_all_cloth_svc(db: AsyncSession) -> list[Cloth]:
        return await cloth_crud.get_all_cloths(db)

    # R 조회 - cloth 단일 조회
    @staticmethod
    async def get_cloth_svc(db: AsyncSession, cloth_id: str) -> Cloth:
        cloth = await cloth_crud.get_cloth(db, cloth_id)
        if not cloth:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"cloth_id '{cloth_id}'에 해당하는 cloth가 없습니다."
            )
        return cloth

    # R 조회 - cloth 조회 (user 기준)
    # @staticmethod
    # async def get_cloth_by_user_svc(db: AsyncSession, user_id: int) -> Cloth:
    #     user = await cloth_crud.get_user(db, user_id)
    #     if not user:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail=f"user_id '{user_id}'에 해당하는 유저가 없습니다."
    #         )
    #
    #     cloths = await cloth_crud.get_cloth_by_user(db, user_id)
    #     return cloths

    # U 수정
    @staticmethod
    async def update_cloth_svc(db: AsyncSession, cloth_id: str, data: ClothUpdate) -> Cloth:
        cloth = await cloth_crud.get_cloth(db, cloth_id)
        if not cloth:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"cloth_id '{cloth_id}'에 해당하는 cloth가 없습니다."
            )

        try:
            updated = await cloth_crud.update_cloth(db, cloth, data)
            await db.commit()
            await db.refresh(updated)
            return updated

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cloth 수정에 실패했습니다."
            )
        
    # D 삭제
    @staticmethod
    async def delete_cloth_svc(db: AsyncSession, cloth_id: str) -> dict:
        cloth = await cloth_crud.get_cloth(db, cloth_id)
        if not cloth:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"cloth_id '{cloth_id}'에 해당하는 cloth가 없습니다."
            )

        try:
            await cloth_crud.delete_cloth(db, cloth)
            await db.commit()
            return {"message": f"cloth_id '{cloth_id}' 삭제 완료"}

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cloth 삭제에 실패했습니다."
            )