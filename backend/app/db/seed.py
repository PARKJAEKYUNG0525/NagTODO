from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Category, Cloth, Img, Music
from app.db.models.user import User
from datetime import date
import bcrypt
import os

_DEFAULT_CATEGORIES = [
    ("study",       "공부"),
    ("workout",     "운동"),
    ("daily",       "일상"),
    ("appointment", "약속"),
    ("work",        "업무"),
    ("etc",         "기타"),
]

_CLOTHS_DEFAULT = [
    {"cloth_id": "default_1",     "title": "가리키는_Default", "file_url": "/static/cloth/가리키는_Default.png"},
    {"cloth_id": "default_2",     "title": "거만한_Default",   "file_url": "/static/cloth/거만한_Default.png"},
    {"cloth_id": "default_3",     "title": "노래_Default",    "file_url": "/static/cloth/노래_Default.png"},
    {"cloth_id": "default_4",     "title": "누워있는_Default", "file_url": "/static/cloth/누워있는_Default.png"},
    {"cloth_id": "default_5",     "title": "눈반짝_Default",   "file_url": "/static/cloth/눈반짝_Default.png"},
    {"cloth_id": "default_6",     "title": "드르렁_Default",   "file_url": "/static/cloth/드르렁_Default.png"},
    {"cloth_id": "default_7",     "title": "앉아있는_default",  "file_url": "/static/cloth/앉아있는_default.png"},
    {"cloth_id": "default_8",     "title": "웃음_Default",     "file_url": "/static/cloth/웃음_Default.png"},
    {"cloth_id": "default_9",     "title": "인사_Default",     "file_url": "/static/cloth/인사_Default.png"},
    {"cloth_id": "default_10",    "title": "째려보는_Default",  "file_url": "/static/cloth/째려보는_Default.png"},
]

_CLOTHS_CROISSANT = [
    {"cloth_id": "croissant_1",   "title": "앉아있는_Croissant", "file_url": "/static/cloth/앉아있는_Croissant.png"},
    {"cloth_id": "croissant_2",   "title": "째려보는_Croissant", "file_url": "/static/cloth/째려보는_Croissant.png"},
    {"cloth_id": "croissant_3",   "title": "가리키는_Croissant", "file_url": "/static/cloth/가리키는_Croissant.png"},
    {"cloth_id": "croissant_4",   "title": "거만한_Croissant",   "file_url": "/static/cloth/거만한_Croissant.png"},
    {"cloth_id": "croissant_5",   "title": "노래_Croissant",    "file_url": "/static/cloth/노래_Croissant.png"},
    {"cloth_id": "croissant_6",   "title": "누워있는_Croissant", "file_url": "/static/cloth/누워있는_Croissant.png"},
    {"cloth_id": "croissant_7",   "title": "눈반짝_Croissant",   "file_url": "/static/cloth/눈반짝_Croissant.png"},
    {"cloth_id": "croissant_8",   "title": "드르렁_Croissant",   "file_url": "/static/cloth/드르렁_Croissant.png"},
    {"cloth_id": "croissant_9",   "title": "웃음_Croissant",    "file_url": "/static/cloth/웃음_Croissant.png"},
    {"cloth_id": "croissant_10",  "title": "인사_Croissant",    "file_url": "/static/cloth/인사_Croissant.png"},
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
    {"music_id": "animalcrossing","title": "동물의 숲 비둘기 카페",      "file_url": "/static/music/animalcrossing.mp3",},
    {"music_id": "campfire",      "title": "모닥불 타는 소리",          "file_url": "/static/music/campfire.mp3",},
    {"music_id": "mabinogi",      "title": "모바일 마비노기 - 1기 테마곡", "file_url": "/static/music/mabinogi.mp3",},
    {"music_id": "maplestory",    "title": "메이플스토리 - 샤레니안의기사", "file_url": "/static/music/maplestory.mp3",},
    {"music_id": "pokemon",       "title": "포켓몬스터 - 1기 오프닝",     "file_url": "/static/music/pokemon.mp3",},
]

async def seed_categories(session: AsyncSession) -> None:
    result = await session.execute(select(Category.category_id))
    existing_ids = set(result.scalars().all())
    for category_id, name in _DEFAULT_CATEGORIES:
        if category_id not in existing_ids:
            session.add(Category(category_id=category_id, name=name))

async def seed_cloths(session: AsyncSession) -> None:
    result = await session.execute(select(Cloth.cloth_id))
    existing_ids = set(result.scalars().all())

    for cloth in _CLOTHS_DEFAULT + _CLOTHS_CROISSANT:
        if cloth["cloth_id"] not in existing_ids:
            session.add(Cloth(
                cloth_id=cloth["cloth_id"],
                title=cloth["title"],
                file_url=cloth["file_url"]
            ))

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

# 관리자 생성
async def seed_admin(session: AsyncSession) -> None:
    result = await session.execute(
        select(User).where(User.role == "admin")
    )
    admin = result.scalar_one_or_none()

    if not admin:
        hashed_pw = bcrypt.hashpw(
            os.getenv("ADMIN_PW", "admin1234").encode(),
            bcrypt.gensalt()
        ).decode()

        admin_user = User(
            email=os.getenv("ADMIN_EMAIL", "admin@admin.com"),
            pw=hashed_pw,
            username="관리자",
            birthday=date(2000, 1, 1),
            state=True,
            role="admin"
        )
        session.add(admin_user)
        print("관리자 계정 생성 완료")
    else:
        print("관리자 계정 이미 존재")