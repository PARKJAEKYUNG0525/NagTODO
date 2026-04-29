from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.music import MusicCrud
from app.db.scheme.music import MusicCreate, MusicUpdate
from app.db.models.music import Music

class MusicService:

    # C 생성
    @staticmethod
    async def create_music_svc(db: AsyncSession, data: MusicCreate) -> Music:

        # homepage 존재 확인
        homepage = await MusicCrud.get_homepage(db, data.homepage_id)
        if not homepage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"homepage_id '{data.homepage_id}'에 해당하는 homepage가 없습니다."
            )

        try:
            music = await MusicCrud.create_music(db, data)
            await db.commit()
            await db.refresh(music)
            return music

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="music 생성에 실패했습니다."
            )

    # R 조회 - 전체 조회
    @staticmethod
    async def get_all_musics_svc(db: AsyncSession):
        return await MusicCrud.get_all_musics(db)

    # R 조회 - 단일 조회
    @staticmethod
    async def get_music_svc(db: AsyncSession, music_id: str) -> Music:
        music = await MusicCrud.get_music(db, music_id)
        if not music:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"music_id '{music_id}'에 해당하는 데이터가 없습니다."
            )
        return music

    # R 조회 - homepage 기준 조회
    # @staticmethod
    # async def get_music_by_homepage_svc(db: AsyncSession, homepage_id: str):
    #     return await MusicCrud.get_music_by_homepage(db, homepage_id)

    # U 수정
    @staticmethod
    async def update_music_svc(db: AsyncSession, music_id: str, data: MusicUpdate) -> Music:
        music = await MusicCrud.get_music(db, music_id)
        if not music:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"music_id '{music_id}'에 해당하는 데이터가 없습니다."
            )

        try:
            updated_music = await MusicCrud.update_music(db, music, data)
            await db.commit()
            await db.refresh(updated_music)
            return updated_music

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="music 수정에 실패했습니다."
            )

    # D 삭제
    @staticmethod
    async def delete_music_svc(db: AsyncSession, music_id: str):
        music = await MusicCrud.get_music(db, music_id)
        if not music:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"music_id '{music_id}'에 해당하는 데이터가 없습니다."
            )

        try:
            await MusicCrud.delete_music(db, music)
            await db.commit()

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="music 삭제에 실패했습니다."
            )