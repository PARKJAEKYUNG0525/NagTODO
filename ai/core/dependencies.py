from functools import lru_cache

from ai.embeddings.model import EmbeddingModel
from ai.embeddings.store import EmbeddingStore

'''무거운 객체(임베딩 모델, 벡터 스토어)를 앱 전체에서 딱 한 번만 생성하고
필요한 곳(FastAPI 엔드포인트 등)에 자동으로 주입해주는 연결 허브'''

# @lru_cache : 싱글턴 보장
# 첫 호출 시에만 실행하고 이후엔 캐시된 인스턴스를 반환 -> 요청마다 객체 새로 생성 X

@lru_cache(maxsize=1)
def get_embedding_model() -> EmbeddingModel:
    return EmbeddingModel()


@lru_cache(maxsize=1)
def get_embedding_store() -> EmbeddingStore:
    """디스크에서 인덱스를 로드하고 soft delete 항목을 정리한 스토어를 반환."""
    store = EmbeddingStore()
    store.load()
    store.rebuild()
    return store
