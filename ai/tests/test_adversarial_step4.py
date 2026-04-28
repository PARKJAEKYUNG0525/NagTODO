"""Adversarial tests for Step 4 - edge cases and boundary conditions"""
import pytest
import numpy as np
import networkx as nx
from unittest.mock import AsyncMock, MagicMock, patch


from ai.report.nodes.build_similarity_graph import build_similarity_graph
class TestBuildSimilarityGraphThreshold:
    def test_similarity_exactly_at_threshold_NO_edge(self):
        v1 = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        rest_norm = np.sqrt(1.0 - 0.75**2)
        v2 = np.array([0.75, rest_norm, 0.0, 0.0], dtype=np.float32)
        result = build_similarity_graph({"failure_embeddings": [v1.tolist(), v2.tolist()]})
        assert result["similarity_graph"].number_of_edges() == 0

    def test_similarity_just_above_threshold_creates_edge(self):
        v1 = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        rest_norm = np.sqrt(1.0 - 0.76**2)
        v2 = np.array([0.76, rest_norm, 0.0, 0.0], dtype=np.float32)
        result = build_similarity_graph({"failure_embeddings": [v1.tolist(), v2.tolist()]})
        assert result["similarity_graph"].number_of_edges() == 1


from ai.report.nodes.extract_clusters import extract_clusters
def _make_graph_state(edges, n):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    tasks = [{"text": f"task{i}", "category": "A"} for i in range(n)]
    return {"similarity_graph": g, "failed_tasks": tasks}

class TestExtractClustersSorting:
    def test_clusters_sorted_strictly_descending(self):
        edges = [(0,1),(1,2),(2,3),(3,4), (5,6),(6,7), (8,9),(9,10),(10,11)]
        state = _make_graph_state(edges, 12)
        result = extract_clusters(state)
        sizes = [len(c) for c in result["clusters"]]
        assert sizes == [5, 4, 3]


from ai.report.nodes.quality_check import quality_check
from ai.report.nodes.embed_failures import embed_failures
from ai.report.nodes.summarize_clusters import summarize_clusters

class TestNodeContracts:
    def test_embed_failures_returns_only_failure_embeddings(self):
        mock_model = MagicMock()
        mock_model.encode_passage.return_value = np.array([0.1], dtype=np.float32)
        with patch("ai.report.nodes.embed_failures.get_embedding_model", return_value=mock_model):
            result = embed_failures({"failed_tasks": [{"text": "t"}]})
        assert set(result.keys()) == {"failure_embeddings"}

    def test_quality_check_returns_only_quality_fields(self):
        result = quality_check({"retrospective_report": "a"*100 + " - item"})
        assert set(result.keys()) == {"quality_passed", "quality_issues"}

    def test_summarize_clusters_returns_only_summaries(self):
        result = summarize_clusters({"clusters": []})
        assert set(result.keys()) == {"cluster_summaries"}


class TestQualityCheckBoundaries:
    def test_length_99_fails(self):
        result = quality_check({"retrospective_report": "a" * 99})
        assert result["quality_passed"] is False

    def test_missing_retrospective_report_handled(self):
        result = quality_check({})
        assert result["quality_passed"] is False


from ai.report.nodes.llm_report import llm_report
class TestLlmReportRetryLogic:
    @pytest.mark.asyncio
    async def test_quality_issues_not_included_when_retry_count_zero(self):
        captured_prompts = []
        mock_client = AsyncMock()
        async def capture(prompt):
            captured_prompts.append(prompt)
            return "report"
        mock_client.generate = capture
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            await llm_report({
                "cluster_summaries": [],
                "category_stats": {},
                "retry_count": 0,
                "quality_issues": ["missing numbers"],
            })
        assert "missing numbers" not in captured_prompts[0]

    @pytest.mark.asyncio
    async def test_quality_issues_included_when_retry_count_gt_zero(self):
        captured_prompts = []
        mock_client = AsyncMock()
        async def capture(prompt):
            captured_prompts.append(prompt)
            return "report"
        mock_client.generate = capture
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            await llm_report({
                "cluster_summaries": [],
                "category_stats": {},
                "retry_count": 1,
                "quality_issues": ["missing numbers"],
            })
        assert "missing numbers" in captured_prompts[0]

    @pytest.mark.asyncio
    async def test_llm_report_returns_only_report_and_retry_count(self):
        mock_client = AsyncMock()
        mock_client.generate = AsyncMock(return_value="report")
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            result = await llm_report({
                "cluster_summaries": [],
                "category_stats": {},
                "retry_count": 0,
                "quality_issues": [],
            })
        assert set(result.keys()) == {"retrospective_report", "retry_count"}

    @pytest.mark.asyncio
    async def test_explicit_none_cluster_summaries_not_passed_as_json_null(self):
        """state에 cluster_summaries=None이 명시된 경우 or-fallback으로 []로 처리돼야 함"""
        captured_prompts = []
        mock_client = AsyncMock()
        async def capture(prompt):
            captured_prompts.append(prompt)
            return "report"
        mock_client.generate = capture
        with patch("ai.report.nodes.llm_report.get_ollama_client", return_value=mock_client):
            await llm_report({"cluster_summaries": None, "category_stats": None})
        assert "null" not in captured_prompts[0]
