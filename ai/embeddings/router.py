from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

from ai.core.dependencies import get_embedding_model, get_embedding_store

if TYPE_CHECKING:
    from ai.embeddings.model import EmbeddingModel
    from ai.embeddings.store import EmbeddingStore

router = APIRouter()


class EmbeddingCreateRequest(BaseModel):
    todo_id: str
    user_id: str
    category: str
    text: str
    completed: bool

    @field_validator("todo_id", "user_id", "category", "text")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("빈 문자열은 허용되지 않습니다")
        return v


class EmbeddingUpdateRequest(BaseModel):
    user_id: str
    category: str
    text: str
    completed: bool

    @field_validator("user_id", "category", "text")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("빈 문자열은 허용되지 않습니다")
        return v


@router.post("/ai/embeddings/todo")
def add_todo_embedding(
    req: EmbeddingCreateRequest,
    model: EmbeddingModel = Depends(get_embedding_model),
    store: EmbeddingStore = Depends(get_embedding_store),
):
    vec = model.encode_passage(req.text)
    meta = {
        "user_id": req.user_id,
        "category": req.category,
        "text": req.text,
        "completed": req.completed,
    }
    try:
        store.add(req.todo_id, vec, meta)
    except ValueError as e:
        if "이미 존재" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))
    store.save()
    return {"todo_id": req.todo_id, "indexed": True}


@router.delete("/ai/embeddings/todo/{todo_id}")
def delete_todo_embedding(
    todo_id: str,
    store: EmbeddingStore = Depends(get_embedding_store),
):
    try:
        store.delete(todo_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    store.save()
    return {"todo_id": todo_id, "deleted": True}


@router.put("/ai/embeddings/todo/{todo_id}")
def update_todo_embedding(
    todo_id: str,
    req: EmbeddingUpdateRequest,
    model: EmbeddingModel = Depends(get_embedding_model),
    store: EmbeddingStore = Depends(get_embedding_store),
):
    vec = model.encode_passage(req.text)
    meta = {
        "user_id": req.user_id,
        "category": req.category,
        "text": req.text,
        "completed": req.completed,
    }
    try:
        store.update(todo_id, vec, meta)
    except ValueError as e:
        if "존재하지 않음" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))
    store.save()
    return {"todo_id": todo_id, "updated": True}
