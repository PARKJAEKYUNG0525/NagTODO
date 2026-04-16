from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai.embeddings.model import EmbeddingModel
    from ai.embeddings.store import EmbeddingStore
    from ai.llm.ollama_client import OllamaClient

'''무거운 객체(임베딩 모델, 벡터 스토어)를 앱 전체에서 딱 한 번만 생성하고
필요한 곳(FastAPI 엔드포인트 등)에 자동으로 주입해주는 연결 허브.

모듈 레벨 임포트 대신 함수 내부에서 지연 임포트(lazy import)하여
테스트 환경에서 sentence_transformers 등 무거운 라이브러리 로드를 방지.'''

# @lru_cache : 싱글턴 보장
# 첫 호출 시에만 실행하고 이후엔 캐시된 인스턴스를 반환 -> 요청마다 객체 새로 생성 X

@lru_cache(maxsize=1)
def get_embedding_model() -> EmbeddingModel:
    from ai.embeddings.model import EmbeddingModel
    return EmbeddingModel()


@lru_cache(maxsize=1)
def get_ollama_client() -> OllamaClient:
    from ai.llm.ollama_client import OllamaClient
    return OllamaClient()


@lru_cache(maxsize=1)
def get_embedding_store() -> EmbeddingStore:
    """디스크에서 인덱스를 로드하고 soft delete 항목을 정리한 스토어를 반환."""
    from ai.embeddings.store import EmbeddingStore
    store = EmbeddingStore()
    store.load()
    store.rebuild()
    return store
