from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User
from app.db.scheme.users import UserCreate, UserUpdate

# User 테이블과 관련된 CRUD 작업을 모아둔 클래스
class UserCrud:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User|None:
        result = await db.execute(select(User).filter(User.user_id == user_id))
        # scalar_one_or_none() : 결과 1개면 객체 반환, 없으면 none 반환
        return result.scalar_one_or_none()

    # UserCreate는 scheme/users.py에 위치
    @staticmethod
    async def create(db: AsyncSession, user: UserCreate) -> User:
        # db에서 모든 사용자 불러오기(언패킹 연산자 이용)
        db_user = User(**user.model_dump())
        db.add(db_user)
        await db.flush()
        return db_user

    # UserUpdate는 scheme/users.py에 위치
    @staticmethod
    async def update_by_id(db: AsyncSession, user_id: int, user:UserUpdate) -> User|None:
        # db에서 사용자id로 검색하여 사용자 불러오기
        db_user = await db.get(User, user_id)
        # 일치하는 사용자가 있다면
        if db_user:
            # pydantic에서 명시된 필드만 추출해서 dict로 변환
            update_data = user.model_dump(exclude_unset=True)
            # update_data.items() : dict의 요소를 key-value 짝으로 하나씩 추출
            # key, value 두 개의 인자 : 언패킹, {key : value}가 각각 들어감
            for key, value in update_data.items():
                # db_user.key = value와 동일
                setattr(db_user, key, value)
            await db.flush()
            return db_user
        return None

    @staticmethod
    async def delete_by_id(db: AsyncSession, user_id: int) -> User | None:
        # 삭제 전 객체를 가져와서 삭제
        db_user = await db.get(User, user_id)
        if db_user:
            await db.delete(db_user)
            await db.flush()
            return db_user
        return None

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> User | None:
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    # Q. refresh_token 왜 db에 저장하는가 -> A. 재사용 방지를 위해
    # token은 만료기간이 길기 때문에 유출되면 내가 아닌 제 3자가 계속 엑세스토큰을 발급받을 수 있기 때문
    # 서버에서 db와 비교하는 식으로 보안 강화한 것

    # 사용자 로그인 -> 새 refresh_token 발급 -> DB에 저장
    # 액세스 토큰이 만료되면 사용자가 refresh_token 전송
    # 서버에서 db 확인하여 일치하는지 확인 -> 일치하면 새 액세스 토큰 발급 / 일치하지 않으면 거부
    @staticmethod
    async def update_refresh_token_by_id(db:AsyncSession, user_id: int, refresh_token: str):
        db_user = await db.get(User, user_id)
        if db_user:
            db_user.refresh_token = refresh_token
            await db.flush()
        return db_user