from pydantic import BaseModel


class HomepageBase(BaseModel):
    user_id: str


class HomepageCreate(HomepageBase):
    homepage_id: str


class HomepageUpdate(BaseModel):
    user_id: str | None = None


class HomepageInDB(HomepageBase):
    homepage_id: str

    class Config:
        from_attributes = True


class HomepageResponse(HomepageInDB):
    pass