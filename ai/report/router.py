from __future__ import annotations

import calendar
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, model_validator

from ai.report.graph import report_graph

router = APIRouter()


class MonthlyReportRequest(BaseModel):
    user_id: str
    year: Optional[int] = None        # 캘린더 월 모드: 연도 (예: 2026)
    month: Optional[int] = None       # 캘린더 월 모드: 월 (1–12)
    month_start: Optional[str] = None  # 커스텀 범위 모드: "YYYY-MM-DD"
    month_end: Optional[str] = None    # 커스텀 범위 모드: "YYYY-MM-DD"

    @field_validator("user_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("빈 문자열은 허용되지 않습니다")
        return v

    @model_validator(mode="after")
    def validate_inputs(self) -> "MonthlyReportRequest":
        if (self.year is None) != (self.month is None):
            raise ValueError("year와 month는 함께 입력하거나 둘 다 생략해야 합니다")
        if self.month is not None and not (1 <= self.month <= 12):
            raise ValueError("month는 1–12 사이여야 합니다")
        if self.year is not None and self.year < 2000:
            raise ValueError("year는 2000 이상이어야 합니다")
        if (self.month_start is None) != (self.month_end is None):
            raise ValueError("month_start와 month_end는 함께 입력하거나 둘 다 생략해야 합니다")
        return self


def _rolling_window() -> tuple[str, str]:
    """현재 시각 기준 최근 30일 구간을 반환한다."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=30)
    return start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")


def _calendar_window(year: int, month: int) -> tuple[str, str]:
    """지정한 연·월의 첫날과 마지막날을 반환한다."""
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year:04d}-{month:02d}-01"
    end = f"{year:04d}-{month:02d}-{last_day:02d}"
    return start, end


@router.post("/ai/report/monthly")
async def monthly_report(req: MonthlyReportRequest):
    if req.year is not None:
        month_start, month_end = _calendar_window(req.year, req.month)
    elif req.month_start is not None:
        month_start, month_end = req.month_start, req.month_end
    else:
        month_start, month_end = _rolling_window()

    initial_state = {
        "user_id": req.user_id,
        "month_start": month_start,
        "month_end": month_end,
        "monthly_logs": None,  # None → load_logs가 백엔드 API 호출
        "failed_tasks": [],
        "category_stats": {},
        "failure_embeddings": [],
        "similarity_graph": None,
        "clusters": [],
        "cluster_summaries": [],
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

    report = result.get("retrospective_report", "")
    if not report:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "리포트 생성 실패: 결과가 비어 있습니다",
                "quality_issues": result.get("quality_issues", []),
            },
        )

    return {
        "month_start": month_start,
        "month_end": month_end,
        "category_stats": result.get("category_stats", {}),
        "clusters": result.get("clusters", []),
        "cluster_summaries": result.get("cluster_summaries", []),
        "report": report,
        "quality_passed": result.get("quality_passed", False),
        "quality_issues": result.get("quality_issues", []),
    }
