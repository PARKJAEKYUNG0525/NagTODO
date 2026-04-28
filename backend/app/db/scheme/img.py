from pydantic import BaseModel


class ImgBase(BaseModel):
    img_id: str
    title: str
    file_url: str
    # homepage_id: str


class ImgCreate(ImgBase):
    pass


class ImgUpdate(BaseModel):
    img_id: str | None = None
    title: str | None = None
    file_url: str | None = None
    # homepage_id: str | None = None


class ImgInDB(ImgBase):
    pass

    class Config:
        from_attributes = True


class ImgRead(ImgInDB):
    pass
