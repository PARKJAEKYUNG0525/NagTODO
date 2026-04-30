from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.history import HistoryCreate, HistoryUpdate, HistoryRead
from app.services.history import HistoryService as history_svc

router = APIRouter(prefix="/history", tags=["History"])

# R 조회 - AI 서버 리포트용 월간 로그 (text, completed, category)
@router.get("/monthly-logs", response_model=list[dict])
async def get_monthly_logs(
    user_id: int = Query(...),
    month_start: str = Query(..., description="YYYY-MM-DD"),
    month_end: str = Query(..., description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
):
    return await history_svc.get_monthly_logs_svc(db, user_id, month_start, month_end)

# R 전체 조회
@router.get("/", response_model=list[HistoryRead])
async def get_all_history(db: AsyncSession = Depends(get_db)):
    return await history_svc.get_all_history_svc(db)

# R 유저별 조회
@router.get("/user/{user_id}", response_model=list[HistoryRead])
async def get_history_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await history_svc.get_user_svc(db, user_id)

# C 생성
@router.post("/", response_model=HistoryRead, status_code=201)
async def create_history(data: HistoryCreate, db: AsyncSession = Depends(get_db)):
    return await history_svc.create_history_svc(db, data)

# R 단일 조회
@router.get("/{history_id}", response_model=HistoryRead)
async def get_history(history_id: str, db: AsyncSession = Depends(get_db)):
    return await history_svc.get_history_svc(db, history_id)

# U 수정
@router.patch("/{history_id}", response_model=HistoryRead)
async def update_history(history_id: str, data: HistoryUpdate, db: AsyncSession = Depends(get_db)):
    return await history_svc.update_history_svc(db, history_id, data)

# D 삭제
@router.delete("/{history_id}")
async def delete_history(history_id: str, db: AsyncSession = Depends(get_db)):
    return await history_svc.delete_history_svc(db, history_id)
