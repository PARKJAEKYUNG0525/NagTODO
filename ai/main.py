from contextlib import asynccontextmanager

from fastapi import FastAPI

from ai.core.dependencies import get_embedding_model

# generater : 필요할 때마다 하나씩 생성하는 iterator
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 임베딩 모델 pre-load (첫 응답 처리 속도 빠름)
    get_embedding_model()
    # Step 2 완료 후: get_embedding_store() 추가
    yield


app = FastAPI(title="NagTODO AI", lifespan=lifespan)

# 서버 살아있는지 확인
@app.get("/health")
def health():
    return {"status": "ok"}
