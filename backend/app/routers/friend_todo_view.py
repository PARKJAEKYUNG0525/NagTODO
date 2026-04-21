from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.scheme.friend_todo_view import FriendTodoViewCreate, FriendTodoViewUpdate, FriendTodoViewRead
from app.services.friend_todo_view import FriendTodoViewService as friend_todo_view_svc

router = APIRouter(prefix="/friend-todo-views", tags=["FriendTodoView"])

# C 생성
@router.post("/", response_model=FriendTodoViewRead, status_code=201)
def create_friend_todo_view(data: FriendTodoViewCreate, db: Session = Depends(get_db)):
    return friend_todo_view_svc.create_friend_todo_view_svc(db, data)

# R 단일 조회
@router.get("/{friend_todo_view_id}", response_model=FriendTodoViewRead)
def get_friend_todo_view(friend_todo_view_id: int, db: Session = Depends(get_db)):
    return friend_todo_view_svc.get_friend_todo_view_svc(db, friend_todo_view_id)

# R 전체 조회 - User
@router.get("/user/{user_id}", response_model=list[FriendTodoViewRead])
def get_friend_todo_views_by_user(user_id: str, db: Session = Depends(get_db)):
    return friend_todo_view_svc.get_all_friend_todo_views_by_user_svc(db, user_id)

# R 전체 조회 - Todo
@router.get("/todo/{todo_id}", response_model=list[FriendTodoViewRead])
def get_friend_todo_views_by_todo(todo_id: str, db: Session = Depends(get_db)):
    return friend_todo_view_svc.get_all_friend_todo_views_by_todo_svc(db, todo_id)

# U 수정
@router.patch("/{friend_todo_view_id}", response_model=FriendTodoViewRead)
def update_friend_todo_view(friend_todo_view_id: int, data: FriendTodoViewUpdate, db: Session = Depends(get_db)):
    return friend_todo_view_svc.update_friend_todo_view_svc(db, friend_todo_view_id, data)

# D 삭제
@router.delete("/{friend_todo_view_id}")
def delete_friend_todo_view(friend_todo_view_id: int, db: Session = Depends(get_db)):
    return friend_todo_view_svc.delete_friend_todo_view_svc(db, friend_todo_view_id)