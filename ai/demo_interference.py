"""
간섭 파이프라인 시각 확인용 HTTP 데모 스크립트.

FastAPI 서버에 실제 HTTP 요청을 보내 4가지 피드백 분기를 모두 눈으로 확인한다:
  1. 빈 스토어              → 고정 문자열 (유사 데이터 없음)
  2. new_user — 개인 데이터 없음  → 템플릿
  3. user_B  — 개인 성공률 73%   → 템플릿 (잘하고 있음)
  4. user_A  — 개인 성공률 13%   → LLM 잔소리 호출
"""
import sys

import httpx

_SEP = "=" * 60
_NEW_TODO = "러닝 30분"


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
        print(f"  실패 사례    : {data['similar_failures'][:3]}")
    print(f"\n  ▶ 피드백: {data['feedback']}")
    print(_SEP)


def main() -> None:
    base = _base_url()
    print(f"\n서버: {base}")

    with httpx.Client(base_url=base) as client:

        # ── 시나리오 1: 빈 스토어 ────────────────────────────────
        _reset(client)
        data = _interference(client, "user_A")
        _print_result("시나리오 1 | 빈 스토어 → 고정 문자열", "user_A", data)

        # ── 데이터 로드 (시나리오 2~4 공통) ──────────────────────
        print("\n  [mock 데이터 스토어에 적재 중...]")
        _seed(client)

        # ── 시나리오 2: new_user — 개인 데이터 없음 ───────────────
        data = _interference(client, "new_user")
        _print_result("시나리오 2 | 개인 데이터 없음 → 템플릿", "new_user", data)

        # ── 시나리오 3: user_B — 개인 성공률 73% ─────────────────
        data = _interference(client, "user_B")
        _print_result("시나리오 3 | 개인 성공률 73% → 템플릿 (잘함)", "user_B", data)

        # ── 시나리오 4: user_A — 개인 성공률 13% → LLM 잔소리 ────
        print("\n  [Ollama LLM 호출 중... 잠시 대기]")
        data = _interference(client, "user_A")
        _print_result("시나리오 4 | 개인 성공률 13% → LLM 잔소리", "user_A", data)


if __name__ == "__main__":
    main()
