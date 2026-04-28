from pydantic import BaseModel


class ClothBase(BaseModel):
    cloth_id: str
    title: str
    file_url : str
    user_id: int


class ClothCreate(ClothBase):
    pass 


class ClothUpdate(BaseModel):
    cloth_id: str | None = None
    title: str | None = None
    file_url: str | None = None
    user_id: int | None = None


class ClothInDB(ClothBase):
    pass 

    class Config:
        from_attributes = True


class ClothRead(ClothInDB):
    pass