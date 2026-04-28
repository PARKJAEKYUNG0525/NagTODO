import logging

import httpx

from app.core.settings import settings

logger = logging.getLogger(__name__)


async def get_interference(todo_id: str, todo_text: str, category: str, user_id: str) -> dict | None:
    """AI 서버의 간섭 파이프라인 호출. 실패 시 None 반환 (todo 생성은 항상 성공)."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.ai_server_url}/ai/interference",
                json={"todo_id": todo_id, "todo_text": todo_text, "category": category, "user_id": user_id},
                timeout=30.0,
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.warning("AI 간섭 호출 실패: %s", e)
        return None


async def update_embedding(todo_id: str, user_id: str, category: str, text: str, completed: bool) -> None:
    """AI 서버 임베딩 수정 (내부적으로 soft delete + 재임베딩). 실패해도 todo 수정 결과에는 영향 없음."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{settings.ai_server_url}/ai/embeddings/todo/{todo_id}",
                json={"user_id": user_id, "category": category, "text": text, "completed": completed},
                timeout=30.0,
            )
            resp.raise_for_status()
    except Exception as e:
        logger.warning("AI 임베딩 수정 호출 실패 (todo_id=%s): %s", todo_id, e)


async def patch_embedding(todo_id: str, completed: bool | None = None, category: str | None = None) -> None:
    """AI 서버 메타데이터만 수정 (벡터 재계산·soft delete 없음). 실패해도 todo 수정 결과에는 영향 없음."""
    body = {k: v for k, v in {"completed": completed, "category": category}.items() if v is not None}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                f"{settings.ai_server_url}/ai/embeddings/todo/{todo_id}",
                json=body,
                timeout=10.0,
            )
            resp.raise_for_status()
    except Exception as e:
        logger.warning("AI 메타데이터 수정 호출 실패 (todo_id=%s): %s", todo_id, e)


async def delete_embedding(todo_id: str) -> None:
    """AI 서버 임베딩 삭제. 실패해도 todo 삭제 결과에는 영향 없음."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{settings.ai_server_url}/ai/embeddings/todo/{todo_id}",
                timeout=10.0,
            )
            resp.raise_for_status()
    except Exception as e:
        logger.warning("AI 임베딩 삭제 호출 실패 (todo_id=%s): %s", todo_id, e)
