from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.scheme.img import ImgCreate, ImgUpdate, ImgRead
from app.services.img import ImgService as img_svc

router = APIRouter(prefix="/imgs", tags=["Img"])

# C 생성
@router.post("/", response_model=ImgRead, status_code=201)
async def create_img(data: ImgCreate, db: Session = Depends(get_db)):
    return await img_svc.create_img_svc(db, data)

# R 조회 - 전체 조회
@router.get("/", response_model=list[ImgRead])
async def get_all_imgs(db: Session = Depends(get_db)):
    return await img_svc.get_all_imgs_svc(db)

# R 조회 - 단일 조회
@router.get("/{img_id}", response_model=ImgRead)
async def get_img(img_id: str, db: Session = Depends(get_db)):
    return await img_svc.get_img_svc(db, img_id)

# R 조회 - homepage 기준 단일 조회
# @router.get("/homepage/{homepage_id}", response_model=ImgRead)
# def get_imgs_by_homepage(homepage_id: str, db: Session = Depends(get_db)):
#     return img_svc.get_img_by_homepage_svc(db, homepage_id)

# U 수정
@router.patch("/{img_id}", response_model=ImgRead)
async def update_img(img_id: str, data: ImgUpdate, db: Session = Depends(get_db)):
    return await img_svc.update_img_svc(db, img_id, data)

# D 삭제
@router.delete("/{img_id}")
async def delete_img(img_id: str, db: Session = Depends(get_db)):
    return await img_svc.delete_img_svc(db, img_id)