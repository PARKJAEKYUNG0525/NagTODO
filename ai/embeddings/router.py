from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
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


class EmbeddingPatchRequest(BaseModel):
    completed: bool | None = None
    category: str | None = None

    @field_validator("category")
    @classmethod
    def not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("빈 문자열은 허용되지 않습니다")
        return v


def _encode(model: EmbeddingModel, text: str) -> np.ndarray:
    try:
        return model.encode_passage(text)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


def _save(store: EmbeddingStore) -> None:
    try:
        store.save()
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"디스크 저장 실패: {e}")


@router.post("/ai/embeddings/reload")
def reload_embeddings(
    store: EmbeddingStore = Depends(get_embedding_store),
):
    """디스크의 최신 index.faiss + metadata.json을 in-memory 스토어로 다시 로드."""
    store.load()
    return {"reloaded": True, "total": store._index.ntotal}


@router.post("/ai/embeddings/clear")
def clear_embeddings(
    store: EmbeddingStore = Depends(get_embedding_store),
):
    store.clear()
    _save(store)
    return {"cleared": True}


@router.post("/ai/embeddings/todo")
def add_todo_embedding(
    req: EmbeddingCreateRequest,
    model: EmbeddingModel = Depends(get_embedding_model),
    store: EmbeddingStore = Depends(get_embedding_store),
):
    vec = _encode(model, req.text)
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
    _save(store)
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
    _save(store)
    return {"todo_id": todo_id, "deleted": True}


@router.patch("/ai/embeddings/todo/{todo_id}")
def patch_todo_embedding(
    todo_id: str,
    req: EmbeddingPatchRequest,
    store: EmbeddingStore = Depends(get_embedding_store),
):
    fields = req.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=422, detail="변경할 필드가 없습니다")
    try:
        store.patch_meta(todo_id, fields)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    _save(store)
    return {"todo_id": todo_id, "patched": True}


@router.put("/ai/embeddings/todo/{todo_id}")
def update_todo_embedding(
    todo_id: str,
    req: EmbeddingUpdateRequest,
    model: EmbeddingModel = Depends(get_embedding_model),
    store: EmbeddingStore = Depends(get_embedding_store),
):
    vec = _encode(model, req.text)
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
    _save(store)
    return {"todo_id": todo_id, "updated": True}
