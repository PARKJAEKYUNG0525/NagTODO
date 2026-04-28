# from pydantic import BaseModel
#
#
# class HomepageBase(BaseModel):
#     user_id: int
#
#
# class HomepageCreate(HomepageBase):
#     homepage_id: str
#
#
# class HomepageUpdate(BaseModel):
#     user_id: int | None = None
#
#
# class HomepageInDB(HomepageBase):
#     homepage_id: str
#
#     class Config:
#         from_attributes = True
#
#
# class HomepageResponse(HomepageInDB):
#     pass