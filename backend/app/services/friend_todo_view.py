from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.friend_todo_view import FriendTodoViewCrud
from app.db.scheme.friend_todo_view import FriendTodoViewCreate, FriendTodoViewUpdate
from app.db.models.friend_todo_view import FriendTodoView

class FriendTodoViewService:

    # C 생성
    @staticmethod
    async def create_friend_todo_view_svc(db: AsyncSession, data: FriendTodoViewCreate) -> FriendTodoView:
        # user 존재 확인
        user = await FriendTodoViewCrud.get_user(db, data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{data.user_id}'에 해당하는 유저가 없습니다."
            )

        # todo 존재 확인
        todo = await FriendTodoViewCrud.get_todo(db, data.todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"todo_id '{data.todo_id}'에 해당하는 todo가 없습니다."
            )
        
        try:
            friend_todo_view = await FriendTodoViewCrud.create_friend_todo_view(db, data)
            await db.commit()
            await db.refresh(friend_todo_view)
            return friend_todo_view

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="friend_todo_view 생성에 실패했습니다."
            )

    # R 조회 - 단일 조회
    @staticmethod
    async def get_friend_todo_view_svc(db: AsyncSession, friend_todo_view_id: int) -> FriendTodoView:
        friend_todo_view = await FriendTodoViewCrud.get_friend_todo_view(db, friend_todo_view_id)
        if not friend_todo_view:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"friend_todo_view_id '{friend_todo_view_id}'에 해당하는 데이터가 없습니다."
            )
        return friend_todo_view

    # R 조회 - 목록 조회 (user 기준)
    @staticmethod
    async def get_all_friend_todo_views_by_user_svc(db: AsyncSession, user_id: int) -> list[FriendTodoView]:
        friend_todo_views = await FriendTodoViewCrud.get_all_friend_todo_views_by_user(db, user_id)
        return friend_todo_views

    # R 조회 - 목록 조회 (todo 기준)
    @staticmethod
    async def get_all_friend_todo_views_by_todo_svc(db: AsyncSession, todo_id: str) -> list[FriendTodoView]:
        friend_todo_views = await FriendTodoViewCrud.get_all_friend_todo_views_by_todo(db, todo_id)
        return friend_todo_views

    # U 수정
    @staticmethod
    async def update_friend_todo_view_svc(db: AsyncSession, friend_todo_view_id: int, data: FriendTodoViewUpdate) -> FriendTodoView:
        friend_todo_view = await FriendTodoViewCrud.get_friend_todo_view(db, friend_todo_view_id)
        if not friend_todo_view:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"friend_todo_view_id '{friend_todo_view_id}'에 해당하는 데이터가 없습니다."
            )

        try:
            updated = await FriendTodoViewCrud.update_friend_todo_view(db, friend_todo_view, data)
            await db.commit()
            await db.refresh(updated)
            return updated

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="friend_todo_view 수정에 실패했습니다."
            )

    # D 삭제
    @staticmethod
    async def delete_friend_todo_view_svc(db: AsyncSession, friend_todo_view_id: int) -> dict:
        friend_todo_view = await FriendTodoViewCrud.get_friend_todo_view(db, friend_todo_view_id)
        if not friend_todo_view:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"friend_todo_view_id '{friend_todo_view_id}'에 해당하는 데이터가 없습니다."
            )

        try:
            await FriendTodoViewCrud.delete_friend_todo_view(db, friend_todo_view)
            await db.commit()
            return {"message": f"friend_todo_view_id '{friend_todo_view_id}' 삭제 완료"}

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="friend_todo_view 삭제에 실패했습니다."
            )