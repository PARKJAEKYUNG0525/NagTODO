'''
쿼리 벡터 생성 후 EmbeddingStore에서 유사 task top-k 검색

Args:
    todo_text: 검색 기준 todo 텍스트
    model: 쿼리 벡터 생성에 사용할 임베딩 모델
    store: 유사도 검색 대상 벡터 스토어

Returns:
    유사 task 메타데이터 리스트 (최대 TOP_K_SIMILAR개)
'''

from __future__ import annotations

from typing import TYPE_CHECKING

from ai.core.config import settings

if TYPE_CHECKING:
    from ai.embeddings.model import EmbeddingModel
    from ai.embeddings.store import EmbeddingStore

def retrieve_similar(
    todo_text: str,
    model: EmbeddingModel,
    store: EmbeddingStore,
) -> list[dict]:

    query_vec = model.encode(todo_text)
    return store.search(query_vec, top_k=settings.TOP_K_SIMILAR)
