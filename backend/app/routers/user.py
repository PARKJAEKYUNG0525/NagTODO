from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.scheme.user import UserCreate, UserUpdate, UserRead
from app.services.user import UserService as user_svc

router = APIRouter(prefix="/users", tags=["User"])

# C 생성
@router.post("/", response_model=UserRead, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    return user_svc.create_user_svc(db, data)

# R 단일 조회
@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str, db: Session = Depends(get_db)):
    return user_svc.get_user_svc(db, user_id)

# R 전체 조회 - 유저별
@router.get("/user/{user_id}", response_model=list[UserRead])
def get_all_users(user_id: str, db: Session = Depends(get_db)):
    return user_svc.get_all_users_svc(db, user_id)

# U 수정
@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: str, data: UserUpdate, db: Session = Depends(get_db)):
    return user_svc.update_user_svc(db, user_id, data)

# D 삭제
@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    return user_svc.delete_user_svc(db, user_id)