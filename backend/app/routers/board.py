from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme.boards import BoardRead, BoardCreate
from app.db.database import get_db
from app.services import BoardService
from app.core.auth import get_user_id

router=APIRouter(prefix="/boards", tags=["Board"])

@router.get("", response_model=list[BoardRead])
async def list_boards(db:AsyncSession=Depends(get_db)):
    return await BoardService.get_all(db)

@router.post("", response_model=BoardRead, status_code=status.HTTP_201_CREATED)
async def create_board(
        board_data:BoardCreate,
        user_id:int=Depends(get_user_id),
        db:AsyncSession=Depends(get_db)):

    return await BoardService.create(db, user_id, board_data)