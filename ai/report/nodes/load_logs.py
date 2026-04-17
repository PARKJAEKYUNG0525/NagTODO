import httpx

from ai.core.config import settings


async def load_logs(state: dict) -> dict:
    """백엔드 API에서 월간 로그를 가져와 monthly_logs, failed_tasks를 업데이트."""
    user_id: str = state["user_id"]
    month_start: str = state["month_start"]

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(
                f"{settings.BACKEND_API_URL}/todos",
                params={"user_id": user_id, "month_start": month_start},
            )
            response.raise_for_status()
        except httpx.TimeoutException as e:
            raise TimeoutError("백엔드 API 응답 시간 초과") from e
        except httpx.ConnectError as e:
            raise ConnectionError(f"백엔드 API 연결 실패: {settings.BACKEND_API_URL}") from e

        try:
            monthly_logs: list[dict] = response.json()
        except Exception as e:
            raise ValueError(f"백엔드 API 응답 JSON 파싱 실패: {response.text[:200]}") from e

    failed_tasks = [t for t in monthly_logs if not t.get("completed", False)]

    return {
        "monthly_logs": monthly_logs,
        "failed_tasks": failed_tasks,
    }
