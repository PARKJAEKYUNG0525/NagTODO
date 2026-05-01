from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional


class ReportBase(BaseModel):
    title: str
    date: datetime
    detail: str


class ReportCreate(ReportBase):
    user_id: int
    month_start: str   # "YYYY-MM-DD"
    month_end: str     # "YYYY-MM-DD"


class ReportUpdate(BaseModel):
    title: str | None = None
    date: datetime | None = None
    detail: str | None = None


class ReportInDB(BaseModel):
    report_id: str
    title: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    detail: str
    user_id: Optional[int] = None
    month_start: Optional[str] = None
    month_end: Optional[str] = None

    class Config:
        from_attributes = True


class ReportRead(ReportInDB):
    pass