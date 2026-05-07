from typing import Optional

from fastapi import Request, Response, HTTPException, status
from jwt import ExpiredSignatureError, InvalidSignatureError
from app.core.settings import settings
from app.core.jwt_handle import verify_token

# JWT 토큰을 쿠키로 설정
def set_auth_cookies(response: Response, access_token:str, refresh_token:str) -> None:
    response.set_cookie(
        key="access_token",
        value= access_token,
        # 만료 시간(초 단위)
        max_age=int(settings.access_token_expire_seconds),
        secure=True,
        httponly=True,
        samesite="none"
    )
    response.set_cookie(
        key="refresh_token",
        value= refresh_token,
        max_age=int(settings.refresh_token_expire_seconds),
        secure=True,
        httponly=True,
        samesite="none"
    )

# 요청 토큰(사용자)에서 사용자id 가져오기
async def get_user_id(request:Request) -> int:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is missing")
    try:
        user_id = verify_token(access_token)
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No such user")
        return user_id
    # 토큰 인증 만료
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access Token expired")
    # 유효하지 않은 토큰
    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access Token")

# 토큰이 없거나 유효하지 않아도 예외 발생시키지 않고 None 반환
async def get_optional(request:Request) -> Optional[int]:
    access_token = request.cookies.get("access_token")
    if not access_token:
        return None
    try:
        return verify_token(access_token)
    except (ExpiredSignatureError, InvalidSignatureError):
        return None