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
