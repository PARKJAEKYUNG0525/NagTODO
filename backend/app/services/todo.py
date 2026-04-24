from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.todo import TodoCrud 
from app.db.scheme.todo import TodoCreate, TodoUpdate
from app.db.models.todo import Todo

class TodoService:

    # C 생성
    @staticmethod
    async def create_todo_svc(db: AsyncSession, data: TodoCreate) -> Todo:
        # user 존재 확인
        user = await TodoCrud.get_user(db, data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{data.user_id}'에 해당하는 user가 없습니다."
            )

        # category 존재 확인
        category = await TodoCrud.get_category(db, data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"category_id '{data.category_id}'에 해당하는 category가 없습니다."
            )

        try:
            todo = await TodoCrud.create_todo(db, data)
            await db.commit()
            await db.refresh(todo)
            return todo

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="todo 생성에 실패했습니다."
            )

    # R 조회 - todo 단일 조회
    @staticmethod
    async def get_todo_svc(db: AsyncSession, todo_id: str) -> Todo:
        todo = await TodoCrud.get_todo(db, todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"todo_id '{todo_id}'에 해당하는 todo가 없습니다."
            )
        return todo

    # R 조회 - todo 목록 조회 (user 기준)
    @staticmethod
    async def get_user_svc(db: AsyncSession, user_id: int) -> list[Todo]:
        user = await TodoCrud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{user_id}'에 해당하는 user가 없습니다."
            )

        todos = await TodoCrud.get_user(db, user_id)
        return todos
    
    # R 조회 - history 전체 조회
    @staticmethod
    async def get_all_todos_svc(db: AsyncSession) -> list[Todo]:
        todo = await TodoCrud.get_all_todos(db)
        return todo

    # U 수정
    @staticmethod
    async def update_todo_svc(db: AsyncSession, todo_id: str, data: TodoUpdate) -> Todo:
        todo = await TodoCrud.get_todo(db, todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"todo_id '{todo_id}'에 해당하는 todo가 없습니다."
            )

        if data.category_id:
            category = await TodoCrud.get_category(db, data.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"category_id '{data.category_id}'에 해당하는 category가 없습니다."
                )
            
        if data.user_id:
            user = await TodoCrud.get_user(db, data.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"user_id '{data.user_id}'에 해당하는 user가 없습니다."
                )

        try:
            updated = await TodoCrud.update_todo(db, todo, data)
            await db.commit()
            await db.refresh(updated)
            return updated

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="todo 수정에 실패했습니다."
            )
        
    # D 삭제
    @staticmethod
    async def delete_todo_svc(db: AsyncSession, todo_id: str) -> dict:
        todo = await TodoCrud.get_todo(db, todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"todo_id '{todo_id}'에 해당하는 todo가 없습니다."
            )

        try:
            await TodoCrud.delete_todo(db, todo)
            await db.commit()
            return {"message": f"todo_id '{todo_id}' 삭제 완료"}

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="todo 삭제에 실패했습니다."
            )