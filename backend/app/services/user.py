from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.crud import user as user_crud
from app.db.scheme.user import UserCreate, UserUpdate, UserRead 

# C 생성
async def create_user_svc(db: Session, data: UserCreate) -> UserRead:
    if await user_crud.get_email(db, .username):
        raise HTTPException(status_code=400,  detail="이미 사용중인 이름이다")
    hash_pw= get_password_hash(user.password) 
    user_create=UserCreate(username=user.username, password=hash_pw, email=user.email)

    try:
        db_user=await UserCrud.create(db,user_create)
        await db.commit()
        await db.refresh(db_user)
        return db_user
        
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=401, detail="잘못된 이메일 또는 비번이다")
# R 단일 조회
def get_todo_svc(db: Session, todo_id: str) -> TodoRead:
    todo = todo_crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"todo_id '{todo_id}'에 해당하는 todo가 없습니다."
        )
    return TodoRead.model_validate(todo)

# R 전체 조회
def get_all_todos_svc(db: Session, user_id: str) -> list[TodoRead]:
    # user 존재 확인
    user = todo_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user_id '{user_id}'에 해당하는 유저가 없습니다."
        )

    todos = todo_crud.get_all_todos(db, user_id)
    return [TodoRead.model_validate(t) for t in todos]

# U 변경
def update_todo_svc(db: Session, todo_id: str, data: TodoUpdate) -> TodoRead:
    todo = todo_crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"todo_id '{todo_id}'에 해당하는 todo가 없습니다."
        )

    if data.category_id:
        category = todo_crud.get_category(db, data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"category_id '{data.category_id}'에 해당하는 카테고리가 없습니다."
            )

    updated = todo_crud.update_todo(db, todo, data)
    return TodoRead.model_validate(updated)

# D 삭제
def delete_todo_svc(db: Session, todo_id: str) -> dict:
    todo = todo_crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"todo_id '{todo_id}'에 해당하는 todo가 없습니다."
        )

    todo_crud.delete_todo(db, todo)
    return {"message": f"todo_id '{todo_id}' 삭제 완료"}