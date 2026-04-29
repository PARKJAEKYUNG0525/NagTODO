from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.report import ReportCrud 
from app.db.scheme.report import ReportCreate, ReportUpdate
from app.db.models.report import Report

class ReportService:

    # C 생성
    @staticmethod
    async def create_report_svc(db: AsyncSession, data: ReportCreate) -> Report:
        try:
            report = await ReportCrud.create_report(db, data)
            await db.commit()
            await db.refresh(report)
            return report

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="report 생성에 실패했습니다."
            )

    # R 조회 - 리포트 단일 조회
    @staticmethod
    async def get_report_svc(db: AsyncSession, report_id: str) -> Report:
        report = await ReportCrud.get_report(db, report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"report_id '{report_id}'에 해당하는 report가 없습니다."
            )
        return report

    # R 조회 - 리포트 전체 조회
    @staticmethod
    async def get_all_reports_svc(db: AsyncSession) -> list[Report]:
        reports = await ReportCrud.get_all_reports(db)
        return reports

    # R 조회 - user_id별 리포트 조회 (최신순)
    @staticmethod
    async def get_reports_by_user_svc(db: AsyncSession, user_id: int) -> list[Report]:
        return await ReportCrud.get_reports_by_user(db, user_id)

    # U 수정
    @staticmethod
    async def update_report_svc(db: AsyncSession, report_id: str, data: ReportUpdate) -> Report:
        report = await ReportCrud.get_report(db, report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"report_id '{report_id}'에 해당하는 report가 없습니다."
            )

        try:
            updated = await ReportCrud.update_report(db, report, data)
            await db.commit()
            await db.refresh(updated)
            return updated

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="report 수정에 실패했습니다."
            )
        
    # D 삭제
    @staticmethod
    async def delete_report_svc(db: AsyncSession, report_id: str) -> dict:
        report = await ReportCrud.get_report(db, report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"report_id '{report_id}'에 해당하는 report가 없습니다."
            )

        try:
            await ReportCrud.delete_report(db, report)
            await db.commit()
            return {"message": f"report_id '{report_id}' 삭제 완료"}

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="report 삭제에 실패했습니다."
            )