from langgraph.graph import StateGraph, END

from ai.core.config import settings
from ai.report.state import ReportState
from ai.report.nodes.load_logs import load_logs
from ai.report.nodes.embed_failures import embed_failures
from ai.report.nodes.build_similarity_graph import build_similarity_graph
from ai.report.nodes.extract_clusters import extract_clusters
from ai.report.nodes.summarize_clusters import summarize_clusters
from ai.report.nodes.llm_report import llm_report
from ai.report.nodes.quality_check import quality_check

MIN_MONTHLY_TASKS = settings.MIN_MONTHLY_TASKS
MIN_FAILURE_TASKS = settings.MIN_MONTHLY_FAIL_TASKS


def _too_few_tasks(state: dict) -> dict:
    monthly_logs = state.get("monthly_logs") or []
    count = len(monthly_logs)
    return {
        "retrospective_report": (
            f"최근 30일 등록 task 수: {count} / 최소 필요: {settings.MIN_MONTHLY_TASKS}\n"
            "이 정도로는 분석해달라고 하기 좀 민망하지 않나"
        )
    }


def _minimal_report(state: dict) -> dict:
    failed_count = len(state.get("failed_tasks") or [])
    return {
        "retrospective_report": (
            f"실패 task 수 {failed_count}개로 최소 기준({MIN_FAILURE_TASKS}개) 미달 — "
            "패턴 분석 불가. 한 달 동안 본인이랑 한 약속을 5번도 안 어겼다고? 제법인데"
        )
    }


def _check_task_count(state: dict) -> str:
    if not isinstance(state, dict):
        raise TypeError(f"state must be dict, got {type(state).__name__}")
    monthly_logs = state.get("monthly_logs") or []
    if len(monthly_logs) < settings.MIN_MONTHLY_TASKS:
        return "too_few_tasks"
    return "embed_failures"


def _check_failure_count(state: dict) -> str:
    if not isinstance(state, dict):
        raise TypeError(f"state must be dict, got {type(state).__name__}")
    failed_tasks = state.get("failed_tasks") or []
    if len(failed_tasks) < settings.MIN_MONTHLY_FAIL_TASKS:
        return "minimal_report"
    return "build_similarity_graph"


def _route_after_quality(state: dict) -> str:
    if not isinstance(state, dict):
        raise TypeError(f"state must be dict, got {type(state).__name__}")
    quality_passed = state.get("quality_passed", False)
    retry_count = state.get("retry_count", 0)
    # TypedDict 계약을 기대하지만, 직렬화 과정의 타입 불일치를 방어
    if not isinstance(quality_passed, bool):
        quality_passed = str(quality_passed).lower() not in ("false", "0", "")
    if not isinstance(retry_count, int) or retry_count < 0:
        try:
            retry_count = max(0, int(retry_count))
        except (TypeError, ValueError):
            retry_count = 0
    if quality_passed:
        return END
    if retry_count < 2:
        return "llm_retrospective_report"
    return END


def build_report_graph():
    graph = StateGraph(ReportState)

    graph.add_node("load_monthly_logs", load_logs)
    graph.add_node("too_few_tasks", _too_few_tasks)
    graph.add_node("embed_failures", embed_failures)
    graph.add_node("minimal_report", _minimal_report)
    graph.add_node("build_similarity_graph", build_similarity_graph)
    graph.add_node("extract_clusters", extract_clusters)
    graph.add_node("summarize_clusters", summarize_clusters)
    graph.add_node("llm_retrospective_report", llm_report)
    graph.add_node("quality_check", quality_check)

    graph.set_entry_point("load_monthly_logs")

    graph.add_conditional_edges("load_monthly_logs", _check_task_count)
    graph.add_edge("too_few_tasks", END)

    graph.add_conditional_edges("embed_failures", _check_failure_count)
    graph.add_edge("minimal_report", END)

    graph.add_edge("build_similarity_graph", "extract_clusters")
    graph.add_edge("extract_clusters", "summarize_clusters")
    graph.add_edge("summarize_clusters", "llm_retrospective_report")
    graph.add_edge("llm_retrospective_report", "quality_check")
    graph.add_conditional_edges("quality_check", _route_after_quality)

    return graph.compile()


report_graph = build_report_graph()
