from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ai.core.dependencies import get_embedding_model, get_embedding_store, get_ollama_client

if TYPE_CHECKING:
    from ai.embeddings.model import EmbeddingModel
    from ai.embeddings.store import EmbeddingStore
    from ai.llm.ollama_client import OllamaClient

from ai.interference.retrieval import retrieve_similar
from ai.interference.stats import compute_stats
from ai.interference.feedback import generate_feedback

'''POST /ai/interference : todo 생성 시 유사 task 성공률 계산 및 피드백 반환'''

router = APIRouter()


class InterferenceRequest(BaseModel):
    todo_text: str
    category: str
    user_id: str


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
    similar = retrieve_similar(req.todo_text, model, store)
    stats = compute_stats(similar, req.user_id)
    feedback = await generate_feedback(req.todo_text, stats, ollama)

    return InterferenceResponse(
        global_rate=stats["global_rate"],
        personal_rate=stats["personal_rate"],
        similar_count=stats["similar_count"],
        feedback=feedback,
        similar_failures=stats["similar_failures"],
    )
