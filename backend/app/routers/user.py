from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.user import UserCreate, UserUpdate, UserRead, UserLogin, UserPasswordUpdate
from app.db.models.user import User
from app.services.user import UserService as user_svc
from fastapi.responses import JSONResponse, Response

from app.core.jwt_handle import get_current_user

router = APIRouter(prefix="/users", tags=["User"])

# C 생성
@router.post("/", response_model=UserRead, status_code=201)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_svc.create_user_svc(db, data)

# 로그인
@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user, access_token, refresh_token = await user_svc.login(db, data)
    response = JSONResponse(content={
        "user": UserRead.model_validate(user).model_dump(mode="json")
    })
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="none", secure=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="none", secure=True)
    return response

# 로그아웃
@router.post("/logout")
async def logout(response: Response, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await user_svc.logout_svc(db, current_user.user_id)
    response.delete_cookie(key="access_token", httponly=True, samesite="none", secure=True)
    response.delete_cookie(key="refresh_token", httponly=True, samesite="none", secure=True)
    return {"message": "로그아웃 성공"}

# R 조회 - 고정 경로 먼저
@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# R 닉네임 중복 확인
@router.get("/check-username")
async def check_username(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await user_svc.check_username_svc(db, username, current_user.user_id)

# R 닉네임 중복 확인 아래에 추가
@router.get("/search", response_model=list[UserRead])
async def search_users(
    query: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await user_svc.search_users_svc(db, query, current_user.user_id)

# R 전체 조회
@router.get("/user", response_model=list[UserRead])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    return await user_svc.get_all_users_svc(db)

# R 단일 조회 - 변수 경로는 마지막
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await user_svc.get_user_svc(db, user_id)

# U 수정 - 고정 경로 먼저
@router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await user_svc.update_user_svc(db, current_user.user_id, data)

# U 수정 - 비밀번호
@router.patch("/me/password")
async def update_password(
    data: UserPasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await user_svc.update_password_svc(db, current_user, data)

# U 수정 - 변수 경로는 마지막
@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    return await user_svc.update_user_svc(db, user_id, data)

# D 삭제
@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await user_svc.delete_user_svc(db, user_id)