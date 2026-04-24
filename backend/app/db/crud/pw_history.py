from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.db.models.user import User
from app.db.models.pw_history import PwHistory

class PwHistoryCrud:

    # R 조회 - user 존재 확인
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()
    
    # R 조회 - user 비밀번호 변경 이력 단일 조회
    @staticmethod
    async def get_pw_history(db: AsyncSession, pw_history_id: str) -> PwHistory | None:
        result = await db.execute(select(PwHistory).where(PwHistory.pw_history_id == pw_history_id))
        return result.scalar_one_or_none()

    # R 조회 - user 모든 비밀번호 변경 이력 조회
    @staticmethod
    async def get_all_pw_histories(db: AsyncSession, user_id: int) -> list[PwHistory]:
        result = await db.execute(select(PwHistory)
                                  .where(PwHistory.user_id == user_id)
                                  .order_by(desc(PwHistory.updated_at)))
        return list(result.scalars().all())

    # D 삭제
    @staticmethod
    async def delete_pw_history(db: AsyncSession, pw_history: PwHistory) -> None:
        await db.delete(pw_history)
        await db.flush()