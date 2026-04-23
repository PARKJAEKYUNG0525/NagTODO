from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.history import HistoryCrud 
from app.db.scheme.history import HistoryCreate, HistoryUpdate
from app.db.models.history import History

class HistoryService:

    # C 생성
    @staticmethod
    async def create_history_svc(db: AsyncSession, data: HistoryCreate) -> History:
        # todo 존재 확인
        todo = await HistoryCrud.get_todo(db, data.todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"todo_id '{data.todo_id}'에 해당하는 todo가 없습니다."
            )

        try:
            history = await HistoryCrud.create_history(db, data)
            await db.commit()
            await db.refresh(history)
            return history

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="history 생성에 실패했습니다."
            )

    # R 조회 - history 단일 조회
    @staticmethod
    async def get_history_svc(db: AsyncSession, history_id: str) -> History:
        history = await HistoryCrud.get_history(db, history_id)
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"history_id '{history_id}'에 해당하는 history가 없습니다."
            )
        return history

    # R 조회 - history 목록 조회 (user 기준)
    @staticmethod
    async def get_user_svc(db: AsyncSession, user_id: str) -> list[History]:
        user = await HistoryCrud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{user_id}'에 해당하는 user가 없습니다."
            )

        history = await HistoryCrud.get_user(db, user_id)
        return history
    
    # R 조회 - history 전체 조회
    @staticmethod
    async def get_all_history_svc(db: AsyncSession) -> list[History]:
        history = await HistoryCrud.get_all_history(db)
        return history

    # U 수정
    @staticmethod
    async def update_history_svc(db: AsyncSession, history_id: str, data: HistoryUpdate) -> History:
        history = await HistoryCrud.get_history(db, history_id)
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"history_id '{history_id}'에 해당하는 history가 없습니다."
            )

        if data.todo_id:
            todo = await HistoryCrud.get_todo(db, data.todo_id)
            if not todo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"todo_id '{data.todo_id}'에 해당하는 todo가 없습니다."
                )

        try:
            updated = await HistoryCrud.update_history(db, history, data)
            await db.commit()
            await db.refresh(updated)
            return updated

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="history 수정에 실패했습니다."
            )
        
    # D 삭제
    @staticmethod
    async def delete_history_svc(db: AsyncSession, history_id: str) -> dict:
        history = await HistoryCrud.get_history(db, history_id)
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"history_id '{history_id}'에 해당하는 history가 없습니다."
            )

        try:
            await HistoryCrud.delete_history(db, history)
            await db.commit()
            return {"message": f"history_id '{history_id}' 삭제 완료"}

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="history 삭제에 실패했습니다."
            )