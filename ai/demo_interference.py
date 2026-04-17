"""
간섭 파이프라인 시각 확인용 HTTP 데모 스크립트.

FastAPI 서버에 실제 HTTP 요청을 보내 4가지 피드백 분기를 모두 눈으로 확인한다:
  1. 빈 스토어              → 고정 문자열 (유사 데이터 없음)
  2. 타인 데이터 + 낮은 전체 성공률 → 템플릿 (개인 데이터 없음)
  3. 개인 성공률 >= 30%     → 템플릿 (잘하고 있음)
  4. 개인 성공률 < 30%      → LLM 잔소리 호출
"""
import sys

import httpx

_SEP = "=" * 60
_NEW_TODO = "러닝 30분"
_MY_USER = "user_A"
_OTHER_USER = "other_user"


def _base_url() -> str:
    return sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"


def _seed(client: httpx.Client, user_id: str, completed_count: int) -> None:
    res = client.post("/ai/demo/seed", json={"user_id": user_id, "completed_count": completed_count})
    res.raise_for_status()


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


def _print_result(label: str, data: dict) -> None:
    pr = f"{data['personal_rate']:.1f}%" if data["personal_rate"] is not None else "없음"
    gr = f"{data['global_rate']:.1f}%" if data["global_rate"] is not None else "없음"

    print(f"\n{_SEP}")
    print(f"  {label}")
    print(_SEP)
    print(f"  새 TODO      : {_NEW_TODO}")
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
        data = _interference(client, _MY_USER)
        _print_result("시나리오 1 | 빈 스토어 → 고정 문자열", data)

        # ── 시나리오 2: 타인 데이터 전체 성공률 20%, 개인 데이터 없음 ──
        _reset(client)
        _seed(client, _OTHER_USER, completed_count=2)   # 10개 중 2개 완료 = 20%
        data = _interference(client, _MY_USER)          # user_A 데이터 없음
        _print_result("시나리오 2 | 개인 데이터 없음 + 전체 20% → 템플릿", data)

        # ── 시나리오 3: 개인 성공률 70% ──────────────────────────
        _reset(client)
        _seed(client, _MY_USER, completed_count=7)      # 10개 중 7개 완료 = 70%
        data = _interference(client, _MY_USER)
        _print_result("시나리오 3 | 개인 성공률 70% → 템플릿 (잘함)", data)

        # ── 시나리오 4: 개인 성공률 10% → LLM 잔소리 ──────────────
        _reset(client)
        _seed(client, _MY_USER, completed_count=1)      # 10개 중 1개 완료 = 10%
        print("\n  [Ollama LLM 호출 중... 잠시 대기]")
        data = _interference(client, _MY_USER)
        _print_result("시나리오 4 | 개인 성공률 10% → LLM 잔소리", data)


if __name__ == "__main__":
    main()
