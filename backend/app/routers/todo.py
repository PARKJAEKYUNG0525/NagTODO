import calendar

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.todo import TodoCreate, TodoUpdate, TodoRead, TodoCreateResponse, MonthlyStatsResponse
from app.services.todo import TodoService as todo_svc

router = APIRouter(prefix="/todos", tags=["Todo"])

# C 생성
@router.post("/", response_model=TodoCreateResponse, status_code=201)
async def create_todo(data: TodoCreate, db: AsyncSession = Depends(get_db)):
    return await todo_svc.create_todo_svc(db, data)

# R 단일 조회
@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(todo_id: str, db: AsyncSession = Depends(get_db)):
    return await todo_svc.get_todo_svc(db, todo_id)

# R 전체 조회 - 유저별
@router.get("/user/{user_id}", response_model=list[TodoRead])
async def get_todos_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await todo_svc.get_all_todos_svc(db, user_id)

# U 수정
@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(todo_id: str, data: TodoUpdate, db: AsyncSession = Depends(get_db)):
    return await todo_svc.update_todo_svc(db, todo_id, data)

# D 삭제
@router.delete("/{todo_id}")
async def delete_todo(todo_id: str, db: AsyncSession = Depends(get_db)):
    return await todo_svc.delete_todo_svc(db, todo_id)


# R 월간 통계 조회 (유저 성공률, 전체 사용자 성공률, 카테고리별 달성률)
@router.get("/stats", response_model=MonthlyStatsResponse)
async def get_monthly_stats(
    user_id: int = Query(...),
    month_start: str = Query(..., description="YYYY-MM-DD"),
    month_end: str = Query(..., description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
):
    return await todo_svc.get_monthly_stats_svc(db, user_id, month_start, month_end)