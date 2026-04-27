from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from ai.report.graph import report_graph

router = APIRouter()


class MonthlyReportRequest(BaseModel):
    user_id: str

    @field_validator("user_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("빈 문자열은 허용되지 않습니다")
        return v


@router.post("/ai/report/monthly")
async def monthly_report(req: MonthlyReportRequest):
    month_start = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")

    initial_state = {
        "user_id": req.user_id,
        "month_start": month_start,
        "monthly_logs": None,  # None → load_logs가 백엔드 API 호출
        "failed_tasks": [],
        "category_stats": {},
        "failure_embeddings": [],
        "similarity_graph": None,
        "clusters": [],
        "cluster_summaries": [],
        "pattern_analysis": "",
        "retrospective_report": "",
        "retry_count": 0,
        "quality_passed": False,
        "quality_issues": [],
    }

    try:
        result = await report_graph.ainvoke(initial_state)
    except (ConnectionError, TimeoutError) as e:
        return JSONResponse(status_code=503, content={"detail": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

    return {
        "month_start": month_start,
        "category_stats": result.get("category_stats", {}),
        "clusters": result.get("clusters", []),
        "cluster_summaries": result.get("cluster_summaries", []),
        "report": result.get("retrospective_report", ""),
        "quality_passed": result.get("quality_passed", False),
        "quality_issues": result.get("quality_issues", []),
    }
