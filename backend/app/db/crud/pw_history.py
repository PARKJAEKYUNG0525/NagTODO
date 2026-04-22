from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.db.models.pw_history import PwHistory

class PwHistoryCrud:

    # R 조회 - user 비밀번호 변경 이력 조회
    @staticmethod
    async def get_pw_histories(db: AsyncSession, user_id: str) -> list[PwHistory]:
        result = await db.execute(select(PwHistory)
                                  .where(PwHistory.user_id == user_id)
                                  .order_by(desc(PwHistory.updated_at)))
        return list(result.scalars().all())
