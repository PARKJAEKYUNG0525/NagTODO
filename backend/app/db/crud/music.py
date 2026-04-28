from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.music import Music
# from app.db.models.homepage import Homepage
from app.db.scheme.music import MusicCreate, MusicUpdate


class MusicCrud:

    # C 생성
    @staticmethod
    async def create_music(db: AsyncSession, data: MusicCreate) -> Music:
        music = Music(**data.model_dump())
        db.add(music)
        await db.flush()
        return music

    # R 조회 - homepage 존재 확인
    # @staticmethod
    # async def get_homepage(db: AsyncSession, homepage_id: str) -> Homepage | None:
    #     result = await db.execute(select(Homepage).where(Homepage.homepage_id == homepage_id))
    #     return result.scalar_one_or_none()

    # R 조회 - 전체 조회
    @staticmethod
    async def get_all_musics(db: AsyncSession) -> list[Music]:
        result = await db.execute(select(Music))
        return list(result.scalars().all())

    # R 조회 - 단일 조회
    @staticmethod
    async def get_music(db: AsyncSession, music_id: str) -> Music | None:
        result = await db.execute(select(Music).where(Music.music_id == music_id))
        return result.scalar_one_or_none()

    # R 조회 - homepage 기준 조회
    # @staticmethod
    # async def get_music_by_homepage(db: AsyncSession, homepage_id: str) -> list[Music]:
    #     result = await db.execute(select(Music).where(Music.homepage_id == homepage_id))
    #     return list(result.scalars().all())

    # U 수정
    @staticmethod
    async def update_music(db: AsyncSession, music: Music, data: MusicUpdate) -> Music:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(music, key, value)
        await db.flush()
        return music

    # D 삭제
    @staticmethod
    async def delete_music(db: AsyncSession, music: Music) -> None:
        await db.delete(music)
        await db.flush()