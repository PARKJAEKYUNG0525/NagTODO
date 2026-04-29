# 앱 모듈 import 전에 환경변수 설정 (pydantic-settings 검증 통과용)
import os
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "3306")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_tests_only")
os.environ.setdefault("AI_SERVER_URL", "http://localhost:8000")

from datetime import date

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.db.seed import seed_categories
from app.routers.todo import router as todo_router

# Base.metadata에 모든 테이블 등록
import app.db.models  # noqa
import app.db.models.notification  # noqa — models/__init__.py에서 누락됨


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """테스트마다 격리된 SQLite in-memory DB를 사용하는 비동기 세션."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        await seed_categories(session)
        await session.commit()
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """테스트용 유저 생성 및 반환."""
    from app.db.models.user import User

    user = User(
        email="test@nagtodo.com",
        pw="hashed_password",
        username="테스트유저",
        birthday=date(1995, 3, 15),
        state=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """todo 라우터만 포함한 테스트 앱 클라이언트."""
    app = FastAPI()
    app.include_router(todo_router)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
