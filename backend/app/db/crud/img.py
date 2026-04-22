from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.img import Img

class ImgCrud:

    # C 생성
    @staticmethod
    async def create_img(db: AsyncSession, img_id: str, title: str, homepage_id: str) -> Img:
        img = Img(
            img_id=img_id,
            title=title,
            homepage_id=homepage_id
        )
        db.add(img)
        await db.flush()
        return img

    # R 조회 - 단일 조회
    @staticmethod
    async def get_img(db: AsyncSession, img_id: str) -> Img | None:
        result = await db.execute(
            select(Img).where(Img.img_id == img_id)
        )
        return result.scalar_one_or_none()

    # R 조회 - 목록 조회 (homepage 기준)
    @staticmethod
    async def get_all_imgs_by_homepage(db: AsyncSession, homepage_id: str):
        result = await db.execute(
            select(Img).where(Img.homepage_id == homepage_id)
        )
        return list(result.scalars().all())

    # D 삭제
    @staticmethod
    async def delete_img(db: AsyncSession, img: Img):
        await db.delete(img)
        await db.flush()