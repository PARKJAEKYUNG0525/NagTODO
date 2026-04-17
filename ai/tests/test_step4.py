"""Step 4: LangGraph 노드 단위 테스트"""
import json
import pytest
import numpy as np
import networkx as nx
from unittest.mock import AsyncMock, MagicMock, patch


# ── compute_stats ──────────────────────────────────────────────────────────────

from ai.report.nodes.compute_stats import compute_stats

class TestComputeStats:
    def test_basic_aggregation(self):
        logs = [
            {"category": "운동", "completed": True},
            {"category": "운동", "completed": False},
            {"category": "공부", "completed": True},
        ]
        result = compute_stats({"monthly_logs": logs})
        stats = result["category_stats"]
        assert stats["운동"]["total"] == 2
        assert stats["운동"]["completed"] == 1
        assert stats["운동"]["rate"] == 50.0
        assert stats["공부"]["rate"] == 100.0

    def test_no_category_defaults_to_기타(self):
        logs = [{"completed": False}]
        result = compute_stats({"monthly_logs": logs})
        assert "기타" in result["category_stats"]

    def test_empty_logs(self):
        result = compute_stats({"monthly_logs": []})
        assert result["category_stats"] == {}

    def test_rate_precision(self):
        logs = [{"category": "A", "completed": i < 1} for i in range(3)]
        result = compute_stats({"monthly_logs": logs})
        assert result["category_stats"]["A"]["rate"] == round(1 / 3 * 100, 1)


# ── embed_failures ─────────────────────────────────────────────────────────────

from ai.report.nodes.embed_failures import embed_failures

class TestEmbedFailures:
    def test_returns_list_not_ndarray(self):
        mock_model = MagicMock()
        mock_model.encode_passage.return_value = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        with patch("ai.report.nodes.embed_failures.get_embedding_model", return_value=mock_model):
            result = embed_failures({"failed_tasks": [{"text": "운동하기"}]})
        assert isinstance(result["failure_embeddings"], list)
        assert isinstance(result["failure_embeddings"][0], list)

    def test_empty_failed_tasks(self):
        result = embed_failures({"failed_tasks": []})
        assert result == {"failure_embeddings": []}

    def test_embedding_count_matches_tasks(self):
        mock_model = MagicMock()
        mock_model.encode_passage.return_value = np.zeros(384, dtype=np.float32)
        with patch("ai.report.nodes.embed_failures.get_embedding_model", return_value=mock_model):
            result = embed_failures({"failed_tasks": [{"text": f"task{i}"} for i in range(5)]})
        assert len(result["failure_embeddings"]) == 5


# ── build_similarity_graph ─────────────────────────────────────────────────────

from ai.report.nodes.build_similarity_graph import build_similarity_graph

class TestBuildSimilarityGraph:
    def _unit_vec(self, dim=4):
        v = np.ones(dim, dtype=np.float32)
        return (v / np.linalg.norm(v)).tolist()

    def test_identical_embeddings_create_edge(self):
        v = self._unit_vec()
        result = build_similarity_graph({"failure_embeddings": [v, v]})
        g: nx.Graph = result["similarity_graph"]
        assert g.number_of_edges() == 1

    def test_orthogonal_embeddings_no_edge(self):
        v1 = [1.0, 0.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0, 0.0]
        result = build_similarity_graph({"failure_embeddings": [v1, v2]})
        g: nx.Graph = result["similarity_graph"]
        assert g.number_of_edges() == 0

    def test_single_embedding_no_edges(self):
        v = self._unit_vec()
        result = build_similarity_graph({"failure_embeddings": [v]})
        g: nx.Graph = result["similarity_graph"]
        assert g.number_of_nodes() == 1
        assert g.number_of_edges() == 0

    def test_empty_embeddings(self):
        result = build_similarity_graph({"failure_embeddings": []})
        g: nx.Graph = result["similarity_graph"]
        assert g.number_of_nodes() == 0


# ── extract_clusters ───────────────────────────────────────────────────────────

from ai.report.nodes.extract_clusters import extract_clusters

def _make_graph_state(edges: list[tuple], n: int):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    tasks = [{"text": f"task{i}", "category": "A"} for i in range(n)]
    return {"similarity_graph": g, "failed_tasks": tasks}

class TestExtractClusters:
    def test_filters_isolated_nodes(self):
        # 0-1 연결, 2 고립
        state = _make_graph_state([(0, 1)], 3)
        result = extract_clusters(state)
        assert len(result["clusters"]) == 1
        assert len(result["clusters"][0]) == 2

    def test_sorted_by_size_descending(self):
        # 0-1-2 연결, 3-4 연결
        state = _make_graph_state([(0, 1), (1, 2), (3, 4)], 5)
        result = extract_clusters(state)
        sizes = [len(c) for c in result["clusters"]]
        assert sizes == sorted(sizes, reverse=True)

    def test_no_edges_returns_empty_clusters(self):
        state = _make_graph_state([], 3)
        result = extract_clusters(state)
        assert result["clusters"] == []


# ── summarize_clusters ─────────────────────────────────────────────────────────

from ai.report.nodes.summarize_clusters import summarize_clusters

class TestSummarizeClusters:
    def _make_state(self, clusters):
        return {"clusters": clusters}

    def test_basic_summary(self):
        cluster = [
            {"text": "운동1", "category": "운동"},
            {"text": "운동2", "category": "운동"},
            {"text": "공부1", "category": "공부"},
        ]
        result = summarize_clusters(self._make_state([cluster]))
        s = result["cluster_summaries"][0]
        assert s["cluster_id"] == 0
        assert s["size"] == 3
        assert s["dominant_category"] == "운동"
        assert len(s["sample_texts"]) <= 3

    def test_sample_texts_max_3(self):
        cluster = [{"text": f"t{i}", "category": "A"} for i in range(10)]
        result = summarize_clusters(self._make_state([cluster]))
        assert len(result["cluster_summaries"][0]["sample_texts"]) == 3

    def test_empty_clusters(self):
        result = summarize_clusters(self._make_state([]))
        assert result["cluster_summaries"] == []


