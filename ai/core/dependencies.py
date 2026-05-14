from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai.embeddings.model import EmbeddingModel
    from ai.embeddings.store import EmbeddingStore
    from ai.llm.openai_client import OpenAIClient

'''臾닿굅??媛앹껜(?꾨쿋??紐⑤뜽, 踰≫꽣 ?ㅽ넗??瑜????꾩껜?먯꽌 ????踰덈쭔 ?앹꽦?섍퀬
?꾩슂??怨?FastAPI ?붾뱶?ъ씤???????먮룞?쇰줈 二쇱엯?댁＜???곌껐 ?덈툕.

紐⑤뱢 ?덈꺼 ?꾪룷??????⑥닔 ?대??먯꽌 吏???꾪룷??lazy import)?섏뿬
?뚯뒪???섍꼍?먯꽌 sentence_transformers ??臾닿굅???쇱씠釉뚮윭由?濡쒕뱶瑜?諛⑹?.'''

# @lru_cache : ?깃???蹂댁옣
# 泥??몄텧 ?쒖뿉留??ㅽ뻾?섍퀬 ?댄썑??罹먯떆???몄뒪?댁뒪瑜?諛섑솚 -> ?붿껌留덈떎 媛앹껜 ?덈줈 ?앹꽦 X

@lru_cache(maxsize=1)
def get_embedding_model() -> EmbeddingModel:
    from ai.embeddings.model import EmbeddingModel
    return EmbeddingModel()


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAIClient:
    from ai.llm.openai_client import OpenAIClient
    return OpenAIClient()


def get_ollama_client() -> OpenAIClient:
    """Backward-compatible alias. Kept to reduce migration risk."""
    return get_openai_client()


@lru_cache(maxsize=1)
def get_embedding_store() -> EmbeddingStore:
    """?붿뒪?ъ뿉???몃뜳?ㅻ? 濡쒕뱶?섍퀬 soft delete ??ぉ???뺣━???ㅽ넗?대? 諛섑솚."""
    from ai.embeddings.store import EmbeddingStore
    store = EmbeddingStore()
    store.load()
    store.rebuild()
    return store
