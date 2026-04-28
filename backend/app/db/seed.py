from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.category import Category

_DEFAULT_CATEGORIES = [
    ("study",       "공부"),
    ("workout",     "운동"),
    ("daily",       "일상"),
    ("appointment", "약속"),
    ("work",        "업무"),
    ("etc",         "기타"),
]

async def seed_categories(session: AsyncSession) -> None:
    result = await session.execute(select(Category.category_id))
    existing_ids = set(result.scalars().all())
    for category_id, name in _DEFAULT_CATEGORIES:
        if category_id not in existing_ids:
            session.add(Category(category_id=category_id, name=name))
