from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.report import Report
from app.db.scheme.report import ReportCreate, ReportUpdate

class ReportCrud:

    # C 생성
    @staticmethod
    async def create_report(db: AsyncSession, data: ReportCreate) -> Report:
        report = Report(**data.model_dump())
        db.add(report)
        await db.flush()
        return report

    # R 조회
    @staticmethod
    async def get_report(db: AsyncSession, report_id: str) -> Report | None:
        result = await db.execute(select(Report).where(Report.report_id == report_id))
        return result.scalar_one_or_none()

    # R 조회 - report 전체 조회
    @staticmethod
    async def get_all_reports(db: AsyncSession) -> list[Report]:
        result = await db.execute(select(Report))
        return list(result.scalars().all())

    # R 조회 - user_id별 조회 (최신순)
    @staticmethod
    async def get_reports_by_user(db: AsyncSession, user_id: int) -> list[Report]:
        from sqlalchemy import desc
        result = await db.execute(
            select(Report).where(Report.user_id == user_id).order_by(desc(Report.date))
        )
        return list(result.scalars().all())

    # U 수정
    @staticmethod
    async def update_report(db: AsyncSession, report: Report, data: ReportUpdate) -> Report:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(report, key, value)
        await db.flush()
        return report

    # D 삭제
    @staticmethod
    async def delete_report(db: AsyncSession, report: Report) -> None:
        await db.delete(report)
        await db.flush()