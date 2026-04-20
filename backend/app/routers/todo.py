from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.scheme.todo import TodoCreate, TodoUpdate, TodoRead
from app.services.todo import TodoService as todo_svc

router = APIRouter(prefix="/todos", tags=["Todo"])

# C 생성
@router.post("/", response_model=TodoRead, status_code=201)
def create_todo(data: TodoCreate, db: Session = Depends(get_db)):
    return todo_svc.create_todo_svc(db, data)

# R 단일 조회
@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: str, db: Session = Depends(get_db)):
    return todo_svc.get_todo_svc(db, todo_id)

# R 전체 조회 - 유저별
@router.get("/user/{user_id}", response_model=list[TodoRead])
def get_todos_by_user(user_id: str, db: Session = Depends(get_db)):
    return todo_svc.get_all_todos_svc(db, user_id)

# U 수정
@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: str, data: TodoUpdate, db: Session = Depends(get_db)):
    return todo_svc.update_todo_svc(db, todo_id, data)

# D 삭제
@router.delete("/{todo_id}")
def delete_todo(todo_id: str, db: Session = Depends(get_db)):
    return todo_svc.delete_todo_svc(db, todo_id)