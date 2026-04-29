from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.scheme.music import MusicCreate, MusicUpdate, MusicRead
from app.services.music import MusicService as music_svc

router = APIRouter(prefix="/musics", tags=["Music"])

# C 생성
@router.post("/", response_model=MusicRead, status_code=201)
async def create_music(data: MusicCreate, db: Session = Depends(get_db)):
    return await music_svc.create_music_svc(db, data)

# R 조회 - 전체 조회
@router.get("/", response_model=list[MusicRead])
async def get_all_musics(db: Session = Depends(get_db)):
    return await music_svc.get_all_musics_svc(db)

# R 조회 - 단일 조회
@router.get("/{music_id}", response_model=MusicRead)
async def get_music(music_id: str, db: Session = Depends(get_db)):
    return await music_svc.get_music_svc(db, music_id)

# R 조회 - homepage 기준 조회
# @router.get("/homepage/{homepage_id}", response_model=MusicRead)
# def get_music_by_homepage(homepage_id: str, db: Session = Depends(get_db)):
#     return music_svc.get_music_by_homepage_svc(db, homepage_id)

# U 수정
@router.patch("/{music_id}", response_model=MusicRead)
async def update_music(music_id: str, data: MusicUpdate, db: Session = Depends(get_db)):
    return await music_svc.update_music_svc(db, music_id, data)

# D 삭제
@router.delete("/{music_id}")
async def delete_music(music_id: str, db: Session = Depends(get_db)):
    return await music_svc.delete_music_svc(db, music_id)