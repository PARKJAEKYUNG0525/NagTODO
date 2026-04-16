import numpy as np
from sentence_transformers import SentenceTransformer

from ai.core.config import settings

'''임베딩 모델(multilingual-e5-small) 로더/추론'''

class EmbeddingModel:
    def __init__(self) -> None:
        # 모델 로드
        self._model = SentenceTransformer(settings.EMBEDDING_MODEL)

    # 검색 쿼리용 인코딩 — e5 모델 규칙에 따라 'query: ' 접두어 사용
    def encode(self, text: str) -> np.ndarray:
        return self._encode_with_prefix("query", text)

    # todo 저장용 인코딩 — e5 모델 규칙에 따라 'passage: ' 접두어 사용
    def encode_passage(self, text: str) -> np.ndarray:
        return self._encode_with_prefix("passage", text)

    def _encode_with_prefix(self, prefix: str, text: str) -> np.ndarray:
        vec = self._model.encode(
            f"{prefix}: {text}",
            normalize_embeddings=True,  # L2 정규화(벡터를 길이 1로) → 내적 = cosine similarity
            convert_to_numpy=True,      # PyTorch tensor가 아닌 numpy 배열로 바로 반환 (FAISS는 numpy 배열과 궁합 좋음)
        ).astype(np.float32)
        return vec