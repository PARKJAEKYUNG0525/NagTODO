from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.todo import Todo
from app.db.models.user import User
from app.db.models.category import Category
from app.db.scheme.todo import TodoCreate, TodoUpdate

class TodoCrud:

    # C 생성
    @staticmethod
    async def create_todo(db: AsyncSession, data: TodoCreate) -> Todo:
        todo = Todo(**data.model_dump())
        db.add(todo)
        await db.flush()
        return todo

    # R 조회 - user 존재 확인
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    # R 조회 - category 존재 확인
    @staticmethod
    async def get_category(db: AsyncSession, category_id: str) -> Category | None:
        result = await db.execute(select(Category).where(Category.category_id == category_id))
        return result.scalar_one_or_none()

    # R 조회 - todo 단일 조회
    @staticmethod
    async def get_todo(db: AsyncSession, todo_id: str) -> Todo | None:
        result = await db.execute(select(Todo).where(Todo.todo_id == todo_id))
        return result.scalar_one_or_none()

    # R 조회 - todo 목록 조회 (user 기준)
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> list[Todo]:
        result = await db.execute(select(Todo).where(Todo.user_id == user_id))
        return list(result.scalars().all())
    
    # R 조회 - 전체 조회
    @staticmethod
    async def get_all_todos(db: AsyncSession) -> list[Todo]:
        result = await db.execute(select(Todo))
        return list(result.scalars().all())

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