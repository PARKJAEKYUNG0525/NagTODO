from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.todo import TodoCrud
from app.db.crud.user import UserCrud
from app.db.crud.category import CategoryCrud
from app.db.scheme.todo import TodoCreate, TodoUpdate, TodoCreateResponse, InterferenceResult, MonthlyStatsResponse
from app.db.models.todo import Todo
from app.services.ai_client import get_interference, update_embedding, patch_embedding, delete_embedding


async def _require_user(db: AsyncSession, user_id: int):
    """user_id에 해당하는 User가 없으면 404를 발생시킨다."""
    user = await UserCrud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user_id '{user_id}'에 해당하는 user가 없습니다."
        )
    return user


async def _require_category(db: AsyncSession, category_id: str):
    """category_id에 해당하는 Category가 없으면 404를 발생시킨다."""
    category = await CategoryCrud.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"category_id '{category_id}'에 해당하는 category가 없습니다."
        )
    return category


class TodoService:

    # C 생성
    @staticmethod
    async def create_todo_svc(db: AsyncSession, data: TodoCreate) -> TodoCreateResponse:
        # user 및 category 존재 확인
        await _require_user(db, data.user_id)
        await _require_category(db, data.category_id)

        try:
            todo = await TodoCrud.create_todo(db, data)
            await db.commit()
            await db.refresh(todo)
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="todo 생성에 실패했습니다."
            )

        # AI 간섭 호출 (실패해도 todo 생성 결과는 반환)
        ai_result = await get_interference(
            todo_id=todo.todo_id,
            todo_text=data.title,
            category=data.category_id,
            user_id=str(data.user_id),
        )
        interference = InterferenceResult(**ai_result) if ai_result else None

        return TodoCreateResponse.model_validate({**todo.__dict__, "interference": interference})

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
    async def get_all_todos_svc(db: AsyncSession, user_id: int) -> list[Todo]:
        await _require_user(db, user_id)
        return await TodoCrud.get_todos_by_user(db, user_id)
    

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
            await _require_category(db, data.category_id)

        if data.user_id:
            await _require_user(db, data.user_id)

        old_title = todo.title

        try:
            updated = await TodoCrud.update_todo(db, todo, data)
            await db.commit()
            await db.refresh(updated)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"todo 수정에 실패했습니다: {e}"
            )

        title_changed = data.title is not None and data.title != old_title

        if title_changed:
            # 제목 변경 → soft delete + 재임베딩
            await update_embedding(
                todo_id=todo_id,
                user_id=str(updated.user_id),
                category=updated.category_id,
                text=updated.title,
                completed=(updated.todo_status == "완료"),
            )
        elif data.todo_status is not None or data.category_id is not None:
            # 상태·카테고리만 변경 → 메타데이터만 갱신
            await patch_embedding(
                todo_id=todo_id,
                completed=(updated.todo_status == "완료") if data.todo_status is not None else None,
                category=updated.category_id if data.category_id is not None else None,
            )
        return updated
        
    # R 조회 - 월간 통계
    @staticmethod
    async def get_monthly_stats_svc(
        db: AsyncSession, user_id: int, month_start: str, month_end: str
    ) -> MonthlyStatsResponse:
        await _require_user(db, user_id)

        category_stats = await TodoCrud.get_user_category_stats(db, user_id, month_start, month_end)
        all_users_success_rate = await TodoCrud.get_all_users_success_rate(db, month_start, month_end)

        total = sum(s["total"] for s in category_stats.values())
        completed = sum(s["completed"] for s in category_stats.values())
        user_success_rate = round(completed / total * 100, 1) if total > 0 else 0.0

        return MonthlyStatsResponse(
            user_success_rate=user_success_rate,
            all_users_success_rate=all_users_success_rate,
            category_stats=category_stats,
        )

    # R 조회 - AI 서버 리포트용 월간 로그
    @staticmethod
    async def get_monthly_logs_svc(
        db: AsyncSession, user_id: int, month_start: str, month_end: str
    ) -> list[dict]:
        await _require_user(db, user_id)
        return await TodoCrud.get_monthly_logs(db, user_id, month_start, month_end)

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
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="todo 삭제에 실패했습니다."
            )

        await delete_embedding(todo_id=todo_id)
        return {"message": f"todo_id '{todo_id}' 삭제 완료"}