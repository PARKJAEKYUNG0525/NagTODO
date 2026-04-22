from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Annotated, Optional

class ReportBase(BaseModel):
    title: str
    date: datetime
    detail: str

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    title: str | None = None
    date: datetime | None = None
    detail: str | None = None

class ReportInDB(BaseModel):
    report_id: str
    title: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    detail: str
    
    class Config:
        from_attributes = True

class ReportRead(ReportInDB):
    pass