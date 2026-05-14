from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

from ai.core.config import settings
from ai.core.dependencies import get_embedding_model, get_embedding_store, get_openai_client
from ai.interference.feedback import generate_feedback
from ai.interference.retrieval import retrieve_similar
from ai.interference.stats import compute_stats

if TYPE_CHECKING:
    from ai.embeddings.model import EmbeddingModel
    from ai.embeddings.store import EmbeddingStore
    from ai.llm.openai_client import OpenAIClient

logger = logging.getLogger(__name__)
router = APIRouter()


class InterferenceRequest(BaseModel):
    todo_id: str
    todo_text: str
    category: int
    user_id: str

    @field_validator("todo_id", "todo_text", "user_id")
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


def _save_embedding(req: InterferenceRequest, model: "EmbeddingModel", store: "EmbeddingStore") -> None:
    """Save the new todo embedding. Failure should not break the response flow."""
    try:
        vec = model.encode_passage(req.todo_text)
        store.add(
            req.todo_id,
            vec,
            {
                "user_id": req.user_id,
                "category": req.category,
                "text": req.todo_text,
                "completed": False,
            },
        )
        store.save()
    except ValueError as e:
        logger.warning("Embedding save skipped (todo_id=%s): %s", req.todo_id, e)
    except Exception as e:
        logger.error("Embedding save failed (todo_id=%s): %s", req.todo_id, e)


@router.post("/ai/interference", response_model=InterferenceResponse)
async def interference(
    req: InterferenceRequest,
    model: EmbeddingModel = Depends(get_embedding_model),
    store: EmbeddingStore = Depends(get_embedding_store),
    llm_client: OpenAIClient = Depends(get_openai_client),
) -> InterferenceResponse:
    personal_count = store.count_user(req.user_id)

    if personal_count < settings.MIN_PERSONAL_TODOS:
        global_similar = retrieve_similar(req.todo_text, model, store)
        global_stats = compute_stats(global_similar, req.user_id)
        remaining = settings.MIN_PERSONAL_TODOS - personal_count - 1
        global_rate = global_stats["global_rate"]
        rate_str = f"{global_rate:.1f}%" if global_rate is not None else "집계 중"

        _save_embedding(req, model, store)
        return InterferenceResponse(
            global_rate=global_rate,
            personal_rate=None,
            similar_count=global_stats["similar_count"],
            feedback=(
                f"비슷한 todo의 전체 성공률은 {rate_str}입니다. "
                f"개인 패턴 분석까지 {remaining}개가 더 필요해요."
            ),
            similar_failures=[],
        )

    similar = retrieve_similar(req.todo_text, model, store)
    stats = compute_stats(similar, req.user_id)
    feedback = await generate_feedback(req.todo_text, stats, llm_client)
    _save_embedding(req, model, store)

    return InterferenceResponse(
        global_rate=stats["global_rate"],
        personal_rate=stats["personal_rate"],
        similar_count=stats["similar_count"],
        feedback=feedback,
        similar_failures=stats["similar_failures"],
    )
