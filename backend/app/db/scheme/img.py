from pydantic import BaseModel


class ImgBase(BaseModel):
    title: str
    homepage_id: str


class ImgCreate(ImgBase):
    img_id: str


class ImgUpdate(BaseModel):
    title: str | None = None
    homepage_id: str | None = None


class ImgResponse(ImgBase):
    img_id: str

    class Config:
        from_attributes = True