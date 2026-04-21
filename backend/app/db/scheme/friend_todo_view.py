from pydantic import BaseModel, Field
from typing import Annotated

class FriendTodoViewBase(BaseModel):
    user_id: Annotated[str, Field(max_length=100)]
    todo_id: Annotated[str, Field(max_length=100)]

class FriendTodoViewCreate(FriendTodoViewBase):
    pass

class FriendTodoViewUpdate(FriendTodoViewBase):
    pass

class FriendTodoViewInDB(FriendTodoViewBase):
    friend_todo_view_id: int

    class Config:
        from_attributes = True

class FriendTodoViewRead(FriendTodoViewInDB):
    pass