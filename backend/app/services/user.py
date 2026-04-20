from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.user import UserCrud
from app.db.scheme.user import UserCreate, UserUpdate
from app.db.models.user import User

user_crud = UserCrud()

class UserService:

    # C 생성
    @staticmethod
    async def create_user_svc(db: AsyncSession, data: UserCreate) -> User:
        try:
            user = await user_crud.create_user(db, data)
            await db.commit()
            await db.refresh(user)
            return user

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user 생성에 실패했습니다."
            )

    # R 조회 - user 단일 조회
    @staticmethod
    async def get_user_svc(db: AsyncSession, user_id: str) -> User:
        user = await user_crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{user_id}'에 해당하는 유저가 없습니다."
            )
        return user

    # R 조회 - user 목록 조회
    @staticmethod
    async def get_all_users_svc(db: AsyncSession) -> list[User]:
        users = await user_crud.get_all_users(db)
        return users

    # U 수정
    @staticmethod
    async def update_user_svc(db: AsyncSession, user_id: str, data: UserUpdate) -> User:
        user = await user_crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{user_id}'에 해당하는 유저가 없습니다."
            )

        try:
            updated = await user_crud.update_user(db, user, data)
            await db.commit()
            await db.refresh(updated)
            return updated

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user 수정에 실패했습니다."
            )

    # D 삭제
    @staticmethod
    async def delete_user_svc(db: AsyncSession, user_id: str) -> dict:
        user = await user_crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{user_id}'에 해당하는 유저가 없습니다."
            )

        try:
            await user_crud.delete_user(db, user)
            await db.commit()
            return {"message": f"user_id '{user_id}' 삭제 완료"}

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user 삭제에 실패했습니다."
            )