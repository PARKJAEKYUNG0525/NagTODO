"""
데모 전용 라우터 — DEMO_MODE=1 환경변수 설정 시에만 main.py에서 마운트됨.
스토어에 mock 데이터를 심거나 초기화하는 엔드포인트를 제공한다.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from ai.core.dependencies import get_embedding_model, get_embedding_store

if TYPE_CHECKING:
    from ai.embeddings.model import EmbeddingModel
    from ai.embeddings.store import EmbeddingStore

router = APIRouter(prefix="/ai/demo", tags=["demo"])

# user_id, category, text, completed 포함
# user_A : 건강 실패 패턴  → personal_rate 약 13%  (LLM 잔소리 시나리오)
# user_B : 건강 성공 패턴  → personal_rate 약 73%  (템플릿 시나리오)
# other  : 전체 성공률 낮음 → global_rate 기여
# (new_user 는 데이터 없음  → 고정 문자열 / 개인 데이터 없음 시나리오)
_MOCK_DATA: list[dict] = [
    # ── user_A: 건강 (2/15 완료 ≈ 13%) ──────────────────────────
    {"user_id": "user_A", "category": "health", "text": "러닝 30분",              "completed": True},
    {"user_id": "user_A", "category": "health", "text": "스쿼트 50개",            "completed": False},
    {"user_id": "user_A", "category": "health", "text": "스트레칭 10분",          "completed": False},
    {"user_id": "user_A", "category": "health", "text": "물 2리터 마시기",        "completed": False},
    {"user_id": "user_A", "category": "health", "text": "11시 전에 잠자리 들기",  "completed": False},
    {"user_id": "user_A", "category": "health", "text": "점심 후 10분 걷기",      "completed": True},
    {"user_id": "user_A", "category": "health", "text": "계단으로 올라가기",      "completed": False},
    {"user_id": "user_A", "category": "health", "text": "과자 대신 과일 먹기",    "completed": False},
    {"user_id": "user_A", "category": "health", "text": "카페인 오후 2시 이후 끊기", "completed": False},
    {"user_id": "user_A", "category": "health", "text": "20분마다 먼 곳 보기",   "completed": False},
    {"user_id": "user_A", "category": "health", "text": "헬스장 등록하기",        "completed": False},
    {"user_id": "user_A", "category": "health", "text": "저녁 과식 안 하기",      "completed": False},
    {"user_id": "user_A", "category": "health", "text": "체중 기록하기",          "completed": False},
    {"user_id": "user_A", "category": "health", "text": "비타민 챙겨 먹기",      "completed": False},
    {"user_id": "user_A", "category": "health", "text": "폼롤러로 근막 풀기",    "completed": False},
    # ── user_A: 공부 (3/10 완료 ≈ 30%) ──────────────────────────
    {"user_id": "user_A", "category": "study",  "text": "영어 단어 20개 외우기",  "completed": True},
    {"user_id": "user_A", "category": "study",  "text": "인강 1강 듣기",          "completed": False},
    {"user_id": "user_A", "category": "study",  "text": "알고리즘 문제 1개 풀기", "completed": True},
    {"user_id": "user_A", "category": "study",  "text": "독서 30분",              "completed": False},
    {"user_id": "user_A", "category": "study",  "text": "CS 개념 하나 정리",      "completed": True},
    {"user_id": "user_A", "category": "study",  "text": "기술 블로그 읽기",       "completed": False},
    {"user_id": "user_A", "category": "study",  "text": "오픈소스 코드 읽기",     "completed": False},
    {"user_id": "user_A", "category": "study",  "text": "TED 강연 1편 듣기",      "completed": False},
    {"user_id": "user_A", "category": "study",  "text": "자격증 문제 10문제",     "completed": False},
    {"user_id": "user_A", "category": "study",  "text": "깃허브 잔디 1칸 채우기", "completed": False},
    # ── user_A: 업무 (4/10 완료 = 40%) ──────────────────────────
    {"user_id": "user_A", "category": "work",   "text": "받은 메일 정리하기",     "completed": True},
    {"user_id": "user_A", "category": "work",   "text": "코드 리뷰 완료하기",     "completed": True},
    {"user_id": "user_A", "category": "work",   "text": "회의록 작성하기",        "completed": False},
    {"user_id": "user_A", "category": "work",   "text": "할 일 우선순위 정리",    "completed": True},
    {"user_id": "user_A", "category": "work",   "text": "노션 페이지 업데이트",   "completed": False},
    {"user_id": "user_A", "category": "work",   "text": "PR 설명 꼼꼼히 작성",    "completed": True},
    {"user_id": "user_A", "category": "work",   "text": "테스트 코드 1개 추가",   "completed": False},
    {"user_id": "user_A", "category": "work",   "text": "티켓 닫기",              "completed": False},
    {"user_id": "user_A", "category": "work",   "text": "내일 일정 미리 확인",    "completed": False},
    {"user_id": "user_A", "category": "work",   "text": "작업 전 요구사항 다시 읽기", "completed": False},

    # ── user_B: 건강 (11/15 완료 ≈ 73%) ─────────────────────────
    {"user_id": "user_B", "category": "health", "text": "러닝 30분",              "completed": True},
    {"user_id": "user_B", "category": "health", "text": "스쿼트 50개",            "completed": True},
    {"user_id": "user_B", "category": "health", "text": "스트레칭 10분",          "completed": True},
    {"user_id": "user_B", "category": "health", "text": "물 2리터 마시기",        "completed": True},
    {"user_id": "user_B", "category": "health", "text": "11시 전에 잠자리 들기",  "completed": True},
    {"user_id": "user_B", "category": "health", "text": "점심 후 10분 걷기",      "completed": True},
    {"user_id": "user_B", "category": "health", "text": "계단으로 올라가기",      "completed": True},
    {"user_id": "user_B", "category": "health", "text": "과자 대신 과일 먹기",    "completed": True},
    {"user_id": "user_B", "category": "health", "text": "카페인 오후 2시 이후 끊기", "completed": True},
    {"user_id": "user_B", "category": "health", "text": "20분마다 먼 곳 보기",   "completed": True},
    {"user_id": "user_B", "category": "health", "text": "헬스장 등록하기",        "completed": True},
    {"user_id": "user_B", "category": "health", "text": "저녁 과식 안 하기",      "completed": False},
    {"user_id": "user_B", "category": "health", "text": "체중 기록하기",          "completed": False},
    {"user_id": "user_B", "category": "health", "text": "비타민 챙겨 먹기",      "completed": False},
    {"user_id": "user_B", "category": "health", "text": "폼롤러로 근막 풀기",    "completed": False},

    # ── other: 건강 (3/10 완료 = 30%) — global_rate 낮춤 ─────────
    {"user_id": "other",  "category": "health", "text": "러닝 30분",              "completed": True},
    {"user_id": "other",  "category": "health", "text": "스쿼트 50개",            "completed": False},
    {"user_id": "other",  "category": "health", "text": "스트레칭 10분",          "completed": True},
    {"user_id": "other",  "category": "health", "text": "물 2리터 마시기",        "completed": False},
    {"user_id": "other",  "category": "health", "text": "11시 전에 잠자리 들기",  "completed": False},
    {"user_id": "other",  "category": "health", "text": "점심 후 10분 걷기",      "completed": True},
    {"user_id": "other",  "category": "health", "text": "계단으로 올라가기",      "completed": False},
    {"user_id": "other",  "category": "health", "text": "과자 대신 과일 먹기",    "completed": False},
    {"user_id": "other",  "category": "health", "text": "카페인 오후 2시 이후 끊기", "completed": False},
    {"user_id": "other",  "category": "health", "text": "20분마다 먼 곳 보기",   "completed": False},
]


@router.post("/seed")
def seed(
    model: EmbeddingModel = Depends(get_embedding_model),
    store: EmbeddingStore = Depends(get_embedding_store),
) -> dict:
    """_MOCK_DATA 전체를 스토어에 추가한다. 이미 존재하는 항목은 건너뜀."""
    added = 0
    for i, item in enumerate(_MOCK_DATA):
        todo_id = f"demo_{item['user_id']}_{i}"
        vec = model.encode_passage(item["text"])
        try:
            store.add(
                todo_id=todo_id,
                vec=vec,
                meta={
                    "user_id":   item["user_id"],
                    "category":  item["category"],
                    "text":      item["text"],
                    "completed": item["completed"],
                },
            )
            added += 1
        except ValueError:
            pass  # 이미 존재하는 항목 건너뜀
    return {"seeded": added}


@router.post("/reset")
def reset(store: EmbeddingStore = Depends(get_embedding_store)) -> dict:
    """스토어의 모든 데이터를 삭제한다."""
    store.clear()
    return {"status": "cleared"}
