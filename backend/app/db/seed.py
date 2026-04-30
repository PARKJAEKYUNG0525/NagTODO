from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Category, Img, Music

_DEFAULT_CATEGORIES = [
    ("study",       "공부"),
    ("workout",     "운동"),
    ("daily",       "일상"),
    ("appointment", "약속"),
    ("work",        "업무"),
    ("etc",         "기타"),
]

_DEFAULT_IMGS = [
    {"img_id": "green",           "title": "초록색",  "file_url": "/static/image/green.JPG"},
    {"img_id": "purple",          "title": "보라색",  "file_url": "/static/image/purple.JPG"},
    {"img_id": "hill",            "title": "언덕",    "file_url": "/static/image/hill.JPG"},
    {"img_id": "mountain",        "title": "산",     "file_url": "/static/image/mountain.JPG"},
    {"img_id": "plains",          "title": "평원",    "file_url": "/static/image/plains.JPG"},
    {"img_id": "mountain_night",  "title": "겨울 산",  "file_url": "/static/image/mountain_night.JPG"},
]

_DEFAULT_MUSICS = [
    {
        "music_id": "animalcrossing",
        "title":    "동물의 숲 비둘기 카페",
        "file_url": "/static/music/animalcrossing.mp3",
    },
    {
        "music_id": "campfire",
        "title":    "모닥불 타는 소리",
        "file_url": "/static/music/campfire.mp3",
    },
    {
        "music_id": "mabinogi",
        "title":    "모바일 마비노기 - 1기 테마곡",
        "file_url": "/static/music/mabinogi.mp3",
    },
    {
        "music_id": "maplestory",
        "title":    "메이플스토리 - 샤레니안의기사",
        "file_url": "/static/music/maplestory.mp3",
    },
    {
        "music_id": "pokemon",
        "title":    "포켓몬스터 - 1기 오프닝",
        "file_url": "/static/music/pokemon.mp3",
    },
]

async def seed_categories(session: AsyncSession) -> None:
    result = await session.execute(select(Category.category_id))
    existing_ids = set(result.scalars().all())
    for category_id, name in _DEFAULT_CATEGORIES:
        if category_id not in existing_ids:
            session.add(Category(category_id=category_id, name=name))

async def seed_imgs(session: AsyncSession):
    result = await session.execute(select(Img))
    existing = {i.img_id: i for i in result.scalars().all()}

    for i in _DEFAULT_IMGS:
        if i["img_id"] in existing:
            existing[i["img_id"]].file_url = i["file_url"]
        else:
            session.add(Img(**i))

async def seed_musics(session: AsyncSession):
    result = await session.execute(select(Music))
    existing = {m.music_id: m for m in result.scalars().all()}

    for m in _DEFAULT_MUSICS:
        if m["music_id"] in existing:
            existing[m["music_id"]].file_url = m["file_url"]
        else:
            session.add(Music(**m))