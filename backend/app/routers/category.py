from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.services.category import CategoryService as category_svc

router = APIRouter(prefix="/category", tags=["Category"])

# C 생성
@router.post("/", response_model=CategoryRead, status_code=201)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await category_svc.create_category_svc(db, data)

# R 단일 조회
@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: str, db: AsyncSession = Depends(get_db)):
    return await category_svc.get_category_svc(db, category_id)

# R 전체 조회
@router.get("/", response_model=list[CategoryRead])
async def get_all_category(db: AsyncSession = Depends(get_db)):
    return await category_svc.get_all_category_svc(db)

# U 수정
@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(category_id: str, data: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    return await category_svc.update_category_svc(db, category_id, data)

# D 삭제
@router.delete("/{category_id}")
async def delete_category(category_id: str, db: AsyncSession = Depends(get_db)):
    return await category_svc.delete_category_svc(db, category_id)