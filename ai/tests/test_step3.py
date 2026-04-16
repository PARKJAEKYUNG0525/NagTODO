"""Step 3 완료 조건 검증 테스트.

완료 조건:
1. POST /ai/interference 200 응답, 명세 형식 일치
2. 빈 벡터 스토어에서도 에러 없이 동작
3. personal_rate < 30% 일 때만 LLM 호출됨을 확인
4. similar_failures 개인 실패 우선 정렬 확인
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from ai.interference.stats import compute_stats


# ── stats 단위 테스트 ─────────────────────────────────────────────────────────────

def _make_task(user_id: str, completed: bool, text: str = "task") -> dict:
    return {"user_id": user_id, "completed": completed, "text": text}


def test_compute_stats_empty():
    """유사 데이터 없으면 similar_count=0, 성공률은 None."""
    result = compute_stats([], "u1")
    assert result["similar_count"] == 0
    assert result["global_rate"] is None
    assert result["personal_rate"] is None
    assert result["similar_failures"] == []


def test_compute_stats_global_rate():
    """global_rate = 전체 완료 / 전체 * 100."""
    tasks = [
        _make_task("u2", True),
        _make_task("u2", False),
        _make_task("u2", False),
        _make_task("u2", True),
    ]
    result = compute_stats(tasks, "u1")
    assert result["global_rate"] == pytest.approx(50.0)
    assert result["personal_rate"] is None  # u1 데이터 없음
    assert result["similar_count"] == 4
    assert result["personal_count"] == 0


def test_compute_stats_personal_rate():
    """personal_rate = user_id 매칭 항목만 계산."""
    tasks = [
        _make_task("u1", True),   # personal 완료
        _make_task("u1", False),  # personal 실패
        _make_task("u2", False),  # 타 사용자
    ]
    result = compute_stats(tasks, "u1")
    assert result["personal_rate"] == pytest.approx(50.0)
    assert result["personal_count"] == 2
    assert result["global_rate"] == pytest.approx(100 / 3)


def test_compute_stats_personal_all_completed():
    """개인 성공률 100% 케이스."""
    tasks = [_make_task("u1", True), _make_task("u1", True)]
    result = compute_stats(tasks, "u1")
    assert result["personal_rate"] == pytest.approx(100.0)


def test_similar_failures_personal_first():
    """similar_failures는 개인 실패가 먼저, 최대 5개."""
    tasks = [
        _make_task("u1", False, "개인실패1"),
        _make_task("u1", False, "개인실패2"),
        _make_task("u2", False, "타인실패1"),
        _make_task("u2", False, "타인실패2"),
        _make_task("u2", False, "타인실패3"),
        _make_task("u2", False, "타인실패4"),
    ]
    result = compute_stats(tasks, "u1")
    failures = result["similar_failures"]
    assert len(failures) == 6
    # 개인 실패가 앞에 와야 함
    assert failures[0] == "개인실패1"
    assert failures[1] == "개인실패2"


def test_similar_failures_max_ten():
    """similar_failures는 최대 10개를 초과하지 않는다."""
    tasks = [_make_task("u1", False, f"실패{i}") for i in range(15)]
    result = compute_stats(tasks, "u1")
    assert len(result["similar_failures"]) == 10


# ── feedback 단위 테스트 ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_feedback_no_data():
    """유사 데이터 없으면 LLM 미호출, 고정 문자열 반환."""
    from ai.interference.feedback import generate_feedback

    ollama = AsyncMock()
    stats = {"similar_count": 0, "personal_rate": None, "global_rate": None, "similar_failures": []}
    result = await generate_feedback("운동하기", stats, ollama)
    ollama.generate.assert_not_called()
    assert isinstance(result, str) and len(result) > 0


@pytest.mark.asyncio
async def test_feedback_personal_rate_high_no_llm():
    """personal_rate >= 30%이면 LLM 미호출."""
    from ai.interference.feedback import generate_feedback

    ollama = AsyncMock()
    stats = {"similar_count": 5, "personal_rate": 50.0, "global_rate": 40.0, "similar_failures": []}
    result = await generate_feedback("운동하기", stats, ollama)
    ollama.generate.assert_not_called()
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_feedback_no_personal_low_global_no_llm():
    """personal_rate 없음 + global_rate < 30%이면 LLM 미호출."""
    from ai.interference.feedback import generate_feedback

    ollama = AsyncMock()
    stats = {"similar_count": 5, "personal_rate": None, "global_rate": 20.0, "similar_failures": []}
    result = await generate_feedback("운동하기", stats, ollama)
    ollama.generate.assert_not_called()
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_feedback_personal_rate_low_calls_llm():
    """personal_rate < 30%이면 LLM 호출."""
    from ai.interference.feedback import generate_feedback

    ollama = AsyncMock()
    ollama.generate.return_value = "이번엔 꼭 해내야 해요!"
    stats = {"similar_count": 10, "personal_rate": 20.0, "global_rate": 40.0, "similar_failures": ["운동 포기"]}
    result = await generate_feedback("운동하기", stats, ollama)
    ollama.generate.assert_called_once()
    assert result == "이번엔 꼭 해내야 해요!"


# ── 라우터 통합 테스트 ────────────────────────────────────────────────────────────

def _make_app():
    """테스트용 FastAPI 앱 생성 (의존성 오버라이드 적용)."""
    from fastapi import FastAPI
    from ai.interference.router import router
    from ai.core.dependencies import get_embedding_model, get_embedding_store
    from ai.core.dependencies import get_ollama_client

    app = FastAPI()
    app.include_router(router)

    mock_model = MagicMock()
    mock_model.encode.return_value = __import__("numpy").zeros(384, dtype="float32")

    mock_store = MagicMock()
    mock_store.search.return_value = []

    mock_ollama = MagicMock()

    app.dependency_overrides[get_embedding_model] = lambda: mock_model
    app.dependency_overrides[get_embedding_store] = lambda: mock_store
    app.dependency_overrides[get_ollama_client] = lambda: mock_ollama
    return app


def test_router_empty_store_200():
    """빈 벡터 스토어에서도 200 응답, 명세 형식 일치."""
    client = TestClient(_make_app())
    resp = client.post(
        "/ai/interference",
        json={"todo_text": "운동하기", "category": "health", "user_id": "u1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "global_rate" in body
    assert "personal_rate" in body
    assert "similar_count" in body
    assert "feedback" in body
    assert "similar_failures" in body
    assert body["similar_count"] == 0


def test_router_response_schema():
    """응답 필드 타입 검증."""
    client = TestClient(_make_app())
    resp = client.post(
        "/ai/interference",
        json={"todo_text": "독서하기", "category": "learning", "user_id": "u2"},
    )
    body = resp.json()
    assert isinstance(body["similar_failures"], list)
    assert isinstance(body["feedback"], str)
    assert body["global_rate"] is None
    assert body["personal_rate"] is None
