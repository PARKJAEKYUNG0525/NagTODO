# history 테이블 제거 후 todo 테이블로 통합 — 코드 보존용 주석처리
#
# from pydantic import BaseModel
# from datetime import datetime
#
# class HistoryBase(BaseModel):
#     user_id: int
#     title: str
#     todo_status: str
#     archived_at: datetime
#     category_name: str
#
# class HistoryCreate(HistoryBase):
#     pass
#
# class HistoryUpdate(BaseModel):
#     user_id: int | None = None
#     title: str | None = None
#     todo_status: str | None = None
#     archived_at: datetime | None = None
#     category_name: str | None = None
#
# class HistoryInDB(BaseModel):
#     history_id: str
#     user_id: int
#     title: str
#     todo_status: str
#     archived_at: datetime
#     category_name: str
#
#     class Config:
#         from_attributes = True
#
# class HistoryRead(HistoryInDB):
#     pass
