from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.scheme.homepage import HomepageCreate, HomepageUpdate, HomepageResponse
from app.services.homepage import HomepageService as homepage_svc

router = APIRouter(prefix="/homepages", tags=["Homepage"])


# C 생성
@router.post("/", response_model=HomepageResponse, status_code=201)
async def create_homepage(data: HomepageCreate, db: AsyncSession = Depends(get_db)):
    return await homepage_svc.create_homepage_svc(db, data)

# R 단일 조회
@router.get("/{homepage_id}", response_model=HomepageResponse)
async def get_homepage(homepage_id: str, db: AsyncSession = Depends(get_db)):
    return await homepage_svc.get_homepage_svc(db, homepage_id)

# R user 기준 조회
@router.get("/user/{user_id}", response_model=HomepageResponse)
async def get_homepage_by_user(user_id: str, db: AsyncSession = Depends(get_db)):
    return await homepage_svc.get_homepage_by_user_svc(db, user_id)

# D 삭제
@router.delete("/{homepage_id}")
async def delete_homepage(homepage_id: str, db: AsyncSession = Depends(get_db)):
    return await homepage_svc.delete_homepage_svc(db, homepage_id)