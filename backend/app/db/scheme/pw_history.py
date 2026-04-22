from pydantic import BaseModel
from datetime import datetime

class PwHistoryBase(BaseModel):
    user_id: str
    pw: str
    updated_at: datetime

class PwHistoryInDB(PwHistoryBase):
    pw_history_id: str

    class Config:
        from_attributes = True