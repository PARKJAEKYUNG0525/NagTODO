# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi import HTTPException, status
# from app.db.crud.homepage import HomepageCrud
# from app.db.scheme.homepage import HomepageCreate, HomepageUpdate
# from app.db.models.homepage import Homepage
#
#
# class HomepageService:
#
#     # C 생성
#     @staticmethod
#     async def create_homepage_svc(db: AsyncSession, data: HomepageCreate) -> Homepage:
#         # user 존재 확인
#         user = await HomepageCrud.get_user(db, data.user_id)
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"user_id '{data.user_id}'에 해당하는 유저가 없습니다."
#             )
#
#         try:
#             homepage = await HomepageCrud.create_homepage(db, data)
#             await db.commit()
#             await db.refresh(homepage)
#             return homepage
#
#         except Exception:
#             await db.rollback()
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="homepage 생성에 실패했습니다."
#             )
#
#     # R 조회 - 단일 조회
#     @staticmethod
#     async def get_homepage_svc(db: AsyncSession, homepage_id: str) -> Homepage:
#         homepage = await HomepageCrud.get_homepage(db, homepage_id)
#         if not homepage:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"homepage_id '{homepage_id}'에 해당하는 데이터가 없습니다."
#             )
#         return homepage
#
#     # R 조회 - user 기준 단일 조회
#     @staticmethod
#     async def get_homepage_by_user_svc(db: AsyncSession, user_id: int) -> Homepage:
#         homepage = await HomepageCrud.get_homepage_by_user(db, user_id)
#         if not homepage:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"user_id '{user_id}'에 해당하는 homepage가 없습니다."
#             )
#         return homepage
#
#     # U 수정
#     @staticmethod
#     async def update_homepage_svc(db: AsyncSession, homepage_id: str, data: HomepageUpdate) -> Homepage:
#         homepage = await HomepageCrud.get_homepage(db, homepage_id)
#         if not homepage:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"homepage_id '{homepage_id}'에 해당하는 데이터가 없습니다."
#             )
#
#         try:
#             updated = await HomepageCrud.update_homepage(db, homepage, data)
#             await db.commit()
#             await db.refresh(updated)
#             return updated
#
#         except Exception:
#             await db.rollback()
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="homepage 수정에 실패했습니다."
#             )
#
#     # D 삭제
#     @staticmethod
#     async def delete_homepage_svc(db: AsyncSession, homepage_id: str) -> dict:
#         homepage = await HomepageCrud.get_homepage(db, homepage_id)
#         if not homepage:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"homepage_id '{homepage_id}'에 해당하는 데이터가 없습니다."
#             )
#
#         try:
#             await HomepageCrud.delete_homepage(db, homepage)
#             await db.commit()
#             return {"message": f"homepage_id '{homepage_id}' 삭제 완료"}
#
#         except Exception:
#             await db.rollback()
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="homepage 삭제에 실패했습니다."
#             )