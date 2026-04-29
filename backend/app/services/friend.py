from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.crud.friend import FriendCrud
from app.db.scheme.friend import FriendCreate, FriendUpdate, FriendRead  
from app.db.models.friend import Friend

class FriendService:

    # C 생성 (친구 신청 보내기)
    @staticmethod
    async def create_friend_svc(db: AsyncSession, requester_id: int, data: FriendCreate) -> Friend:
        # receiver 존재 확인
        receiver = await FriendCrud.get_user(db, data.receiver_id)
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"receiver_id '{data.receiver_id}'에 해당하는 유저가 없습니다."
            )

        # 자신한테 신청하는 지 확인
        if requester_id == data.receiver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="자기 자신에게 친구 신청을 보낼 수 없습니다."
            )
        
        try:
            friend = await FriendCrud.create_friend(db, requester_id, data)
            await db.commit()
            await db.refresh(friend)
            return friend

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="친구 신청 보내기에 실패했습니다."
            )

    # R 조회 - 받은 신청 목록 조회
    @staticmethod
    async def get_receive_svc(db: AsyncSession, user_id: int) -> list[Friend]:
    # async def get_receive_svc(db, user_id):
        result = await FriendCrud.get_receive(db, user_id)
        if not result:
            return []  # 404 대신 빈 배열 반환
        return result

    # U 수정 (친구 신청 수락 / 거절)
    @staticmethod
    async def update_friend_svc(db: AsyncSession, user_id: int, friend_id: int, data: FriendUpdate) -> Friend:
        #해당 신청 내역이 존재하는지 확인
        friend = await FriendCrud.get_friend(db, friend_id)
        if not friend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"friend_id '{friend_id}'에 해당하는 friend가 없습니다."
            )

        # 내가 받은 신청이 맞는지 확인 (수신자만 수락/거절 가능)
        if friend.receiver_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="본인에게 온 신청만 처리할 수 있습니다."
            )
        
        # 이미 처리된 상태인지 확인
        if friend.status != "대기":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 처리된 상태입니다"
            )
        
        try:
            updated = await FriendCrud.update_friend(db, friend, data)
            await db.commit()
            await db.refresh(updated)
            return updated

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="friend 수정에 실패했습니다."
            )
        
    # D 삭제
    @staticmethod
    async def delete_friend_svc(db: AsyncSession, friend_id: int) -> dict:
        friend = await FriendCrud.get_friend(db, friend_id)
        if not friend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"friend_id '{friend_id}'에 해당하는 todo가 없습니다."
            )

        try:
            await FriendCrud.delete_friend(db, friend)
            await db.commit()
            return {"message": f"friend_id '{friend_id}' 삭제 완료"}

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="friend 삭제에 실패했습니다."
            )
        
    @staticmethod
    async def get_accepted_svc(db: AsyncSession, user_id: int):
        result = await FriendCrud.get_all_friends(db, user_id)
        return [FriendRead.from_orm_with_users(f) for f in result] if result else []
        

    # 검색 (이메일/닉네임 통합 검색)
    @staticmethod
    async def search_friend_svc(db: AsyncSession, query: str):
        user = await FriendCrud.search_user(db, query)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="일치하는 유저를 찾을 수 없습니다."
            )
        return user

    # 신청 보내기
    @staticmethod
    async def send_request_svc(db: AsyncSession, requester_id: int, receiver_id: int):
        # 본인 확인
        if receiver_id == requester_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="본인에게 친구 신청을 보낼 수 없습니다."
            )
        
        # 중복 신청 확인 ← 추가
        existing = await FriendCrud.get_existing_request(db, requester_id, receiver_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 친구 신청을 보냈습니다."
            )
        
        try:
            new_req = await FriendCrud.create_request(db, requester_id, receiver_id)
            await db.commit()      
            await db.refresh(new_req) 
            return new_req
        
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="친구 신청 보내기에 실패했습니다."
            )
        




