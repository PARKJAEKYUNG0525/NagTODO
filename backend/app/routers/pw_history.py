from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.pw_history import PwHistoryUpdate, PwHistoryRead
from app.services.pw_history import PwHistoryService as pwhistory_svc

router = APIRouter(prefix="/pwhistory", tags=["PwHistory"])

# R 단일 조회
@router.get("/{pw_history_id}", response_model=PwHistoryRead)
async def get_pw_history(pw_history_id: str, db: AsyncSession = Depends(get_db)):
    return await pwhistory_svc.get_pw_history_svc(db, pw_history_id)

# R 전체 조회
@router.get("/user/{user_id}", response_model=list[PwHistoryRead])
async def get_todos_by_user(user_id: str, db: AsyncSession = Depends(get_db)):
    return await pwhistory_svc.get_all_pw_histories_svc(db, user_id)

# U 수정 #성공 시 트리거 실행
@router.patch("/{pw_history_id}", response_model=PwHistoryRead)
async def update_pw_history(pw_history_id: str, 
                            data: PwHistoryUpdate, 
                            db: AsyncSession = Depends(get_db),
                            old_pw: str=Body(...),
                            new_pw: str=Body(...)):
    return await pwhistory_svc.update_pw_history_svc(db, pw_history_id, data, old_pw, new_pw)

# D 삭제
@router.delete("/{pw_history_id}")
async def delete_todo(pw_history_id: str, db: AsyncSession = Depends(get_db)):
    return await pwhistory_svc.delete_pw_history(db, pw_history_id)