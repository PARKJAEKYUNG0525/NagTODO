# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.db.database import get_db
# from app.db.scheme.homepage import HomepageCreate, HomepageUpdate, HomepageResponse
# from app.services.homepage import HomepageService as homepage_svc
#
# router = APIRouter(prefix="/homepages", tags=["Homepage"])
#
# # C 생성
# @router.post("/", response_model=HomepageResponse, status_code=201)
# def create_homepage(data: HomepageCreate, db: Session = Depends(get_db)):
#     return homepage_svc.create_homepage_svc(db, data)
#
# # R 단일 조회
# @router.get("/{homepage_id}", response_model=HomepageResponse)
# def get_homepage(homepage_id: str, db: Session = Depends(get_db)):
#     return homepage_svc.get_homepage_svc(db, homepage_id)
#
# # R user 기준 조회
# @router.get("/user/{user_id}", response_model=HomepageResponse)
# def get_homepage_by_user(user_id: int, db: Session = Depends(get_db)):
#     return homepage_svc.get_homepage_by_user_svc(db, user_id)
#
# # U 수정
# @router.patch("/{homepage_id}", response_model=HomepageResponse)
# def update_homepage(homepage_id: str, data: HomepageUpdate, db: Session = Depends(get_db)):
#     return homepage_svc.update_homepage_svc(db, homepage_id, data)
#
# # D 삭제
# @router.delete("/{homepage_id}")
# def delete_homepage(homepage_id: str, db: Session = Depends(get_db)):
#     return homepage_svc.delete_homepage_svc(db, homepage_id)