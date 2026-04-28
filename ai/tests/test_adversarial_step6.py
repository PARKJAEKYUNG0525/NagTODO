"""
Step 6 Adversarial Test Suite
강화 목표: quality_check와 llm_report의 숨겨진 결함 노출
"""
import pytest
from unittest.mock import AsyncMock, patch
from ai.report.nodes.quality_check import quality_check
from ai.report.nodes.llm_report import llm_report


class TestQualityCheckTypeSafety:
    """quality_check이 None, int, dict 등 잘못된 타입을 처리하는지 검증"""

    def test_retrospective_report_none_causes_crash(self):
        """CRITICAL: retrospective_report=None인 경우 len() 호출 시 TypeError"""
        state = {"retrospective_report": None}
        with pytest.raises(TypeError, match="object of type 'NoneType' has no len"):
            quality_check(state)

    def test_retrospective_report_integer_causes_crash(self):
        """CRITICAL: retrospective_report이 정수인 경우 len() 호출 시 TypeError"""
        state = {"retrospective_report": 123}
        with pytest.raises(TypeError, match="object of type 'int' has no len"):
            quality_check(state)

    def test_retrospective_report_dict_causes_crash(self):
        """CRITICAL: retrospective_report이 dict인 경우 TypeError"""
        state = {"retrospective_report": {"text": "리포트"}}
        with pytest.raises(TypeError):
            quality_check(state)



class TestLlmReportNoneReturn:
    """ollama_client.generate()가 None을 반환하는 경우"""

    @pytest.mark.asyncio
    async def test_ollama_returns_none_breaks_quality_check(self):
        """CRITICAL: None 반환 후 quality_check에서 crash"""
        mock_client = AsyncMock()
        mock_client.generate.return_value = None
        
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            result = await llm_report({
                "cluster_summaries": [],
                "category_stats": {"운동": {"total": 10}},
            })
        
        assert result["retrospective_report"] is None
        
        with pytest.raises(TypeError, match="object of type 'NoneType' has no len"):
            quality_check(result)


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

    def test_indented_bullet_fails(self):
        """HIGH: 들여쓰기된 bullet은 매칭 안 됨"""
        report = ("100자 이상입니다. " * 6 + "내용. " * 2 + "\n  - 들여쓰기된 항목")
        
        result = quality_check({"retrospective_report": report})
        assert any("bullet" in i for i in result["quality_issues"])

    def test_numbered_without_space_fails(self):
        """HIGH: "1.항목" (space 없음)은 bullet 인식 못함"""
        report = "분석입니다. " * 8 + "75% 달성.\n1.첫항목\n2.둘째항목"
        
        result = quality_check({"retrospective_report": report})
        assert any("bullet" in i for i in result["quality_issues"])


class TestNumberPatternOvermatch:
    """숫자 패턴의 과도한 매칭"""

    def test_date_triggers_false_positive(self):
        """MEDIUM: 날짜가 통계 숫자로 오인됨"""
        report = "분석입니다 2024-01-15에. " * 5 + "내용. " * 5 + "\n- 항목"
        
        result = quality_check({"retrospective_report": report})
        assert not any("숫자" in i for i in result["quality_issues"])

    def test_year_in_text_false_positive(self):
        """MEDIUM: 연도가 통계로 오인됨"""
        report = "지난 2024년도는 힘들었습니다. " * 5 + "개선이 필요합니다 " * 3 + "\n- 항목"
        
        result = quality_check({"retrospective_report": report})
        assert not any("숫자" in i for i in result["quality_issues"])


