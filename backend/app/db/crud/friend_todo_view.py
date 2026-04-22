from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.user import User
from app.db.models.todo import Todo
from app.db.models.friend_todo_view import FriendTodoView
from app.db.scheme.friend_todo_view import FriendTodoViewCreate, FriendTodoViewUpdate

class FriendTodoViewCrud:

    # C 생성
    @staticmethod
    async def create_friend_todo_view(db: AsyncSession, data: FriendTodoViewCreate) -> FriendTodoView:
        friend_todo_view = FriendTodoView(**data.model_dump())
        db.add(friend_todo_view)
        await db.flush()
        return friend_todo_view
    
    # R 조회 - user 존재 확인
    @staticmethod
    async def get_user(db: AsyncSession, user_id: str) -> User | None:
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    # R 조회 - category 존재 확인
    @staticmethod
    async def get_todo(db: AsyncSession, todo_id: str) -> Todo | None:
        result = await db.execute(select(Todo).where(Todo.todo_id == todo_id))
        return result.scalar_one_or_none()

    # R 조회 - 단일 조회
    @staticmethod
    async def get_friend_todo_view(db: AsyncSession, friend_todo_view_id: int) -> FriendTodoView | None:
        result = await db.execute(select(FriendTodoView).where(FriendTodoView.friend_todo_view_id == friend_todo_view_id))
        return result.scalar_one_or_none()

    # R 조회 - 목록 조회 (user 기준)
    @staticmethod
    async def get_all_friend_todo_views_by_user(db: AsyncSession, user_id: str) -> list[FriendTodoView]:
        result = await db.execute(select(User).where(User.user_id == user_id))
        return list(result.scalars().all())

    # R 조회 - 목록 조회 (todo 기준)
    @staticmethod
    async def get_all_friend_todo_views_by_todo(db: AsyncSession, todo_id: str) -> list[FriendTodoView]:
        result = await db.execute(select(Todo).where(Todo.todo_id == todo_id))
        return list(result.scalars().all())

    # U 수정
    @staticmethod
    async def update_friend_todo_view(db: AsyncSession, friend_todo_view: FriendTodoView, data: FriendTodoViewUpdate) -> FriendTodoView:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(friend_todo_view, key, value)
        await db.flush()
        return friend_todo_view

    # D 삭제
    @staticmethod
    async def delete_friend_todo_view(db: AsyncSession, friend_todo_view: FriendTodoView) -> None:
        await db.delete(friend_todo_view)
        await db.flush()