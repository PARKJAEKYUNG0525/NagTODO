"""
데모 전용 라우터 — DEMO_MODE=1 환경변수 설정 시에만 main.py에서 마운트됨.
스토어에 mock 데이터를 심거나 초기화하는 엔드포인트를 제공한다.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ai.core.dependencies import get_embedding_model, get_embedding_store

if TYPE_CHECKING:
    from ai.embeddings.model import EmbeddingModel
    from ai.embeddings.store import EmbeddingStore

router = APIRouter(prefix="/ai/demo", tags=["demo"])

_MOCK_TEXTS = [
    # 건강
    "러닝 30분",
    "스쿼트 50개",
    "스트레칭 10분",
    "물 2리터 마시기",
    "11시 전에 잠자리 들기",
    # 공부 / 자기계발
    "영어 단어 20개 외우기",
    "기술 블로그 글 읽기",
    "인강 1강 듣기",
    "독서 30분",
    "알고리즘 문제 1개 풀기",
    # 업무 / 생산성
    "받은 메일 정리하기",
    "오늘 할 일 우선순위 정리",
    "코드 리뷰 완료하기",
    "회의록 작성하기",
    "노션 페이지 업데이트",
    # 생활 / 루틴
    "방 청소하기",
    "설거지 바로 하기",
    "지출 가계부 기록",
    "SNS 사용 1시간 이내로",
    "쓰레기 분리수거",
    # 멘탈 / 감정
    "감사 일기 3줄 쓰기",
    "명상 5분",
    "오늘 하루 회고 적기",
]


class SeedRequest(BaseModel):
    user_id: str
    completed_count: int  # 0~10, 앞에서부터 completed_count개를 완료 처리


@router.post("/seed")
def seed(
    req: SeedRequest,
    model: EmbeddingModel = Depends(get_embedding_model),
    store: EmbeddingStore = Depends(get_embedding_store),
) -> dict:
    """mock 운동 관련 태스크를 스토어에 추가한다."""
    added = 0
    for i, text in enumerate(_MOCK_TEXTS):
        todo_id = f"demo_{req.user_id}_{i}"
        # 이미 존재하면 스킵 (중복 실행 방어)
        if any(m["todo_id"] == todo_id and not m["is_deleted"] for m in store._metadata):
            continue
        vec = model.encode_passage(text)
        store.add(
            todo_id=todo_id,
            vec=vec,
            meta={
                "user_id": req.user_id,
                "category": "health",
                "text": text,
                "completed": i < req.completed_count,
            },
        )
        added += 1
    return {"seeded": added, "total_in_store": store._index.ntotal}


@router.post("/reset")
def reset(store: EmbeddingStore = Depends(get_embedding_store)) -> dict:
    """스토어의 모든 데이터를 삭제한다."""
    store.clear()
    return {"status": "cleared"}
