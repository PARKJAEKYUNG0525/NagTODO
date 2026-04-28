from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.notification import Notification
from app.db.models.user import User
from app.db.scheme.notification import NotificationCreate, NotificationUpdate

class NotificationCrud:

    # C 생성
    @staticmethod
    async def create_notification(db: AsyncSession, data: NotificationCreate) -> Notification:
        notification = Notification(**data.model_dump())
        db.add(notification)
        await db.flush()
        return notification

    # R 조회 - user 존재 확인
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    # R 조회 - 단일 조회
    @staticmethod
    async def get_notification(db: AsyncSession, notification_id: int) -> Notification | None:
        result = await db.execute(select(Notification).where(Notification.notification_id == notification_id))
        return result.scalar_one_or_none()

    # R 조회 - user 기준 조회 (특정 user_id가 가진 알림 목록 전부 가져옴)
    @staticmethod
    async def get_notifications_by_user(db: AsyncSession, user_id: int) -> list[Notification]:
        result = await db.execute(select(Notification).where(Notification.user_id == user_id))
        return list(result.scalars().all())

    # R 조회 - 전체 조회
    @staticmethod
    async def get_all_notifications(db: AsyncSession) -> list[Notification]:
        result = await db.execute(select(Notification))
        return list(result.scalars().all())

    # U 수정
    @staticmethod
    async def update_notification(db: AsyncSession, notification: Notification, data: NotificationUpdate) -> Notification:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(notification, key, value)
        await db.flush()
        return notification