"""
간섭 파이프라인 시각 확인용 HTTP 데모 스크립트.

FastAPI 서버에 실제 HTTP 요청을 보내 4가지 피드백 분기를 모두 눈으로 확인한다.

피드백 분기 구조:
  ┌─ 개인 todo < MIN_PERSONAL_TODOS(15)일 때 router early return
  │   1. 빈 스토어, user_A  → 전체 성공률 집계 불가 + 필요 개수 안내
  │   2. new_user           → 전체 성공률 안내 + 필요 개수 안내
  └─ 개인 todo >= 15일 때 generate_feedback 호출
      3. user_B (73%)       → 비꼬기 메시지 (personal_rate >= 30%)
      4. user_A (13%)       → LLM 잔소리 호출 (personal_rate < 30%)
"""
import sys

import httpx

_SEP = "=" * 60
_NEW_TODO = "스위치온 다이어트 1일차"


def _base_url() -> str:
    return sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"


def _seed(client: httpx.Client) -> None:
    res = client.post("/ai/demo/seed", timeout=120)  # 임베딩 인코딩 시간 고려
    res.raise_for_status()
    print(f"  seed 완료: {res.json()}")


def _reset(client: httpx.Client) -> None:
    res = client.post("/ai/demo/reset")
    res.raise_for_status()


def _interference(client: httpx.Client, user_id: str) -> dict:
    res = client.post(
        "/ai/interference",
        json={"todo_text": _NEW_TODO, "category": "health", "user_id": user_id},
        timeout=120,  # LLM 응답 대기
    )
    res.raise_for_status()
    return res.json()


def _print_result(label: str, user_id: str, data: dict) -> None:
    pr = f"{data['personal_rate']:.1f}%" if data["personal_rate"] is not None else "없음"
    gr = f"{data['global_rate']:.1f}%" if data["global_rate"] is not None else "없음"

    print(f"\n{_SEP}")
    print(f"  {label}")
    print(_SEP)
    print(f"  새 TODO      : {_NEW_TODO}  (user_id: {user_id})")
    print(f"  유사 개수    : {data['similar_count']}")
    print(f"  전체 성공률  : {gr}")
    print(f"  개인 성공률  : {pr}")
    if data["similar_failures"]:
        print(f"  유사 사례    : {data['similar_failures'][:5]}")
    print(f"\n  ▶ 피드백: {data['feedback']}")
    print(_SEP)


def main() -> None:
    base = _base_url()
    print(f"\n서버: {base}")

    with httpx.Client(base_url=base) as client:

        # ── 시나리오 1: 빈 스토어 (early return) ─────────────────
        _reset(client)
        data = _interference(client, "user_A")
        _print_result("시나리오 1 | 빈 스토어 → 전체 성공률 집계 불가 안내 [early return]", "user_A", data)

        # ── 데이터 로드 (시나리오 2~4 공통) ──────────────────────
        print("\n  [mock 데이터 스토어에 적재 중...]")
        _seed(client)

        # ── 시나리오 2: new_user — 개인 todo 없음 (early return) ──
        data = _interference(client, "new_user")
        _print_result("시나리오 2 | 개인 todo 없음 → 전체 성공률 안내 [early return]", "new_user", data)

        # ── 시나리오 3: user_B — 개인 성공률 30% 이상 (generate_feedback) ─
        data = _interference(client, "user_B")
        _print_result("시나리오 3 | 개인 성공률 30% 이상 → 잔소리 X [generate_feedback]", "user_B", data)

        # ── 시나리오 4: user_A — 개인 성공률 30% 미만 → LLM 잔소리 ────
        print("\n  [Ollama LLM 호출 중... 잠시 대기]")
        data = _interference(client, "user_A")
        _print_result("시나리오 4 | 개인 성공률 30% 미만 → LLM 잔소리 [generate_feedback → LLM]", "user_A", data)


if __name__ == "__main__":
    main()
