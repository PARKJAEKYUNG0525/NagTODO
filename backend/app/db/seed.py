from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Category, Music

_DEFAULT_CATEGORIES = [
    ("study",       "공부"),
    ("workout",     "운동"),
    ("daily",       "일상"),
    ("appointment", "약속"),
    ("work",        "업무"),
    ("etc",         "기타"),
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

async def seed_music(session: AsyncSession):
    result = await session.execute(select(Music))
    existing = {m.music_id for m in result.scalars().all()}

    for m in _DEFAULT_MUSICS:
        if m["music_id"] in existing:
            continue
        session.add(Music(**m))