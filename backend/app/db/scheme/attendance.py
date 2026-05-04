from pydantic import BaseModel
from datetime import date

class AttendanceBase(BaseModel):
    attended_at: date

class AttendanceCreate(BaseModel):
    pass

class AttendanceInDB(AttendanceBase):
    user_id: int

    class Config:
        from_attributes = True

class AttendanceRead(AttendanceInDB):
    pass

class AttendanceResponse(BaseModel):
    is_first_today: bool
    total_days: int

    reward_cloth_id: str | None = None
    reward_cloth_title: str | None = None
    reward_cloth_file_url: str | None = None