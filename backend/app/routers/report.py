from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.database import get_db
from app.db.scheme.report import ReportCreate, ReportUpdate, ReportRead
from app.services.report import ReportService as report_svc

router = APIRouter(prefix="/reports", tags=["Report"])

# C 생성
@router.post("/", response_model=ReportRead, status_code=201)
async def create_report(data: ReportCreate, db: AsyncSession = Depends(get_db)):
    return await report_svc.create_report_svc(db, data)

# R 단일 조회
@router.get("/{report_id}", response_model=ReportRead)
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    return await report_svc.get_report_svc(db, report_id)

# R 조회 (user_id 필터 or 전체)
@router.get("/", response_model=list[ReportRead])
async def get_reports(
    user_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    if user_id is not None:
        return await report_svc.get_reports_by_user_svc(db, user_id)
    return await report_svc.get_all_reports_svc(db)

# U 수정
@router.patch("/{report_id}", response_model=ReportRead)
async def update_report(report_id: str, data: ReportUpdate, db: AsyncSession = Depends(get_db)):
    return await report_svc.update_report_svc(db, report_id, data)

# D 삭제
@router.delete("/{report_id}")
async def delete_report(report_id: str, db: AsyncSession = Depends(get_db)):
    return await report_svc.delete_report_svc(db, report_id)