# ── quality_check ──────────────────────────────────────────────────────────────

from ai.report.nodes.quality_check import quality_check

class TestQualityCheck:
    def _good_report(self):
        return (
            "이번 달 전체 달성률은 75%였습니다.\n"
            "- 운동: 10회 중 8회 완료 (80%)\n"
            "- 공부: 5회 중 3회 완료 (60%)\n"
            "- 독서: 3회 중 2회 완료 (67%)\n"
            "총 18개 task 중 13개를 달성하여 전월 대비 5% 향상되었습니다.\n"
            "실패한 5개 task는 주로 시간 관리 부족으로 분석됩니다."
        )

    def test_passes_all_rules(self):
        result = quality_check({"retrospective_report": self._good_report()})
        assert result["quality_passed"] is True
        assert result["quality_issues"] == []

    def test_fails_min_length(self):
        result = quality_check({"retrospective_report": "짧은 리포트 - 1개"})
        assert not result["quality_passed"]
        assert any("길이" in issue for issue in result["quality_issues"])

    def test_fails_no_bullet(self):
        report = "이번 달 달성률은 75%였습니다. 총 20개 task 중 15개를 완료했습니다. " + "a" * 80
        result = quality_check({"retrospective_report": report})
        assert not result["quality_passed"]
        assert any("bullet" in issue for issue in result["quality_issues"])

    def test_fails_no_number(self):
        report = "이번 달 열심히 했습니다.\n- 운동 완료\n- 공부 완료\n" + "노력했습니다. " * 10
        result = quality_check({"retrospective_report": report})
        assert not result["quality_passed"]
        assert any("숫자" in issue for issue in result["quality_issues"])

    def test_missing_report_field(self):
        result = quality_check({})
        assert not result["quality_passed"]

    def test_bullet_variants(self):
        for bullet in ["- 항목", "• 항목", "* 항목", "1. 항목"]:
            report = f"달성률 75%\n{bullet}\n" + "내용 " * 20
            result = quality_check({"retrospective_report": report})
            bullet_issues = [i for i in result["quality_issues"] if "bullet" in i]
            assert bullet_issues == [], f"{bullet!r} 패턴이 인식되지 않음"


# ── load_logs (async, mock HTTP) ───────────────────────────────────────────────

from ai.report.nodes.load_logs import load_logs

class TestLoadLogs:
    @pytest.mark.asyncio
    async def test_splits_failed_tasks(self):
        todos = [
            {"text": "운동", "completed": True},
            {"text": "공부", "completed": False},
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = todos
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("ai.report.nodes.load_logs.httpx.AsyncClient", return_value=mock_client):
            result = await load_logs({"user_id": "u1", "month_start": "2026-04-01"})

        assert len(result["monthly_logs"]) == 2
        assert len(result["failed_tasks"]) == 1
        assert result["failed_tasks"][0]["text"] == "공부"

    @pytest.mark.asyncio
    async def test_connection_error_raises(self):
        import httpx as httpx_mod
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=httpx_mod.ConnectError("연결 실패"))

        with patch("ai.report.nodes.load_logs.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(ConnectionError):
                await load_logs({"user_id": "u1", "month_start": "2026-04-01"})


# ── llm_analysis (async, mock LLM) ────────────────────────────────────────────

from ai.report.nodes.llm_analysis import llm_analysis

class TestLlmAnalysis:
    @pytest.mark.asyncio
    async def test_returns_pattern_analysis(self):
        mock_client = AsyncMock()
        mock_client.generate = AsyncMock(return_value="클러스터 0: 의지력 부족")
        with patch("ai.report.nodes.llm_analysis.get_ollama_client", return_value=mock_client):
            result = await llm_analysis({"cluster_summaries": [
                {"cluster_id": 0, "size": 2, "dominant_category": "운동", "sample_texts": ["운동1"]}
            ]})
        assert result["pattern_analysis"] == "클러스터 0: 의지력 부족"

    @pytest.mark.asyncio
    async def test_empty_clusters_still_calls_llm(self):
        mock_client = AsyncMock()
        mock_client.generate = AsyncMock(return_value="분석 없음")
        with patch("ai.report.nodes.llm_analysis.get_ollama_client", return_value=mock_client):
            result = await llm_analysis({"cluster_summaries": []})
        assert "pattern_analysis" in result


# ── llm_report (async, mock LLM) ──────────────────────────────────────────────

from ai.report.nodes.llm_report import llm_report

class TestLlmReport:
    def _base_state(self, retry=0, issues=None):
        return {
            "pattern_analysis": "테스트 분석",
            "category_stats": {"운동": {"total": 10, "completed": 7, "rate": 70.0}},
            "retry_count": retry,
            "quality_issues": issues or [],
        }

    @pytest.mark.asyncio
    async def test_increments_retry_count(self):
        mock_client = AsyncMock()
        mock_client.generate = AsyncMock(return_value="리포트 내용")
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            result = await llm_report(self._base_state(retry=2))
        assert result["retry_count"] == 3

    @pytest.mark.asyncio
    async def test_quality_issues_included_in_retry_prompt(self):
        captured_prompts = []
        mock_client = AsyncMock()
        async def capture(prompt):
            captured_prompts.append(prompt)
            return "리포트"
        mock_client.generate = capture
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            await llm_report(self._base_state(retry=1, issues=["숫자 수치 없음"]))
        assert "숫자 수치 없음" in captured_prompts[0]
