"""데모 전용 라우터 — DEMO_MODE=1 환경변수 설정 시에만 main.py에서 마운트됨."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ai.report.graph import report_graph

router = APIRouter(prefix="/ai/demo", tags=["demo"])


class DemoReportRequest(BaseModel):
    user_id: str
    month_start: str = "2026-03-23"
    logs: list[dict]


@router.post("/report")
async def demo_report(req: DemoReportRequest) -> dict:
    """mock log 데이터를 주입해 report 그래프를 실행한다. load_logs HTTP 호출을 건너뜀."""
    state = {
        "user_id": req.user_id,
        "month_start": req.month_start,
        "monthly_logs": req.logs,
    }
    result = await report_graph.ainvoke(state)
    return {
        "retrospective_report": result.get("retrospective_report", ""),
        "category_stats": result.get("category_stats", {}),
        "quality_passed": result.get("quality_passed"),
        "quality_issues": result.get("quality_issues", []),
        "cluster_count": len(result.get("clusters") or []),
    }
