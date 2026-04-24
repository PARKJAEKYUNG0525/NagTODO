from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.history import History
from app.db.models.todo import Todo
from app.db.scheme.history import HistoryCreate, HistoryUpdate

class HistoryCrud:

    # C 생성
    @staticmethod
    async def create_history(db: AsyncSession, data: HistoryCreate) -> History:
        history = History(**data.model_dump())
        db.add(history)
        await db.flush()
        return history

    # R 조회 - todo 존재 확인
    @staticmethod
    async def get_todo(db: AsyncSession, todo_id: str) -> Todo | None:
        result = await db.execute(select(Todo).where(Todo.todo_id == todo_id))
        return result.scalar_one_or_none()

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

    # U 수정
    @staticmethod
    async def update_history(db: AsyncSession, history: History, data: HistoryUpdate) -> Todo:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(history, key, value)
        await db.flush()
        return history

    # D 삭제
    @staticmethod
    async def delete_history(db: AsyncSession, history: History) -> None:
        await db.delete(history)
        await db.flush()