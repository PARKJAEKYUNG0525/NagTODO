"""Step 5: LangGraph 그래프 조립 적대적 검증 테스트"""
import pytest
from langgraph.graph import END

from ai.report.graph import (
    _check_task_count,
    _check_failure_count,
    _route_after_quality,
    _too_few_tasks,
    _minimal_report,
    MIN_MONTHLY_TASKS,
    MIN_FAILURE_TASKS,
)


class TestTypeValidationMissing:
    """입력 타입 검증 누락"""

    def test_check_task_count_state_none_crashes(self):
        with pytest.raises(AttributeError):
            _check_task_count(None)

    def test_check_task_count_monthly_logs_none_crashes(self):
        with pytest.raises(TypeError):
            _check_task_count({"monthly_logs": None})

    def test_check_task_count_monthly_logs_int_crashes(self):
        with pytest.raises(TypeError):
            _check_task_count({"monthly_logs": 123})

    def test_check_failure_count_state_none_crashes(self):
        with pytest.raises(AttributeError):
            _check_failure_count(None)

    def test_check_failure_count_failed_tasks_none_crashes(self):
        with pytest.raises(TypeError):
            _check_failure_count({"failed_tasks": None})

    def test_route_after_quality_retry_count_string_crashes(self):
        with pytest.raises(TypeError, match="'<' not supported"):
            _route_after_quality({"quality_passed": False, "retry_count": "2"})

    def test_too_few_tasks_state_none_crashes(self):
        with pytest.raises(AttributeError):
            _too_few_tasks(None)

    def test_minimal_report_state_none_crashes(self):
        with pytest.raises(AttributeError):
            _minimal_report(None)


class TestBooleanCoercionBug:
    """quality_passed의 boolean 강제 부재"""

    def test_quality_passed_string_false_is_truthy(self):
        result = _route_after_quality({
            "quality_passed": "false",
            "retry_count": 0
        })
        assert result == END  # 버그: 사용자 의도는 False


class TestRetryCountLogic:
    """retry_count < 2 비교 로직"""

    def test_retry_count_boundary_exactly_2(self):
        result = _route_after_quality({"quality_passed": False, "retry_count": 2})
        assert result == END

    def test_retry_count_boundary_exactly_1(self):
        result = _route_after_quality({"quality_passed": False, "retry_count": 1})
        assert result == "llm_retrospective_report"

    def test_retry_count_negative_allows_retry(self):
        result = _route_after_quality({"quality_passed": False, "retry_count": -1})
        assert result == "llm_retrospective_report"


class TestConfigMismatch:
    """graph.py MIN_MONTHLY_TASKS=30 vs config.py MIN_MONTHLY_TASKS=20"""

    def test_min_monthly_tasks_hardcoded_30(self):
        from ai.report.graph import MIN_MONTHLY_TASKS as graph_min
        from ai.core.config import settings

        assert graph_min == 30
        assert settings.MIN_MONTHLY_TASKS == 30

        state_20 = {"monthly_logs": [{}] * 20}
        assert _check_task_count(state_20) == "too_few_tasks"
