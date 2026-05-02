from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.db.scheme.attendance import AttendanceResponse
from app.services.attendance import AttendanceService
from app.core.jwt_handle import get_current_user

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("", response_model=AttendanceResponse)
async def attendance(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return await AttendanceService.create_attendance_svc(db, user.user_id)