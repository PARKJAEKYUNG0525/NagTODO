from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.img import ImgCrud
from app.db.scheme.img import ImgCreate, ImgUpdate
from app.db.models.img import Img


class ImgService:

    # C 생성
    @staticmethod
    async def create_img_svc(db: AsyncSession, data: ImgCreate) -> Img:
        # homepage 존재 확인
        homepage = await ImgCrud.get_homepage(db, data.homepage_id)
        if not homepage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"homepage_id '{data.homepage_id}'에 해당하는 homepage가 없습니다."
            )

        try:
            img = await ImgCrud.create_img(db, data)
            await db.commit()
            await db.refresh(img)
            return img

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="img 생성에 실패했습니다."
            )

    # R 조회 - 목록 조회 (homepage 기준)
    @staticmethod
    async def get_all_imgs_svc(db: AsyncSession) -> list[Img]:
        return await ImgCrud.get_all_imgs(db)

    # R 조회 - 단일 조회
    @staticmethod
    async def get_img_svc(db: AsyncSession, img_id: str) -> Img:
        img = await ImgCrud.get_img(db, img_id)
        if not img:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"img_id '{img_id}'에 해당하는 데이터가 없습니다."
            )
        return img

    # R 조회 - 단일 조회 (homepage 기준)
    # @staticmethod
    # async def get_img_by_homepage_svc(db: AsyncSession, homepage_id: str) -> Img:
    #     img = await ImgCrud.get_img_by_homepage(db, homepage_id)
    #     if not img:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail=f"해당 홈페이지 '{homepage_id}'에 적용된 배경이 없습니다."
    #         )
    #
    #     return img

    # U 수정
    @staticmethod
    async def update_img_svc(db: AsyncSession, img_id: str, data: ImgUpdate) -> Img:
        img = await ImgCrud.get_img(db, img_id)
        if not img:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"img_id '{img_id}'에 해당하는 데이터가 없습니다."
            )

        try:
            updated = await ImgCrud.update_img(db, img, data)
            await db.commit()
            await db.refresh(updated)
            return updated

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="img 수정에 실패했습니다."
            )

    # D 삭제
    @staticmethod
    async def delete_img_svc(db: AsyncSession, img_id: str) -> dict:
        img = await ImgCrud.get_img(db, img_id)
        if not img:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"img_id '{img_id}'에 해당하는 데이터가 없습니다."
            )

        try:
            await ImgCrud.delete_img(db, img)
            await db.commit()
            return {"message": f"img_id '{img_id}' 삭제 완료"}

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="img 삭제에 실패했습니다."
            )