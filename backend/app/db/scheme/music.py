from pydantic import BaseModel


class MusicBase(BaseModel):
    title: str
    homepage_id: str


class MusicCreate(MusicBase):
    music_id: str


class MusicUpdate(BaseModel):
    title: str | None = None
    homepage_id: str | None = None


class MusicResponse(MusicBase):
    music_id: str

    class Config:
        from_attributes = True