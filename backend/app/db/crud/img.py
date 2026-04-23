from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.homepage import Homepage
from app.db.models.img import Img
from app.db.scheme.img import ImgCreate, ImgUpdate

class ImgCrud:

    # C 생성
    @staticmethod
    async def create_img(db: AsyncSession, data: ImgCreate) -> Img:
        img = Img(**data.model_dump())
        db.add(img)
        await db.flush()
        return img

    # R 조회 - homepage 존재 확인
    @staticmethod
    async def get_homepage(db: AsyncSession, homepage_id: str) -> Homepage | None:
        result = await db.execute(select(Homepage).where(Homepage.homepage_id == homepage_id))
        return result.scalar_one_or_none()

    # R 조회 - 단일 조회
    @staticmethod
    async def get_img(db: AsyncSession, img_id: str) -> Img | None:
        result = await db.execute(select(Img).where(Img.img_id == img_id))
        return result.scalar_one_or_none()

    # R 조회 - 목록 조회 (homepage 기준)
    @staticmethod
    async def get_all_imgs_by_homepage(db: AsyncSession, homepage_id: str) -> list[Img]:
        result = await db.execute(select(Img).where(Img.homepage_id == homepage_id))
        return list(result.scalars().all())

    # U 수정
    @staticmethod
    async def update_img(db: AsyncSession, img: Img, data: ImgUpdate) -> Img:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(img, key, value)
        await db.flush()
        return img

    # D 삭제
    @staticmethod
    async def delete_img(db: AsyncSession, img: Img) -> None:
        await db.delete(img)
        await db.flush()