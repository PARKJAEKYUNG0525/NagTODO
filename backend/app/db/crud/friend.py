from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.friend import Friend
from app.db.models.user import User
from app.db.scheme.friend import FriendCreate, FriendUpdate
from sqlalchemy import or_

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

#---------------------------------------------------------

    # C 생성 - 친구 요청 생성
    @staticmethod
    async def create_friend_request(db: AsyncSession, requester_id: int, receiver_id: int) -> Friend:
        friend = Friend(
            requester_id=requester_id,
            receiver_id=receiver_id,
            status="대기"
        )
        db.add(friend)
        await db.flush() 
        return friend
    
    # R 조회 - 이메일 또는 닉네임으로 유저 검색
    @staticmethod
    async def search_user(db: AsyncSession, current_user_id: int, query: str) -> User | None:
        # 이메일이 일치하거나, 닉네임이 일치하는 유저 1명 검색
        result = await db.execute(
                    select(User).where(
                        or_(
                            User.email.ilike(f"%{query}%"),
                            User.username.ilike(f"%{query}%")
                        ),
                        User.user_id != current_user_id  # 나 자신은 제외
                    )
                )
        return list(result.scalars().all())