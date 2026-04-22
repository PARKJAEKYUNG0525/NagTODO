from langgraph.graph import StateGraph, END

from ai.report.state import ReportState
from ai.report.nodes.load_logs import load_logs
from ai.report.nodes.compute_stats import compute_stats
from ai.report.nodes.embed_failures import embed_failures
from ai.report.nodes.build_similarity_graph import build_similarity_graph
from ai.report.nodes.extract_clusters import extract_clusters
from ai.report.nodes.summarize_clusters import summarize_clusters
from ai.report.nodes.llm_analysis import llm_analysis
from ai.report.nodes.llm_report import llm_report
from ai.report.nodes.quality_check import quality_check

MIN_MONTHLY_TASKS = 30
MIN_FAILURE_TASKS = 5


def _too_few_tasks(state: dict) -> dict:
    count = len(state.get("monthly_logs", []))
    return {
        "retrospective_report": (
            f"최근 30일 등록 task 수: {count} / 최소 필요: {MIN_MONTHLY_TASKS}\n"
            "이 정도로는 분석해달라고 하기 좀 민망하지 않나"
        )
    }


def _minimal_report(state: dict) -> dict:
    count = len(state.get("failed_tasks", []))
    return {
        "retrospective_report": (
            f"실패 데이터 부족. 패턴 분석 실패. "
            "한 달 동안 본인이랑 한 약속을 5번도 안 어겼다고? 제법인데"

        )
    }


def _check_task_count(state: dict) -> str:
    if len(state.get("monthly_logs", [])) < MIN_MONTHLY_TASKS:
        return "too_few_tasks"
    return "compute_category_stats"


def _check_failure_count(state: dict) -> str:
    if len(state.get("failed_tasks", [])) < MIN_FAILURE_TASKS:
        return "minimal_report"
    return "build_similarity_graph"


def _route_after_quality(state: dict) -> str:
    if state.get("quality_passed", False):
        return END
    if state.get("retry_count", 0) < 2:
        return "llm_retrospective_report"
    return END


def build_report_graph():
    graph = StateGraph(ReportState)

    graph.add_node("load_monthly_logs", load_logs)
    graph.add_node("too_few_tasks", _too_few_tasks)
    graph.add_node("compute_category_stats", compute_stats)
    graph.add_node("embed_failures", embed_failures)
    graph.add_node("minimal_report", _minimal_report)
    graph.add_node("build_similarity_graph", build_similarity_graph)
    graph.add_node("extract_clusters", extract_clusters)
    graph.add_node("summarize_clusters", summarize_clusters)
    graph.add_node("llm_pattern_analysis", llm_analysis)
    graph.add_node("llm_retrospective_report", llm_report)
    graph.add_node("quality_check", quality_check)

    graph.set_entry_point("load_monthly_logs")

    graph.add_conditional_edges("load_monthly_logs", _check_task_count)
    graph.add_edge("too_few_tasks", END)

    graph.add_edge("compute_category_stats", "embed_failures")
    graph.add_conditional_edges("embed_failures", _check_failure_count)
    graph.add_edge("minimal_report", END)

    graph.add_edge("build_similarity_graph", "extract_clusters")
    graph.add_edge("extract_clusters", "summarize_clusters")
    graph.add_edge("summarize_clusters", "llm_pattern_analysis")
    graph.add_edge("llm_pattern_analysis", "llm_retrospective_report")
    graph.add_edge("llm_retrospective_report", "quality_check")
    graph.add_conditional_edges("quality_check", _route_after_quality)

    return graph.compile()


report_graph = build_report_graph()
