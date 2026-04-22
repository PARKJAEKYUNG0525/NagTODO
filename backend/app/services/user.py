from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.user import UserCrud
from app.db.scheme.user import UserCreate, UserUpdate, UserLogin
from app.db.models.user import User
from app.core.jwt_handle import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password
)

user_crud = UserCrud()

class UserService:

    # C 생성
    # @staticmethod
    # async def create_user_svc(db: AsyncSession, data: UserCreate) -> User:
    #     try:
    #         user = await user_crud.create_user(db, data)
    #         await db.commit()
    #         await db.refresh(user)
    #         return user

    #     except Exception:
    #         await db.rollback()
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="user 생성에 실패했습니다."
    #         )

    # C 생성 - 회원가입
    @staticmethod
    async def signup_svc(db: AsyncSession, data: UserCreate) -> User:
        # 중복 username 확인
        if await UserCrud.get_username(db, data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 동일한 이름의 사용자가 존재합니다."
            )

        # 비밀번호 해시화
        hash_pw = get_password_hash(data.pw)
        data.pw = hash_pw

        try:
            user = await UserCrud.create_user(db, data)
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
    
    # 로그인
    @staticmethod
    async def login(db:AsyncSession, user:UserLogin):
        db_user = await UserCrud.get_email(db, user.email)

        if not db_user or not verify_password(user.pw, db_user.pw):
            raise HTTPException(status_code=401, detail="잘못된 이메일 혹은 비밀번호입니다")

        refresh_token = create_refresh_token(db_user.user_id)
        access_token = create_access_token(db_user.user_id)

        updated_user = await UserCrud.update_refresh_token_by_id(db, db_user.user_id, refresh_token)
        await db.commit()
        await db.refresh(updated_user)
        return updated_user, access_token, refresh_token