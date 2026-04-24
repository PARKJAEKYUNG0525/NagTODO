from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.friend import Friend
from app.db.models.user import User
from app.db.scheme.friend import FriendCreate, FriendUpdate

class FriendCrud:

    # C 생성
    @staticmethod
    async def create_friend(db: AsyncSession, requester_id: int, data: FriendCreate) -> Friend:
        friend = Friend(
            requester_id=requester_id,
            receiver_id=data.receiver_id,
            status="대기"
        )
        db.add(friend)
        await db.flush()
        return friend

    # R 조회 - user 존재 확인
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    # R 조회 - friend 단일 조회
    @staticmethod
    async def get_friend(db: AsyncSession, friend_id: int) -> Friend | None:
        result = await db.execute(select(Friend).where(Friend.friend_id == friend_id))
        return result.scalar_one_or_none()

    # R 조회 - 신청 받은 목록 조회 (대기 상태)
    @staticmethod
    async def get_receive(db: AsyncSession, receiver_id: int) -> list[Friend]:
        result = await db.execute(select(Friend).where(
                                                Friend.receiver_id == receiver_id,
                                                Friend.status == "대기"
                                 ))
        return list(result.scalars().all())
    
    # R 조회 - 친구 목록 조회 (수락 상태)
    @staticmethod
    async def get_all_friends(db: AsyncSession, user_id: int) -> list[Friend]:
        result = await db.execute(select(Friend).where(
                                                (Friend.requester_id == user_id) | (Friend.receiver_id == user_id),
                                                Friend.status == "수락"
                                 ))
        return list(result.scalars().all())

    # U 수정
    @staticmethod
    async def update_friend(db: AsyncSession, friend: Friend, data: FriendUpdate) -> Friend:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(friend, key, value)
        await db.flush()
        return friend

    # D 삭제
    @staticmethod
    async def delete_friend(db: AsyncSession, friend: Friend) -> None:
        await db.delete(friend)
        await db.flush()