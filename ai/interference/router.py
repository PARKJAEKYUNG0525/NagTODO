from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

from ai.core.dependencies import get_embedding_model, get_embedding_store, get_ollama_client

if TYPE_CHECKING:
    from ai.embeddings.model import EmbeddingModel
    from ai.embeddings.store import EmbeddingStore
    from ai.llm.ollama_client import OllamaClient

from ai.core.config import settings
from ai.interference.retrieval import retrieve_similar
from ai.interference.stats import compute_stats
from ai.interference.feedback import generate_feedback

'''POST /ai/interference : todo 생성 시 유사 task 성공률 계산 및 피드백 반환'''

router = APIRouter()


class InterferenceRequest(BaseModel):
    todo_text: str
    category: str
    user_id: str

    @field_validator("todo_text", "user_id", "category")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("빈 문자열은 허용되지 않습니다")
        return v


class InterferenceResponse(BaseModel):
    global_rate: float | None
    personal_rate: float | None
    similar_count: int
    feedback: str
    similar_failures: list[str]


@router.post("/ai/interference", response_model=InterferenceResponse)
async def interference(
    req: InterferenceRequest,
    model: EmbeddingModel = Depends(get_embedding_model),
    store: EmbeddingStore = Depends(get_embedding_store),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> InterferenceResponse:
    """retrieval → stats → feedback 3단계 파이프라인."""
    personal_count = store.count_user(req.user_id)
    if personal_count < settings.MIN_PERSONAL_TODOS:
        global_similar = retrieve_similar(req.todo_text, model, store)
        global_stats = compute_stats(global_similar, req.user_id)
        remaining = settings.MIN_PERSONAL_TODOS - personal_count
        global_rate = global_stats["global_rate"]
        rate_str = f"{global_rate:.1f}%" if global_rate is not None else "집계 중"
        return InterferenceResponse(
            global_rate=global_rate,
            personal_rate=None,
            similar_count=global_stats["similar_count"],
            feedback=f"비슷한 todo의 전체 성공률은 {rate_str}이에요. 개인 패턴 분석까지 {remaining}개 더 필요해요.",
            similar_failures=[],
        )

    similar = retrieve_similar(req.todo_text, model, store, user_id=req.user_id)
    stats = compute_stats(similar, req.user_id)
    feedback = await generate_feedback(req.todo_text, stats, ollama)

    return InterferenceResponse(
        global_rate=stats["global_rate"],
        personal_rate=stats["personal_rate"],
        similar_count=stats["similar_count"],
        feedback=feedback,
        similar_failures=stats["similar_failures"],
    )
