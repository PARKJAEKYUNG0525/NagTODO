from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from app.core.settings import settings
from sqlalchemy.orm import sessionmaker

# 비동기 db연결 생성하는 함수 (mysql+asyncmy url사용하여 비동기적으로 db와 연결한다)
async_engine=create_async_engine(settings.db_url, echo=False)

# 비동기 엔진과 연결된 세션사용하려고
# sessionmaker는 옛 방식이라 경고 줄, async_sessionmaker가 최신 버전
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

# 동기 db연결 생성하는 함수 (동기적으로 db와 연결한다))
sync_engine=create_engine(settings.sync_db_url, pool_pre_ping=True)

# 기본 클래스 설정(Base)
Base=declarative_base()

# 비동기 세션 생성
# async def get_db():
#     session=None
#     try:
#         session=AsyncSessionLocal()
#         yield session
#     except:
#         pass
#     finally:
#         if session:
#             await session.close()
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session

# app/db/database.py

async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception:
        try:
            await session.rollback()
        except Exception:
            pass   # rollback 자체가 실패해도 무시 (cancellation race)
        raise
    finally:
        try:
            await session.close()
        except Exception:
            pass   # close 실패도 조용히