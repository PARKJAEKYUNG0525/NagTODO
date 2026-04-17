from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Board
from app.db.scheme.boards import BoardCreate
from app.db.scheme.users import UserCreate


class BoardCrud:

    """ 전체 게시글 조회 """
    @staticmethod
    async def get_all(db: AsyncSession):
        result = select(Board)
        result2 = await db.execute(result)
        return result2.scalars().all()

    ''' 게시글 생성 '''
    # 작성자 추가해서 게시글 생성
    # { "title":"제목", "description":"내용", "user_id":1 }
    @staticmethod
    async def create(db: AsyncSession, user_id: int,  board_data: BoardCreate) -> Board:
        board_dict = board_data.model_dump()
        # BoardCreate에는 title: str, description: str 밖에 없으니까
        # dict[키 이름] = 데이터 형식으로 새 key-value 쌍 추가
        board_dict["user_id"] = user_id
        new_board = Board(**board_dict)
        db.add(new_board)
        await db.flush()
        return new_board