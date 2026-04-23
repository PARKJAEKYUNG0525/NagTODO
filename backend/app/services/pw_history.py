from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.pw_history import PwHistoryCrud
from app.db.scheme.pw_history import PwHistoryUpdate
from app.db.models.pw_history import PwHistory
from app.core.jwt_handle import (
    get_password_hash,
    verify_password
)

class PwHistoryService:

    # R 조회 - user 비밀번호 변경 이력 단일 조회
    @staticmethod
    async def get_pw_history_svc(db: AsyncSession, pw_history_id: str) -> PwHistory:
        pw_history = await PwHistoryCrud.get_pw_history(db, pw_history_id)
        if not pw_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"pw_history_id '{pw_history_id}'에 해당하는 pw_history가 없습니다."
            )
        return pw_history

    # R 조회 - user 모든 비밀번호 변경 이력 조회
    @staticmethod
    async def get_all_pw_histories_svc(db: AsyncSession, user_id: str) -> list[PwHistory]:
        user = await PwHistoryCrud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{user_id}'에 해당하는 유저가 없습니다."
            )

        pw_histories = await PwHistoryCrud.get_all_pw_histories(db, user_id)
        return pw_histories

    # U 수정 (새로운 비밀번호)
    @staticmethod
    async def update_pw_history_svc(db: AsyncSession, data: PwHistoryUpdate, old_pw: str, new_pw: str) -> dict:
        # user 존재 확인
        user = await PwHistoryCrud.get_user(db, data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{data.user_id}'에 해당하는 유저가 없습니다."
            )

        # 현재 비밀번호 일치 확인
        if not verify_password(old_pw, user.pw):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="현재 비밀번호가 일치하지 않습니다."
            )
        
        # 직전 비밀번호와 동일 확인
        if verify_password(new_pw, user.pw):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="새 비밀번호는 직전에 사용한 비밀번호를 사용할 수 없습니다."
            )
        
        try:
            user.pw = get_password_hash(new_pw)
            await db.commit()
            await db.refresh(user)
            return {"message": "비밀번호를 변경했습니다"}
        
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호 변경에 실패했습니다."
            )
        
    # D 삭제
    @staticmethod
    async def delete_pw_history(db: AsyncSession, pw_history_id: str) -> dict:
        pw_history = await PwHistoryCrud.get_pw_history(db, pw_history_id)
        if not pw_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"pw_history_id '{pw_history_id}'에 해당하는 pw_history가 없습니다."
            )

        try:
            await PwHistoryCrud.delete_pw_history(db, pw_history)
            await db.commit()
            return {"message": f"pw_history_id '{pw_history_id}' 삭제 완료"}

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="pw_history 삭제에 실패했습니다."
            )
