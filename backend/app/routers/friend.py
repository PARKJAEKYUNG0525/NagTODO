from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.friend import FriendCreate, FriendUpdate, FriendRead
from app.services.friend import FriendService as friend_svc
from app.db.models.user import User
from app.core.jwt_handle import get_current_user

router = APIRouter(prefix="/friends", tags=["Friend"])

# C 생성 - 친구 신청 보내기
@router.post("/", response_model=FriendRead, status_code=201)
async def create_friend(data: FriendUpdate,
                        db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)
                        ):
    return await friend_svc.create_friend_svc(db, current_user.user_id, data)

# R 조회 - 받은 신청 목록 조회
@router.get("/friend/{friend_id}", response_model=list[FriendRead])
async def get_received_friend(db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(get_current_user)
                             ):
    return await friend_svc.get_receive_svc(db, current_user.user_id)

# U 수정 - 친구 신청 수락/거절
@router.patch("/{friend_id}", response_model=FriendRead)
async def update_friend(friend_id: int,
                        data: FriendUpdate,
                        db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)
                        ):
    return await friend_svc.update_friend_svc(db, current_user.user_id, friend_id, data)

# D 삭제
@router.delete("/{friend_id}")
async def delete_friend(friend_id: int, db: AsyncSession = Depends(get_db)):
    return await friend_svc.delete_friend_svc(db, friend_id)



#-----------------------------------------------------
# 친구 찾기 (이메일 또는 닉네임 검색)
@router.get("/search", response_model=list[FriendRead])
async def search_friend(query: str = Query(..., description="이메일 또는 닉네임 입력"),
                        db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)
                        ):

    return await friend_svc.search_friend_svc(db, current_user, query)

# 친구 신청 보내기
@router.post("/", response_model=FriendRead, status_code=201)
async def create_friend(data: FriendUpdate, 
                        db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)
                        ):
    
    return await friend_svc.send_request_svc(db, current_user.user_id, data.receiver_id)