from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.history import HistoryCreate, HistoryUpdate, HistoryRead
from app.services.history import HistoryService as history_svc

router = APIRouter(prefix="/history", tags=["History"])

# C 생성
@router.post("/", response_model=HistoryRead, status_code=201)
async def create_history(data: HistoryCreate, db: AsyncSession = Depends(get_db)):
    return await history_svc.create_history_svc(db, data)

# R 단일 조회
@router.get("/{history_id}", response_model=HistoryRead)
async def get_history(history_id: str, db: AsyncSession = Depends(get_db)):
    return await history_svc.get_history_svc(db, history_id)

# R 단일 조회 - 유저별
@router.get("/{user_id}", response_model=list[HistoryRead])
async def get_history_by_user(user_id: str, db: AsyncSession = Depends(get_db)):
    return await history_svc.get_user_svc(db, user_id)

# R 전체 조회
@router.get("/", response_model=list[HistoryRead])
async def get_all_history(db: AsyncSession = Depends(get_db)):
    return await history_svc.get_all_history_svc(db)

# U 수정
@router.patch("/{history_id}", response_model=HistoryRead)
async def update_todo(history_id: str, data: HistoryUpdate, db: AsyncSession = Depends(get_db)):
    return await history_svc.update_history_svc(db, history_id, data)

# D 삭제
@router.delete("/{history_id}")
async def delete_todo(history_id: str, db: AsyncSession = Depends(get_db)):
    return await history_svc.delete_history_svc(db, history_id)