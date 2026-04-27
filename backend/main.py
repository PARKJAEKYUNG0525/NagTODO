import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, async_engine
from fastapi.concurrency import asynccontextmanager

from app.middleware.token_refresh import RefreshTokenMiddleware

from app.routers.user import router as user_router
from app.routers.category import router as category_router
from app.routers.cloth import router as cloth_router
from app.routers.friend_todo_view import router as friend_todo_view_router
# from app.routers.friend import router as friend_router
from app.routers.history import router as history_router
from app.routers.homepage import router as homepage_router
from app.routers.img import router as img_router
from app.routers.music import router as music_router
from app.routers.pw_history import router as pw_history_router
# from app.routers.recommend import router as recommend_router
from app.routers.report import router as report_router
from app.routers.todo import router as todo_router
load_dotenv(dotenv_path=".env")

# DB연결 후 모든 테이블 생성(metadata.create_all)
# 종료 시에 DB 연결 해제
@asynccontextmanager
async def lifespan(app:FastAPI):
    async with async_engine.begin() as conn:
        # conn.run_sync : db 연결 후
        # Base.metadata.create_all : 테이블을 생성하라
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

app=FastAPI(lifespan=lifespan)

app.add_middleware(RefreshTokenMiddleware)

# 요청 허용 관련 설정
app.add_middleware(
    # CORSMiddleware,
    # # 요청을 허용할 출처 리스트
    # allow_origins=["http://localhost:3000"],
    # # 로그인/jwt 기반 인증 필요한 경우(쿠키, 세션정보 등 요청 허용)
    # allow_credentials=True,
    # # HTTP 모든 메소드 다 허용(보통은...)
    # # allow_methods=["get", "post"] 이런 식으로 사용할 수도 있음 
    # allow_methods=["*"],
    # allow_headers=["*"],


    CORSMiddleware,
    # allow_origins=["*"],  # 개발 중에는 일단 전체 허용
    allow_origins=["http://192.168.0.42:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(category_router)
app.include_router(cloth_router)
app.include_router(friend_todo_view_router)
# app.include_router(friend_router)
app.include_router(history_router)
app.include_router(homepage_router)
app.include_router(img_router)

app.include_router(music_router)
app.include_router(pw_history_router)
# app.include_router(recommend_router)
app.include_router(report_router)
app.include_router(todo_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)