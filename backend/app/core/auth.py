from typing import Optional

from fastapi import Request, Response, HTTPException, status
from jwt import ExpiredSignatureError, InvalidSignatureError
from app.core.settings import settings
from app.core.jwt_handle import verify_token

# JWT 토큰을 쿠키로 설정
def set_auth_cookies(response: Response, access_token:str, refresh_token:str) -> None:
    response.set_cookie(
        # 쿠키{}의 key
        key="access_token",
        # 쿠키{}의 value
        value= access_token,
        # 만료 시간(초 단위)
        max_age=int(settings.access_token_expire_seconds),
        # ngrok 등 cross-origin 환경에서 쿠키 전송을 위해 secure=True, samesite="none" 필요
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
# 쿠키에서 가져온 액세스 토큰 검증
async def get_user_id(request:Request) -> int:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is missing")
    try:
        # 토큰에서 사용자id 추출 시도
        user_id = verify_token(access_token)
        # 사용자id가 없다면 exception
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No such user")
        # 사용자id가 존재한다면 사용자id 반환
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