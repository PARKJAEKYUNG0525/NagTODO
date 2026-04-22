from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.music import Music

class MusicCrud:

    # C 생성
    @staticmethod
    async def create_music(db: AsyncSession, music_id: str, title: str, homepage_id: str) -> Music:
        music = Music(
            music_id=music_id,
            title=title,
            homepage_id=homepage_id
        )
        db.add(music)
        await db.flush()
        return music

    # R 조회 - 단일 조회
    @staticmethod
    async def get_music(db: AsyncSession, music_id: str) -> Music | None:
        result = await db.execute(
            select(Music).where(Music.music_id == music_id)
        )
        return result.scalar_one_or_none()

    # R 조회 - 목록 조회 (homepage 기준)
    @staticmethod
    async def get_all_musics_by_homepage(db: AsyncSession, homepage_id: str):
        result = await db.execute(
            select(Music).where(Music.homepage_id == homepage_id)
        )
        return list(result.scalars().all())

    # D 삭제
    @staticmethod
    async def delete_music(db: AsyncSession, music: Music):
        await db.delete(music)
        await db.flush()