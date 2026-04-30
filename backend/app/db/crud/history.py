from datetime import datetime

from sqlalchemy import func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.scheme.history import HistoryCreate, HistoryUpdate
from app.db.models.history import History

class HistoryCrud:

    # C 생성
    @staticmethod
    async def create_history(db: AsyncSession, data: HistoryCreate) -> History:
        history = History(**data.model_dump())
        db.add(history)
        await db.flush()
        return history

    # R 조회 - 히스토리 단일 조회
    @staticmethod
    async def get_history(db: AsyncSession, history_id: str) -> History | None:
        result = await db.execute(select(History).where(History.history_id == history_id))
        return result.scalar_one_or_none()

    # R 조회 - 히스토리 목록 조회 (user 기준)
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> list[History]:
        result = await db.execute(select(History).where(History.user_id == user_id))
        return list(result.scalars().all())

    # R 조회 - 히스토리 전체 조회
    @staticmethod
    async def get_all_history(db: AsyncSession) -> list[History]:
        result = await db.execute(select(History))
        return list(result.scalars().all())

    # R 조회 - 유저 카테고리별 월간 달성률 (history.archived_at 기준)
    @staticmethod
    async def get_user_category_stats(
        db: AsyncSession, user_id: int, month_start: str, month_end: str
    ) -> dict[str, dict]:
        start_dt = datetime.strptime(month_start, "%Y-%m-%d")
        end_dt = datetime.strptime(month_end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        stmt = (
            select(
                History.category_name.label("category"),
                func.count().label("total"),
                func.sum(case((History.todo_status == "완료", 1), else_=0)).label("completed"),
            )
            .where(
                History.user_id == user_id,
                History.archived_at >= start_dt,
                History.archived_at <= end_dt,
            )
            .group_by(History.category_name)
        )

        result = await db.execute(stmt)
        return {
            row.category: {
                "total": row.total,
                "completed": row.completed or 0,
                "rate": round((row.completed or 0) / row.total * 100, 1) if row.total > 0 else 0.0,
            }
            for row in result.all()
        }

    # U 수정
    @staticmethod
    async def update_history(db: AsyncSession, history: History, data: HistoryUpdate) -> History:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(history, key, value)
        await db.flush()
        return history

    # R 조회 - AI 서버 리포트용 월간 로그 (text, completed, category 형식)
    @staticmethod
    async def get_monthly_logs(
        db: AsyncSession, user_id: int, month_start: str, month_end: str
    ) -> list[dict]:
        start_dt = datetime.strptime(month_start, "%Y-%m-%d")
        end_dt = datetime.strptime(month_end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        stmt = (
            select(
                History.title.label("text"),
                History.todo_status,
                History.category_name.label("category"),
            )
            .where(
                History.user_id == user_id,
                History.archived_at >= start_dt,
                History.archived_at <= end_dt,
            )
        )
        result = await db.execute(stmt)
        return [
            {
                "text": row.text,
                "completed": row.todo_status == "완료",
                "category": row.category,
            }
            for row in result.all()
        ]

    # D 삭제
    @staticmethod
    async def delete_history(db: AsyncSession, history: History) -> None:
        await db.delete(history)
        await db.flush()
