from datetime import datetime

from sqlalchemy import func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.todo import Todo
from app.db.scheme.todo import TodoCreate, TodoUpdate

class TodoCrud:

    # C 생성
    @staticmethod
    async def create_todo(db: AsyncSession, data: TodoCreate) -> Todo:
        todo = Todo(**data.model_dump())
        db.add(todo)
        await db.flush()
        return todo

    # R 조회 - todo 단일 조회
    @staticmethod
    async def get_todo(db: AsyncSession, todo_id: str) -> Todo | None:
        result = await db.execute(select(Todo).where(Todo.todo_id == todo_id))
        return result.scalar_one_or_none()

    # R 조회 - todo 목록 조회 (user 기준)
    @staticmethod
    async def get_todos_by_user(db: AsyncSession, user_id: int) -> list[Todo]:
        result = await db.execute(select(Todo).where(Todo.user_id == user_id))
        return list(result.scalars().all())

    # R 조회 - 유저 카테고리별 월간 달성률 (todo.created_at 기준)
    @staticmethod
    async def get_user_category_stats(
        db: AsyncSession, user_id: int, month_start: str, month_end: str
    ) -> dict[str, dict]:
        start_dt = datetime.strptime(month_start, "%Y-%m-%d")
        end_dt = datetime.strptime(month_end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        stmt = (
            select(
                Todo.category_id.label("category"),
                func.count().label("total"),
                func.sum(case((Todo.todo_status == "완료", 1), else_=0)).label("completed"),
            )
            .where(
                Todo.user_id == user_id,
                Todo.created_at >= start_dt,
                Todo.created_at <= end_dt,
            )
            .group_by(Todo.category_id)
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

    # R 조회 - 전체 사용자 월간 성공률 (todo.created_at 기준)
    @staticmethod
    async def get_all_users_success_rate(
        db: AsyncSession, month_start: str, month_end: str
    ) -> float:
        start_dt = datetime.strptime(month_start, "%Y-%m-%d")
        end_dt = datetime.strptime(month_end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        stmt = select(
            func.count().label("total"),
            func.sum(case((Todo.todo_status == "완료", 1), else_=0)).label("completed"),
        ).where(Todo.created_at >= start_dt, Todo.created_at <= end_dt)

        result = await db.execute(stmt)
        row = result.one()
        total = row.total or 0
        if total == 0:
            return 0.0
        return round((row.completed or 0) / total * 100, 1)

    # R 조회 - AI 서버 리포트용 월간 로그 (text, completed, category 형식)
    @staticmethod
    async def get_monthly_logs(
        db: AsyncSession, user_id: int, month_start: str, month_end: str
    ) -> list[dict]:
        start_dt = datetime.strptime(month_start, "%Y-%m-%d")
        end_dt = datetime.strptime(month_end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        stmt = (
            select(
                Todo.title.label("text"),
                Todo.todo_status,
                Todo.category_id.label("category"),
            )
            .where(
                Todo.user_id == user_id,
                Todo.created_at >= start_dt,
                Todo.created_at <= end_dt,
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

    # U 수정
    @staticmethod
    async def update_todo(db: AsyncSession, todo: Todo, data: TodoUpdate) -> Todo:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(todo, key, value)
        await db.flush()
        return todo

    # D 삭제
    @staticmethod
    async def delete_todo(db: AsyncSession, todo: Todo) -> None:
        await db.delete(todo)
        await db.flush()
