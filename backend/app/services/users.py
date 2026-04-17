from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.db.scheme.users import UserCreate, UserUpdate, UserLogin
from sqlalchemy.future import select
from app.db.crud import UserCrud
from fastapi import HTTPException
from app.core.jwt_handle import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password
)

# CRUD는 UserCrud에서 처리하고, 비즈니스 규칙(유효성 검사, 비밀번호 해시, 예외처리 등)을 추가
class UserService:

    @staticmethod
    async def get_user(db:AsyncSession, user_id: int) -> User:
        db_user = await UserCrud.get_by_id(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        return db_user

    @staticmethod
    async def signup(db:AsyncSession, user:UserCreate):
        # 중복 username 확인
        if await UserCrud.get_by_username(db, user.username):
            raise HTTPException(status_code=400, detail="이미 동일한 이름의 사용자가 존재합니다")

        # username없으면 -> 새 사용자 저장
        # password는 미리 암호화
        hash_pw = get_password_hash(user.password)
        # username, password, email을 DB에 저장
        user_create=UserCreate(username=user.username, password=hash_pw, email=user.email)

        try:
            db_user = await UserCrud.create(db,user_create)
            await db.commit()
            await db.refresh(db_user)
            return db_user

        except Exception:
            await db.rollback()
            raise HTTPException(status_code=401, detail="잘못된 이메일 혹은 비밀번호입니다")

    @staticmethod
    async def login(db:AsyncSession, user:UserLogin):
        # email로 사용자 찾아서 가져오기
        db_user = await UserCrud.get_by_email(db, user.email)

        # DB에 들어잇는 암호화된 비번(db_user.password)과 내가 입력한 비번(user.password) 확인
        if not db_user or not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="잘못된 이메일 혹은 비밀번호입니다")

        # 사용자id로 토큰 발급
        refresh_token = create_refresh_token(db_user.user_id)
        access_token = create_access_token(db_user.user_id)

        # db에 refresh_token 저장
        updated_user = await UserCrud.update_refresh_token_by_id(db, db_user.user_id, refresh_token)
        await db.commit()
        # 토큰 저장된 사용자로 갱신
        await db.refresh(updated_user)
        # 사용자 정보 + jwt 액세스/리프레시 토큰 반환받기
        return updated_user, access_token, refresh_token