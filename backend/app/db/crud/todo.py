from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.todo import Todo
from app.db.models.user import User
from app.db.models.category import Category
from app.db.scheme.todo import TodoCreate, TodoUpdate
from typing import Optional


# C 생성
def create_todo(db: Session, data: TodoCreate) -> Todo:
    todo = Todo(
        title=data.title,
        detail=data.detail,
        todo_status=data.todo_status,
        visibility=data.visibility,
        user_id=data.user_id,
        category_id=data.category_id,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

# R 조회 - user확인
def get_user(db: Session, user_id: str) -> Optional[User]:
    stmt = select(User).where(User.user_id == user_id)
    return db.scalar(stmt)

# R 조회 - category 존재 확인
def get_category(db: Session, category_id: str) -> Optional[Category]:
    stmt = select(Category).where(Category.category_id == category_id)
    return db.scalar(stmt)

# R 조회 - todo 단일 조회
def get_todo(db: Session, todo_id: str) -> Optional[Todo]:
    stmt = select(Todo).where(Todo.todo_id == todo_id)
    return db.scalar(stmt)

# R 조회 - todo 목록 조회 (user 기준)
def get_all_todos(db: Session, user_id: str) -> list[Todo]:
    stmt = select(Todo).where(Todo.user_id == user_id)
    return list(db.scalars(stmt).all())

# U 수정
def update_todo(db: Session, todo: Todo, data: TodoUpdate) -> Todo:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo

# D 삭제
def delete_todo(db: Session, todo: Todo) -> None:
    db.delete(todo)
    db.commit()
