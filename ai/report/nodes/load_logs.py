import logging

import httpx

from ai.core.config import settings

logger = logging.getLogger(__name__)


async def load_logs(state: dict) -> dict:
    """백엔드 API에서 월간 로그와 카테고리 통계를 가져온다."""
    # monthly_logs가 이미 주입된 경우 HTTP 생략 (데모/테스트용)
    if state.get("monthly_logs") is not None:
        monthly_logs: list[dict] = state["monthly_logs"]
        return {
            "monthly_logs": monthly_logs,
            "failed_tasks": [t for t in monthly_logs if not t.get("completed", False)],
            "category_stats": state.get("category_stats", {}),
        }

    user_id: str = state["user_id"]
    month_start: str = state["month_start"]
    month_end: str = state.get("month_end", "")

    params: dict = {"user_id": user_id, "month_start": month_start}
    if month_end:
        params["month_end"] = month_end

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            todos_resp = await client.get(
                f"{settings.BACKEND_API_URL}/todos/monthly-logs",
                params=params,
            )
            todos_resp.raise_for_status()
        except httpx.TimeoutException as e:
            raise TimeoutError("백엔드 API 응답 시간 초과") from e
        except httpx.ConnectError as e:
            raise ConnectionError(f"백엔드 API 연결 실패: {settings.BACKEND_API_URL}") from e

        try:
            monthly_logs = todos_resp.json()
        except Exception as e:
            raise ValueError(f"백엔드 API 응답 JSON 파싱 실패: {todos_resp.text[:200]}") from e

        # 카테고리 통계는 백엔드에서 계산 (history 기반) — LLM 프롬프트 컨텍스트로 사용
        # monthly_logs 조회에 사용한 params를 그대로 재사용
        category_stats: dict = {}
        try:
            stats_resp = await client.get(
                f"{settings.BACKEND_API_URL}/todos/stats",
                params=params,
            )
            stats_resp.raise_for_status()
            category_stats = stats_resp.json().get("category_stats", {})
        except Exception as e:
            # 통계 조회 실패 시 빈 dict로 진행 — LLM 프롬프트에서 카테고리 섹션이 비게 됨
            logger.warning("카테고리 통계 조회 실패 (user_id=%s): %s", user_id, e)

    failed_tasks = [t for t in monthly_logs if not t.get("completed", False)]

    return {
        "monthly_logs": monthly_logs,
        "failed_tasks": failed_tasks,
        "category_stats": category_stats,
    }
