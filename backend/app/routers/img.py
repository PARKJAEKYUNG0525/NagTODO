from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.scheme.img import ImgCreate, ImgUpdate, ImgResponse
from app.services.img import ImgService as img_svc

router = APIRouter(prefix="/imgs", tags=["Img"])

# C 생성
@router.post("/", response_model=ImgResponse, status_code=201)
def create_img(data: ImgCreate, db: Session = Depends(get_db)):
    return img_svc.create_img_svc(db, data)

# R 단일 조회
@router.get("/{img_id}", response_model=ImgResponse)
def get_img(img_id: str, db: Session = Depends(get_db)):
    return img_svc.get_img_svc(db, img_id)

# R homepage 기준 조회
@router.get("/homepage/{homepage_id}", response_model=list[ImgResponse])
def get_imgs_by_homepage(homepage_id: str, db: Session = Depends(get_db)):
    return img_svc.get_all_imgs_by_homepage_svc(db, homepage_id)

# U 수정
@router.patch("/{img_id}", response_model=ImgResponse)
def update_img(img_id: str, data: ImgUpdate, db: Session = Depends(get_db)):
    return img_svc.update_img_svc(db, img_id, data)

# D 삭제
@router.delete("/{img_id}")
def delete_img(img_id: str, db: Session = Depends(get_db)):
    return img_svc.delete_img_svc(db, img_id)