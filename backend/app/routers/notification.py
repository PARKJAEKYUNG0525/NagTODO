from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.notification import NotificationCreate, NotificationUpdate, NotificationResponse

from app.services.notification import NotificationService as notification_svc

router = APIRouter(prefix="/notifications", tags=["Notification"])

# C 생성
@router.post("/", response_model=NotificationResponse, status_code=201)
async def create_notification(data: NotificationCreate, db: AsyncSession = Depends(get_db)):
    return await notification_svc.create_notification_svc(db, data)

# R 단일 조회
@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(notification_id: int, db: AsyncSession = Depends(get_db)):
    return await notification_svc.get_notification_svc(db, notification_id)

# R 전체 조회 - user 기준
@router.get("/user/{user_id}", response_model=list[NotificationResponse])
async def get_notifications_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await notification_svc.get_all_notifications_by_user_svc(db, user_id)


# R 전체 조회
@router.get("/", response_model=list[NotificationResponse])
async def get_all_notifications(db: AsyncSession = Depends(get_db)):
    return await notification_svc.get_all_notifications_svc(db)

# U 수정
@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(notification_id: int, data: NotificationUpdate, db: AsyncSession = Depends(get_db)):
    return await notification_svc.update_notification_svc(db, notification_id, data)