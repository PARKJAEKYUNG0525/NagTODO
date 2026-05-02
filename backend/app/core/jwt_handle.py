import uuid
from datetime import timedelta, datetime, timezone

import jwt
from passlib.context import CryptContext

from app.core.settings import settings

from fastapi import Depends, HTTPException , Request  
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

security = HTTPBearer()

# 해싱 방식과 정책 관리(bcrypt 알고리즘 사용)
pwd_crypt = CryptContext(schemes=["bcrypt"])

'''비밀번호 암호화'''
def get_password_hash(password:str):
    return pwd_crypt.hash(password)

'''비밀번호 검증'''
# 평문 비번과 해시값 비교해서 같으면 True
def verify_password(plain_pw:str, hashed_pw:str) -> bool:
    return pwd_crypt.verify(plain_pw, hashed_pw)

'''JWT 토큰 생성'''
# jwt 생성 함수(암호화된 jwt문자열 반환)
# uid(userid)
def create_token(uid:int, expires_delta:timedelta, **kwargs) -> str:
    # 추가정보를 페이로드에 넣고 싶을 때
    to_encode = kwargs.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp":expire, "uid":uid})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

# create_token 함수 호출해서 jwt 생성(여기서 준 uid, 알아서 넣는 exp 포함)
# kwargs 없으면 payload는 uid, exp로만 구성
def create_access_token(uid:int) -> str:
    return create_token(uid=uid, expires_delta=settings.access_token_expire_seconds)

# 리프레시 토큰 관리(재발급/ 로그아웃 시 무효화)
def create_refresh_token(uid:int) -> str:
    return create_token(uid=uid, jti=str(uuid.uuid4()), expires_delta=settings.refresh_token_expire_seconds)

'''JWT 토큰 해독'''
# 토큰 해독하여 토큰의 payload 부분을 dict로 반환
# 서명 검증하여 토큰 변조 여부 확인
def decode_token(token:str) -> dict:
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm]
    )

# 토큰을 해독한 후, 받은 payload{} 에서 uid(userid) 꺼내서 반환
def verify_token(token:str) -> int | None:
    payload = decode_token(token)
    return payload.get("uid")


async def get_current_user(
    # credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    token = request.cookies.get("access_token")

    try:
        user_id = verify_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    from app.db.crud.user import UserCrud
    user = await UserCrud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    return user