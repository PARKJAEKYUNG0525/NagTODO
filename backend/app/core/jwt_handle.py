import uuid
from datetime import timedelta, datetime, timezone

import jwt
from passlib.context import CryptContext

from app.core.settings import settings

# 해싱 방식과 정책 관리(bcrypt 알고리즘 사용)
pwd_crypt = CryptContext(schemes=["bcrypt"])

'''비밀번호 암호화'''
def get_password_hash(password:str):
    # 입력한 비밀번호를 72바이트까지 잘라서 'utf-8'로 encoding
    trunc_password = password.encode("utf-8")[:72]
    return pwd_crypt.hash(trunc_password)

'''비밀번호 검증'''
# 평문 비번과 해시값 비교해서 같으면 True
def verify_password(plain_pw:str, hashed_pw:str) -> bool:
    trunc_password = plain_pw.encode("utf-8")[:72]
    return pwd_crypt.verify(trunc_password, hashed_pw)

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
def verify_token(token:str) -> int:
    payload = decode_token(token)
    return payload.get("uid")