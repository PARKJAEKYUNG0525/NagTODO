from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.notification import NotificationCrud
from app.db.scheme.notification import NotificationCreate, NotificationUpdate
from app.db.models.notification import Notification

class NotificationService:

    # C 생성
    @staticmethod
    async def create_notification_svc(db: AsyncSession, data: NotificationCreate) -> Notification:
        # user 존재 확인
        user = await NotificationCrud.get_user(db, data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id '{data.user_id}'에 해당하는 유저가 없습니다."
            )

        try:
            notification = await NotificationCrud.create_notification(db, data)
            await db.commit()
            await db.refresh(notification)
            return notification

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="notification 생성에 실패했습니다."
            )

    # R 조회 - 단일 조회
    @staticmethod
    async def get_notification_svc(db: AsyncSession, notification_id: int) -> Notification:
        notification = await NotificationCrud.get_notification(db, notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"notification_id '{notification_id}'에 해당하는 데이터가 없습니다."
            )
        return notification

    # R 조회 - 목록 조회 (user 기준)
    @staticmethod
    async def get_all_notifications_by_user_svc(db: AsyncSession, user_id: int) -> list[Notification]:
        notifications = await NotificationCrud.get_notifications_by_user(db, user_id)
        return notifications

    # R 조회 - 전체 조회
    @staticmethod
    async def get_all_notifications_svc(db: AsyncSession) -> list[Notification]:
        notifications = await NotificationCrud.get_all_notifications(db)
        return notifications

    # U 수정 (읽음 처리 포함)
    @staticmethod
    async def update_notification_svc(db: AsyncSession,notification_id: int,data: NotificationUpdate) -> Notification:
        notification = await NotificationCrud.get_notification(db, notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"notification_id '{notification_id}'에 해당하는 데이터가 없습니다."
            )

        try:
            updated = await NotificationCrud.update_notification(db, notification, data)
            await db.commit()
            await db.refresh(updated)
            return updated

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="notification 수정에 실패했습니다."
            )