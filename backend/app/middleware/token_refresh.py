from fastapi import Request
from starlette.responses import Response

from app.core.jwt_handle import verify_token, create_access_token, create_refresh_token
from app.core.auth import set_auth_cookies
from app.db.crud import UserCrud
from app.db.database import get_db
from starlette.middleware.base import BaseHTTPMiddleware
from jwt import ExpiredSignatureError, InvalidTokenError

'''요청 중 토큰 만료 시 재등록하는 middleware'''
# BaseHTTPMiddleware를 상속받아 미들웨어 생성
# 요청(request) -> 처리(handler) -> 응답(response) 사이에 추가 로직 삽입 가능
# call_next(request) : 다음 미들웨어 or 라우터로 요청 전달
class RefreshTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 쿠키에서 토큰 가져옴
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        try:
            # access_token이 존재하면
            if access_token:
                # access_token 유효성 검증
                verify_token(access_token)
                # 검증 통과 시 응답 반환
                return response
        # 만료/잘못된 토큰이면 pass
        except (ExpiredSignatureError, InvalidTokenError):
            pass
        # 만료/잘못된 토큰이라면 refresh_token 확인
        if refresh_token:
            try:
                # refresh_token 유효성 검증하여 사용자id 반환받기
                user_id = verify_token(refresh_token)
            # refresh_token도 만료/잘못된 토큰이라면
            except (ExpiredSignatureError, InvalidTokenError):
                # 갱신 없이 반환
                return response

            new_access_token = create_access_token(user_id)
            new_refresh_token = create_refresh_token(user_id)

            # DB에 새 refresh_token 저장
            try:
                # anext : 비동기 제너레이터에서 값 가져오는 함수, 다음(=세션) 객체 가져옴
                db = await anext(get_db())
                await UserCrud.update_refresh_token_by_id(db, user_id, new_refresh_token)
                await db.commit()
            except Exception:
                await db.rollback()
                raise

            set_auth_cookies(response, new_access_token, new_refresh_token)
        return response