from contextlib import asynccontextmanager

from fastapi import FastAPI

from ai.core.config import settings
from ai.core.dependencies import get_embedding_model, get_embedding_store
from ai.interference.router import router as interference_router

# generator : 필요할 때마다 하나씩 생성하는 iterator
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 무거운 객체 pre-load (첫 응답 처리 속도 향상)
    get_embedding_model()
    get_embedding_store()
    yield


app = FastAPI(title="NagTODO AI", lifespan=lifespan)
app.include_router(interference_router)

if settings.DEMO_MODE:
    from ai.interference.demo_router import router as interference_demo_router
    from ai.report.demo_router import router as report_demo_router
    app.include_router(interference_demo_router)
    app.include_router(report_demo_router)


# 서버 살아있는지 확인
@app.get("/health")
def health():
    return {"status": "ok"}
