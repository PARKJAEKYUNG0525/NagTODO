from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.pw_history import PwHistoryCrud as pwhistory_crud
from app.db.models.pw_history import PwHistory
from app.db.crud.user import UserCrud

class PwHistoryService:

    @staticmethod
    async def pw_history_svc(db: AsyncSession, user_id: str, old_pw: str, new_pw: str):
        #user 존재 확인
        user = await UserCrud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{user_id}'에 해당하는 유저가 없습니다."
            )
        
        