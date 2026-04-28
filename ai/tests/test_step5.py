"""Step 5: LangGraph 그래프 조립 테스트"""
import pytest
from unittest.mock import AsyncMock, patch
from langgraph.graph import END

from ai.core.config import settings
from ai.report.graph import (
    build_report_graph,
    _check_task_count,
    _check_failure_count,
    _route_after_quality,
    _too_few_tasks,
    _minimal_report,
)

MIN_MONTHLY_TASKS = settings.MIN_MONTHLY_TASKS
MIN_FAILURE_TASKS = settings.MIN_MONTHLY_FAIL_TASKS


# ── 조건부 엣지 함수 ────────────────────────────────────────────────────────────

class TestCheckTaskCount:
    def _logs(self, n: int) -> list:
        return [{}] * n

    def test_too_few_routes_to_terminal(self):
        state = {"monthly_logs": self._logs(MIN_MONTHLY_TASKS - 1)}
        assert _check_task_count(state) == "too_few_tasks"

    def test_exact_threshold_routes_to_embed(self):
        state = {"monthly_logs": self._logs(MIN_MONTHLY_TASKS)}
        assert _check_task_count(state) == "embed_failures"

    def test_plenty_routes_to_embed(self):
        state = {"monthly_logs": self._logs(100)}
        assert _check_task_count(state) == "embed_failures"

    def test_empty_logs_routes_to_terminal(self):
        assert _check_task_count({}) == "too_few_tasks"


class TestCheckFailureCount:
    def _failures(self, n: int) -> list:
        return [{}] * n

    def test_too_few_routes_to_terminal(self):
        state = {"failed_tasks": self._failures(MIN_FAILURE_TASKS - 1)}
        assert _check_failure_count(state) == "minimal_report"

    def test_exact_threshold_routes_to_graph(self):
        state = {"failed_tasks": self._failures(MIN_FAILURE_TASKS)}
        assert _check_failure_count(state) == "build_similarity_graph"

    def test_plenty_routes_to_graph(self):
        state = {"failed_tasks": self._failures(20)}
        assert _check_failure_count(state) == "build_similarity_graph"

    def test_empty_failures_routes_to_terminal(self):
        assert _check_failure_count({}) == "minimal_report"


class TestRouteAfterQuality:
    def test_quality_passed_returns_end(self):
        state = {"quality_passed": True, "retry_count": 0}
        assert _route_after_quality(state) == END

    def test_quality_failed_retry_allowed(self):
        state = {"quality_passed": False, "retry_count": 1}
        assert _route_after_quality(state) == "llm_retrospective_report"

    def test_quality_failed_retry_exhausted(self):
        state = {"quality_passed": False, "retry_count": 2}
        assert _route_after_quality(state) == END

    def test_quality_failed_retry_count_zero(self):
        state = {"quality_passed": False, "retry_count": 0}
        assert _route_after_quality(state) == "llm_retrospective_report"

    def test_missing_quality_passed_defaults_to_retry(self):
        # quality_passed 미설정 → False로 취급 → 재시도
        state = {"retry_count": 0}
        assert _route_after_quality(state) == "llm_retrospective_report"


# ── 터미널 노드 ─────────────────────────────────────────────────────────────────

class TestTooFewTasks:
    def test_report_stored_in_state(self):
        result = _too_few_tasks({"monthly_logs": [{}] * 5})
        assert "retrospective_report" in result
        assert len(result["retrospective_report"]) > 0

    def test_message_contains_threshold(self):
        result = _too_few_tasks({"monthly_logs": []})
        assert str(MIN_MONTHLY_TASKS) in result["retrospective_report"]


class TestMinimalReport:
    def test_report_stored_in_state(self):
        result = _minimal_report({"failed_tasks": [{}] * 2})
        assert "retrospective_report" in result
        assert len(result["retrospective_report"]) > 0

    def test_message_contains_threshold(self):
        result = _minimal_report({"failed_tasks": []})
        assert str(MIN_FAILURE_TASKS) in result["retrospective_report"]


# ── 그래프 빌드 ─────────────────────────────────────────────────────────────────

class TestBuildReportGraph:
    def test_compile_no_error(self):
        graph = build_report_graph()
        assert graph is not None
