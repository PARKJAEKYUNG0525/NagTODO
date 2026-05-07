from fastapi import Request
from starlette.responses import Response

from app.core.jwt_handle import verify_token, create_access_token, create_refresh_token
from app.core.auth import set_auth_cookies
from app.db.crud import UserCrud
from app.db.database import get_db
from starlette.middleware.base import BaseHTTPMiddleware
from jwt import ExpiredSignatureError, InvalidTokenError

'''요청 중 토큰 만료 시 재등록하는 middleware'''
class RefreshTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        try:
            if access_token:
                verify_token(access_token)
                return response
        except (ExpiredSignatureError, InvalidTokenError):
            pass
        if refresh_token:
            try:
                user_id = verify_token(refresh_token)
            except (ExpiredSignatureError, InvalidTokenError):
                return response

            new_access_token = create_access_token(user_id)
            new_refresh_token = create_refresh_token(user_id)

            try:
                db = await anext(get_db())
                await UserCrud.update_refresh_token_by_id(db, user_id, new_refresh_token)
                await db.commit()
            except Exception:
                await db.rollback()
                return response

            set_auth_cookies(response, new_access_token, new_refresh_token)
        return response