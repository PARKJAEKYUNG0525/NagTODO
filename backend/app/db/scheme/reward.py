from pydantic import BaseModel, Field
from datetime import datetime, timezone

class RewardBase(BaseModel):
    cloth_id: str

class RewardCreate(RewardBase):
    pass

class RewardInDB(RewardBase):
    user_id: int
    unlocked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True

class RewardRead(RewardInDB):
    cloth_title: str | None = None
    cloth_file_url: str | None = None

    @classmethod
    def from_orm_with_cloth(cls, reward):
        return cls(
            user_id=reward.user_id,
            cloth_id=reward.cloth_id,
            unlocked_at=reward.unlocked_at,
            cloth_title=reward.cloth.title if reward.cloth else None,
            cloth_file_url=reward.cloth.file_url if reward.cloth else None,
        )