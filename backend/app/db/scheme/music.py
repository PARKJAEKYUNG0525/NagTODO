from pydantic import BaseModel


class MusicBase(BaseModel):
    music_id: str
    title: str
    file_url: str
    # homepage_id: str


class MusicCreate(MusicBase):
    pass


class MusicUpdate(BaseModel):
    music_id: str | None = None
    title: str | None = None
    file_url: str | None = None
    # homepage_id: str | None = None


class MusicInDB(MusicBase):
    pass

    class Config:
        from_attributes = True


class MusicRead(MusicInDB):
    pass