"""Step 1 완료 조건 검증 테스트."""
import numpy as np
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


# ── 1. EmbeddingModel ────────────────────────────────────────────────────────

def test_embedding_shape():
    from ai.embeddings.model import EmbeddingModel
    vec = EmbeddingModel().encode("테스트")
    assert vec.shape == (384,), f"expected (384,), got {vec.shape}"


def test_embedding_normalized():
    from ai.embeddings.model import EmbeddingModel
    vec = EmbeddingModel().encode("테스트")
    norm = float(np.linalg.norm(vec))
    assert abs(norm - 1.0) < 1e-5, f"벡터가 정규화되지 않음: norm={norm}"


# ── 2. OllamaClient ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ollama_generate():
    from ai.llm.ollama_client import OllamaClient
    result = await OllamaClient().generate("안녕")
    assert isinstance(result, str) and len(result) > 0


# ── 3. FastAPI 서버 기동 ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health():
    from ai.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
