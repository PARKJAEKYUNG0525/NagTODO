from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.music import MusicCreate, MusicUpdate, MusicResponse
from app.services.music import MusicService as music_svc

router = APIRouter(prefix="/musics", tags=["Music"])

# C 생성
@router.post("/", response_model=MusicResponse, status_code=201)
async def create_music(data: MusicCreate, db: AsyncSession = Depends(get_db)):
    return await music_svc.create_music_svc(db, data)

# R 단일 조회
@router.get("/{music_id}", response_model=MusicResponse)
async def get_music(music_id: str, db: AsyncSession = Depends(get_db)):
    return await music_svc.get_music_svc(db, music_id)

# R homepage 기준 조회
@router.get("/homepage/{homepage_id}", response_model=list[MusicResponse])
async def get_musics_by_homepage(homepage_id: str, db: AsyncSession = Depends(get_db)):
    return await music_svc.get_all_musics_by_homepage_svc(db, homepage_id)

# D 삭제
@router.delete("/{music_id}")
async def delete_music(music_id: str, db: AsyncSession = Depends(get_db)):
    return await music_svc.delete_music_svc(db, music_id)