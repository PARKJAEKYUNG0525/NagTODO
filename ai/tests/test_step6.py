"""Step 6: quality_check 강화 및 llm_report 재시도 프롬프트 테스트"""
import pytest
from unittest.mock import AsyncMock, patch

from ai.report.nodes.quality_check import quality_check


# ── quality_check ──────────────────────────────────────────────────────────────

class TestQualityCheck:
    def _make_state(self, report: str) -> dict:
        return {"retrospective_report": report}

    def test_passes_with_valid_report(self):
        report = (
            "이번 달 운동 카테고리 달성률은 75%였습니다.\n"
            "- 꾸준한 아침 루틴 덕분에 성과가 향상되었습니다.\n"
            "- 공부 카테고리는 50% 달성으로 개선이 필요합니다.\n"
            "총 30개 중 22개를 완료하였으며 다음 달에는 80%를 목표로 합니다."
        )
        result = quality_check(self._make_state(report))
        assert result["quality_passed"] is True
        assert result["quality_issues"] == []

    def test_empty_string_fails_all_three_rules(self):
        result = quality_check(self._make_state(""))
        assert result["quality_passed"] is False
        assert len(result["quality_issues"]) == 3
        assert any("짧습니다" in i for i in result["quality_issues"])
        assert any("bullet" in i for i in result["quality_issues"])
        assert any("숫자" in i for i in result["quality_issues"])

    def test_short_report_message_includes_length(self):
        short = "- 개선 필요 항목 있음. 50% 달성."
        result = quality_check(self._make_state(short))
        length_issues = [i for i in result["quality_issues"] if "짧습니다" in i]
        assert len(length_issues) == 1
        assert str(len(short)) in length_issues[0]

    def test_exact_100_chars_passes_length(self):
        # bullet과 숫자를 포함하면서 정확히 100자
        base = "- 달성률 50%입니다. "  # 14자
        report = (base * 8)[:100]  # 112자 생성 후 100자로 자름
        assert len(report) == 100
        result = quality_check(self._make_state(report))
        assert all("짧습니다" not in i for i in result["quality_issues"])

    def test_99_chars_fails_length(self):
        report = "a" * 99
        result = quality_check(self._make_state(report))
        assert any("짧습니다" in i for i in result["quality_issues"])

    def test_bullet_dash_passes(self):
        report = "달성률은 75%입니다. " + "x" * 80 + "\n- 개선 항목"
        result = quality_check(self._make_state(report))
        assert all("bullet" not in i for i in result["quality_issues"])

    def test_bullet_dot_passes(self):
        report = "달성률은 75%입니다. " + "x" * 80 + "\n• 개선 항목"
        result = quality_check(self._make_state(report))
        assert all("bullet" not in i for i in result["quality_issues"])

    def test_bullet_asterisk_passes(self):
        report = "달성률은 75%입니다. " + "x" * 80 + "\n* 개선 항목"
        result = quality_check(self._make_state(report))
        assert all("bullet" not in i for i in result["quality_issues"])

    def test_bullet_numbered_list_passes(self):
        report = "달성률은 75%입니다. " + "x" * 80 + "\n1. 개선 항목"
        result = quality_check(self._make_state(report))
        assert all("bullet" not in i for i in result["quality_issues"])

    def test_no_bullet_fails(self):
        # 100자 이상, 숫자 포함, bullet 없음
        report = "이번 달 달성률은 75퍼센트였습니다. " + "개선이 필요합니다. " * 8 + "총 30개 완료."
        result = quality_check(self._make_state(report))
        assert any("bullet" in i for i in result["quality_issues"])

    def test_no_number_fails(self):
        # 100자 이상, bullet 포함, 숫자 없음
        report = "- 개선 방향\n" + "이번 달 달성률이 좋았습니다. 꾸준히 노력했습니다. " * 5
        result = quality_check(self._make_state(report))
        assert any("숫자" in i for i in result["quality_issues"])

    def test_missing_report_key_treated_as_empty(self):
        result = quality_check({})
        assert result["quality_passed"] is False
        assert len(result["quality_issues"]) == 3


# ── llm_report 재시도 프롬프트 ──────────────────────────────────────────────────

from ai.report.nodes.llm_report import llm_report


class TestLlmReportRetryPrompt:
    _BASE_STATE = {
        "cluster_summaries": [{"cluster_id": 0, "size": 2, "dominant_category": "운동", "sample_texts": ["운동1"]}],
        "category_stats": {"운동": {"total": 10, "completed": 7, "rate": 70.0}},
    }

    @pytest.mark.asyncio
    async def test_first_attempt_no_retry_section(self):
        mock_client = AsyncMock()
        mock_client.generate.return_value = "리포트 내용"
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            await llm_report({**self._BASE_STATE, "retry_count": 0, "quality_issues": []})
        prompt = mock_client.generate.call_args[0][0]
        assert "이전 시도에서" not in prompt

    @pytest.mark.asyncio
    async def test_retry_prompt_includes_issues(self):
        issues = ["리포트가 너무 짧습니다 (40자)", "통계 숫자가 인용되지 않았습니다"]
        mock_client = AsyncMock()
        mock_client.generate.return_value = "개선된 리포트"
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            await llm_report({
                **self._BASE_STATE,
                "retry_count": 1,
                "quality_issues": issues,
            })
        prompt = mock_client.generate.call_args[0][0]
        assert "이전 시도에서 다음 문제가 있었습니다:" in prompt
        assert "- 리포트가 너무 짧습니다 (40자)" in prompt
        assert "- 통계 숫자가 인용되지 않았습니다" in prompt
        assert "위 문제를 반드시 수정하여 다시 작성하세요." in prompt

    @pytest.mark.asyncio
    async def test_retry_increments_count(self):
        mock_client = AsyncMock()
        mock_client.generate.return_value = "리포트"
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            result = await llm_report({**self._BASE_STATE, "retry_count": 1, "quality_issues": []})
        assert result["retry_count"] == 2

    @pytest.mark.asyncio
    async def test_retry_positive_but_no_issues_skips_section(self):
        # retry_count > 0이지만 quality_issues가 비어있으면 재시도 섹션 미포함
        mock_client = AsyncMock()
        mock_client.generate.return_value = "리포트"
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            await llm_report({**self._BASE_STATE, "retry_count": 1, "quality_issues": []})
        prompt = mock_client.generate.call_args[0][0]
        assert "이전 시도에서" not in prompt
