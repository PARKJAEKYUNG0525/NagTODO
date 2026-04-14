from functools import lru_cache

from ai.embeddings.model import EmbeddingModel

'''무거운 객체(임베딩 모델 등)를 앱 전체에서 딱 한 번만 생성하고 필요한 곳(FastAPI 엔드포인트 등)에 자동으로 주입해주는 연결 허브'''

# @lru_cache : 싱글턴 보장
# 첫 호출 시에만 실행하고 이후엔 캐시된 인스턴스를 반환 -> 요청마다 모델 새로 로드 X

# FastAPI가 요청을 받을 때 get_embedding_model()을 자동으로 호출해서 인자로 넣어줌
# 라우터 함수 안에서 직접 import하거나 전역 변수로 꺼낼 필요 X
@lru_cache(maxsize=1)
def get_embedding_model() -> EmbeddingModel:
    return EmbeddingModel()
