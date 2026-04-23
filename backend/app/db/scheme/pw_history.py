from pydantic import BaseModel
from datetime import datetime

class PwHistoryBase(BaseModel):
    user_id: int
    pw: str
    updated_at: datetime

class PwHistoryCreate(PwHistoryBase):
    pass

class PwHistoryUpdate(PwHistoryBase):
    pass

class PwHistoryInDB(PwHistoryBase):
    pw_history_id: str

    class Config:
        from_attributes = True

class PwHistoryRead(PwHistoryInDB):
    pass