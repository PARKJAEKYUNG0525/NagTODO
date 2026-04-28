"""
Step 6 Adversarial Test Suite
강화 목표: quality_check와 llm_report의 숨겨진 결함 노출
"""
import pytest
from unittest.mock import AsyncMock, patch
from ai.report.nodes.quality_check import quality_check
from ai.report.nodes.llm_report import llm_report


class TestQualityCheckTypeSafety:
    """quality_check이 None, int, dict 등 잘못된 타입을 방어적으로 처리하는지 검증"""

    def test_retrospective_report_none_treated_as_empty(self):
        """None은 빈 문자열로 처리돼 crash 없이 질 검증 실패"""
        result = quality_check({"retrospective_report": None})
        assert result["quality_passed"] is False
        assert any("짧습니다" in i for i in result["quality_issues"])

    def test_retrospective_report_integer_causes_crash(self):
        """int는 or-fallback으로 걸러지지 않아 len()에서 TypeError"""
        state = {"retrospective_report": 123}
        with pytest.raises(TypeError):
            quality_check(state)

    def test_retrospective_report_dict_causes_crash(self):
        """dict는 or-fallback으로 걸러지지 않아 regex.search()에서 TypeError"""
        with pytest.raises(TypeError):
            quality_check({"retrospective_report": {"text": "리포트"}})


class TestLlmReportNoneReturn:
    """ollama_client.generate()가 None을 반환하는 경우"""

    @pytest.mark.asyncio
    async def test_ollama_returns_none_falls_back_to_empty_string(self):
        """None 반환 시 or-fallback으로 빈 문자열이 저장돼 quality_check가 정상 실행됨"""
        mock_client = AsyncMock()
        mock_client.generate.return_value = None

        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            result = await llm_report({
                "cluster_summaries": [],
                "category_stats": {"운동": {"total": 10}},
            })

        assert result["retrospective_report"] == ""
        # quality_check도 crash 없이 실행 가능
        qc = quality_check(result)
        assert qc["quality_passed"] is False


class TestLlmReportStateLoss:
    """llm_report가 state의 다른 필드를 버림"""

    @pytest.mark.asyncio
    async def test_state_fields_not_preserved(self):
        """HIGH: state 필드들이 손실됨"""
        mock_client = AsyncMock()
        mock_client.generate.return_value = "리포트"
        
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            state = {
                "cluster_summaries": [],
                "category_stats": {"운동": {"total": 10, "completed": 7}},
                "failed_tasks": [{"id": "task1"}],
                "retry_count": 1,
            }
            
            result = await llm_report(state)
        
        assert set(result.keys()) == {"retrospective_report", "retry_count"}
        assert "pattern_analysis" not in result
        assert "category_stats" not in result


class TestQualityCheckBulletRegex:
    """bullet pattern의 경계 케이스"""

    def test_indented_bullet_passes(self):
        """앞 공백 허용 패턴으로 들여쓰기된 bullet도 매칭됨"""
        report = "100자 이상입니다. " * 6 + "내용. " * 2 + "\n  - 들여쓰기된 항목"

        result = quality_check({"retrospective_report": report})
        assert all("bullet" not in i for i in result["quality_issues"])

    def test_numbered_without_space_passes(self):
        r"""\s*\S 패턴으로 "1.항목" (space 없음)도 bullet 인식됨"""
        report = "분석입니다. " * 8 + "75% 달성.\n1.첫항목\n2.둘째항목"

        result = quality_check({"retrospective_report": report})
        assert all("bullet" not in i for i in result["quality_issues"])


class TestNumberPatternOvermatch:
    """숫자 패턴이 날짜/연도를 올바르게 제외하는지 검증"""

    def test_date_excluded_from_stat_pattern(self):
        """날짜(YYYY-MM-DD) 숫자는 stat 패턴에서 제외 → 실제 수치가 없으면 숫자 이슈 발생"""
        report = "분석입니다 2024-01-15에. " * 5 + "내용. " * 5 + "\n- 항목"

        result = quality_check({"retrospective_report": report})
        # 날짜만 있고 실제 달성률 수치가 없으므로 숫자 이슈가 발생해야 함
        assert any("숫자" in i for i in result["quality_issues"])

    def test_year_excluded_from_stat_pattern(self):
        """연도(2024년)는 stat 패턴에서 제외 → 실제 수치가 없으면 숫자 이슈 발생"""
        report = "지난 2024년도는 힘들었습니다. " * 5 + "개선이 필요합니다 " * 3 + "\n- 항목"

        result = quality_check({"retrospective_report": report})
        # 연도만 있고 실제 달성률 수치가 없으므로 숫자 이슈가 발생해야 함
        assert any("숫자" in i for i in result["quality_issues"])


