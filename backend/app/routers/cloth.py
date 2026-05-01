from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.scheme.cloth import ClothCreate, ClothUpdate, ClothRead
from app.services.cloth import ClothService as cloth_svc

router = APIRouter(prefix="/cloths", tags=["Cloth"])

# C 생성
@router.post("/", response_model=ClothRead, status_code=201)
async def create_todo(data: ClothCreate, db: Session = Depends(get_db)):
    return await cloth_svc.create_cloth_svc(db, data)

# R 단일 조회
@router.get("/{cloth_id}", response_model=ClothRead)
async def get_todo(cloth_id: str, db: Session = Depends(get_db)):
    return await cloth_svc.get_cloth_svc(db, cloth_id)

# R 전체 조회 - 유저별
@router.get("/user/{user_id}", response_model=list[ClothRead])
async def get_cloths_by_user(user_id: int, db: Session = Depends(get_db)):
    return await cloth_svc.get_all_cloths_svc(db, user_id)

# U 수정
@router.patch("/{cloth_id}", response_model=ClothRead)
async def update_cloth(cloth_id: str, data: ClothUpdate, db: Session = Depends(get_db)):
    return await cloth_svc.update_cloth_svc(db, cloth_id, data)

# D 삭제
@router.delete("/{cloth_id}")
async def delete_cloth(cloth_id: str, db: Session = Depends(get_db)):
    return await cloth_svc.delete_cloth_svc(db, cloth_id)