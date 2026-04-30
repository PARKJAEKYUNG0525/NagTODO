from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.user import UserCrud
from app.db.scheme.user import UserCreate, UserUpdate, UserLogin, UserPasswordUpdate
from app.db.models.user import User
from app.core.jwt_handle import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password
)

class UserService:

    # C 생성
    @staticmethod
    async def create_user_svc(db: AsyncSession, data: UserCreate) -> User:
        # 중복 username 확인
        if await UserCrud.get_username(db, data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 동일한 닉네임이 존재합니다."
            )

        # 비밀번호 해시화
        data.pw = get_password_hash(data.pw)

        try:
            user = await UserCrud.create_user(db, data)
            await db.commit()
            await db.refresh(user)
            return user

        # except Exception:
        #     await db.rollback()
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="user 생성에 실패했습니다."
        #     )
        except Exception as e:
            await db.rollback()
            print(f"에러 발생: {e}")  # 추가
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user 생성에 실패했습니다."
            )

    # R 닉네임 중복 확인
    @staticmethod
    async def check_username_svc(db: AsyncSession, username: str, current_user_id: int):
        user = await UserCrud.get_username(db, username)

        if user and user.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 사용 중인 닉네임입니다."
            )

        return {"message": "사용 가능한 닉네임입니다."}

    # R 조회 - user 단일 조회
    @staticmethod
    async def get_user_svc(db: AsyncSession, user_id: int) -> User:
        user = await UserCrud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{user_id}'에 해당하는 user가 없습니다."
            )
        return user

    # R 조회 - user 목록 조회
    @staticmethod
    async def get_all_users_svc(db: AsyncSession) -> list[User]:
        users = await UserCrud.get_all_users(db)
        return users
    
    # R 조회 - 검색
    @staticmethod
    async def search_users_svc(db: AsyncSession, query: str, current_user_id: int):
        users = await UserCrud.search_users(db, query, current_user_id)
        return users

    # U 수정
    @staticmethod
    async def update_user_svc(db: AsyncSession, user_id: int, data: UserUpdate) -> User:
        user = await UserCrud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{user_id}'에 해당하는 user가 없습니다."
            )

        try:
            updated = await UserCrud.update_user(db, user, data)
            await db.commit()
            await db.refresh(updated)
            return updated

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user 수정에 실패했습니다."
            )
        
    # U 수정 - 비밀번호    
    @staticmethod
    async def update_password_svc(
        db: AsyncSession,
        current_user: User,
        data: UserPasswordUpdate
    ) -> dict:

        if not verify_password(data.current_pw, current_user.pw):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="현재 비밀번호가 올바르지 않습니다."
            )

        if data.new_pw != data.confirm_pw:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="새 비밀번호가 일치하지 않습니다."
            )

        if verify_password(data.new_pw, current_user.pw):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="기존 비밀번호와 동일한 비밀번호는 사용할 수 없습니다."
            )

        try:
            current_user.pw = get_password_hash(data.new_pw)

            await db.commit()
            await db.refresh(current_user)

            return {"message": "비밀번호 변경 완료"}

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호 변경에 실패했습니다."
            )

    # U 수정 - state
    # @staticmethod
    # async def update_state_svc(db: AsyncSession, user_id: int):
    #     updated_user = await UserCrud.update_state_by_id(db, user_id, 0)
    #     await db.commit()
    #     await db.refresh(updated_user)
    #     return {"message": "탈퇴가 완료되었습니다"}


    # D 삭제
    @staticmethod
    async def delete_user_svc(db: AsyncSession, user_id: int) -> dict:
        user = await UserCrud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{user_id}'에 해당하는 user가 없습니다."
            )

        try:
            await UserCrud.delete_user(db, user)
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
        
        if str(db_user.state) == 0:
            raise HTTPException(status_code=403, detail="사용할 수 없는 user입니다")

        refresh_token = create_refresh_token(db_user.user_id)
        access_token = create_access_token(db_user.user_id)

        updated_user = await UserCrud.update_refresh_token_by_id(db, db_user.user_id, refresh_token)
        await db.commit()
        await db.refresh(updated_user)
        return updated_user, access_token, refresh_token
    
    # 로그아웃
    @staticmethod
    async def logout_svc(db: AsyncSession, user_id: int):
        updated_user = await UserCrud.update_refresh_token_by_id(db, user_id, None)
        await db.commit()
        await db.refresh(updated_user)
        return updated_user