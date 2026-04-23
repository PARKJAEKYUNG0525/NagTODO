from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.scheme.music import MusicCreate, MusicUpdate, MusicResponse
from app.services.music import MusicService as music_svc

router = APIRouter(prefix="/musics", tags=["Music"])

# C 생성
@router.post("/", response_model=MusicResponse, status_code=201)
def create_music(data: MusicCreate, db: Session = Depends(get_db)):
    return music_svc.create_music_svc(db, data)

# R 단일 조회
@router.get("/{music_id}", response_model=MusicResponse)
def get_music(music_id: str, db: Session = Depends(get_db)):
    return music_svc.get_music_svc(db, music_id)

# R homepage 기준 조회
@router.get("/homepage/{homepage_id}", response_model=list[MusicResponse])
def get_musics_by_homepage(homepage_id: str, db: Session = Depends(get_db)):
    return music_svc.get_all_musics_by_homepage_svc(db, homepage_id)

# U 수정
@router.patch("/{music_id}", response_model=MusicResponse)
def update_music(music_id: str, data: MusicUpdate, db: Session = Depends(get_db)):
    return music_svc.update_music_svc(db, music_id, data)

# D 삭제
@router.delete("/{music_id}")
def delete_music(music_id: str, db: Session = Depends(get_db)):
    return music_svc.delete_music_svc(db, music_id)