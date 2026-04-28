"""
월간 리포트 파이프라인 시각 확인용 HTTP 데모 스크립트.

FastAPI 서버에 실제 HTTP 요청을 보내 3가지 분기를 모두 눈으로 확인한다.

그래프 분기 구조:
  load_logs → _check_task_count
    ├─ task < MIN_MONTHLY_TASKS(30)
    │   1. user_lazy (10개 로그)  → too_few_tasks: 따끔한 한 마디
    └─ task >= 30 → compute_stats → embed_failures → _check_failure_count
        ├─ failed < MIN_MONTHLY_FAIL_TASKS(5)
        │   2. user_perfect (30개, 전부 완료)  → minimal_report: 비꼬기
        └─ failed >= 5
            3. user_A (35개, 26개 실패)  → 풀 파이프라인 (LLM 분석 + 리포트 + 품질 검증)

실행:
  python -m ai.demo.report [서버_URL]
"""
import sys

import httpx

_SEP = "=" * 60

# ── mock 데이터 ────────────────────────────────────────────────────────────────

# 시나리오 3용: user_A 35개 로그 (건강 13% / 공부 30% / 업무 40%)
_LOGS_FULL: list[dict] = [
    # 건강 (2/15 완료 ≈ 13%)
    {"category": "health", "text": "러닝 30분",               "completed": True},
    {"category": "health", "text": "스쿼트 50개",             "completed": False},
    {"category": "health", "text": "스트레칭 10분",           "completed": False},
    {"category": "health", "text": "물 2리터 마시기",         "completed": False},
    {"category": "health", "text": "11시 전에 잠자리 들기",   "completed": False},
    {"category": "health", "text": "점심 후 10분 걷기",       "completed": True},
    {"category": "health", "text": "계단으로 올라가기",       "completed": False},
    {"category": "health", "text": "과자 대신 과일 먹기",     "completed": False},
    {"category": "health", "text": "카페인 오후 2시 이후 끊기", "completed": False},
    {"category": "health", "text": "20분마다 먼 곳 보기",     "completed": False},
    {"category": "health", "text": "헬스장 등록하기",         "completed": False},
    {"category": "health", "text": "저녁 과식 안 하기",       "completed": False},
    {"category": "health", "text": "체중 기록하기",           "completed": False},
    {"category": "health", "text": "비타민 챙겨 먹기",        "completed": False},
    {"category": "health", "text": "폼롤러로 근막 풀기",      "completed": False},
    # 공부 (3/10 완료 = 30%)
    {"category": "study",  "text": "영어 단어 20개 외우기",   "completed": True},
    {"category": "study",  "text": "인강 1강 듣기",           "completed": False},
    {"category": "study",  "text": "알고리즘 문제 1개 풀기",  "completed": True},
    {"category": "study",  "text": "독서 30분",               "completed": False},
    {"category": "study",  "text": "CS 개념 하나 정리",       "completed": True},
    {"category": "study",  "text": "기술 블로그 읽기",        "completed": False},
    {"category": "study",  "text": "오픈소스 코드 읽기",      "completed": False},
    {"category": "study",  "text": "TED 강연 1편 듣기",       "completed": False},
    {"category": "study",  "text": "자격증 문제 10문제",      "completed": False},
    {"category": "study",  "text": "깃허브 잔디 1칸 채우기",  "completed": False},
    # 업무 (4/10 완료 = 40%)
    {"category": "work",   "text": "받은 메일 정리하기",      "completed": True},
    {"category": "work",   "text": "코드 리뷰 완료하기",      "completed": True},
    {"category": "work",   "text": "회의록 작성하기",         "completed": False},
    {"category": "work",   "text": "할 일 우선순위 정리",     "completed": True},
    {"category": "work",   "text": "노션 페이지 업데이트",    "completed": False},
    {"category": "work",   "text": "PR 설명 꼼꼼히 작성",     "completed": True},
    {"category": "work",   "text": "테스트 코드 1개 추가",    "completed": False},
    {"category": "work",   "text": "티켓 닫기",               "completed": False},
    {"category": "work",   "text": "내일 일정 미리 확인",     "completed": False},
    {"category": "work",   "text": "작업 전 요구사항 다시 읽기", "completed": False},
]

# 시나리오 1용: 10개 로그 (task 수 부족)
_LOGS_TOO_FEW = _LOGS_FULL[:10]

# 시나리오 2용: 30개 로그, 전부 완료 (실패 없음)
_LOGS_NO_FAILURES = [
    {**log, "completed": True} for log in _LOGS_FULL[:30]
]


# ── 출력 헬퍼 ─────────────────────────────────────────────────────────────────

def _base_url() -> str:
    return sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8081"


def _run_demo(client: httpx.AsyncClient, user_id: str, logs: list[dict]) -> dict:
    res = client.post(
        "/ai/demo/report",
        json={"user_id": user_id, "logs": logs},
        timeout=300,  # LLM 분석 + 리포트 생성 대기
    )
    res.raise_for_status()
    return res.json()


def _print_result(label: str, user_id: str, log_count: int, data: dict) -> None:
    print(f"\n{_SEP}")
    print(f"  {label}")
    print(_SEP)
    print(f"  user_id      : {user_id}")
    print(f"  로그 수      : {log_count}개")

    stats: dict = data.get("category_stats") or {}
    if stats:
        print("  카테고리별 달성률:")
        for cat, s in stats.items():
            print(f"    {cat:10s}: {s['completed']}/{s['total']} ({s['rate']:.1f}%)")

    clusters = data.get("cluster_count", 0)
    if clusters:
        print(f"  실패 클러스터: {clusters}개")

    quality = data.get("quality_passed")
    if quality is not None:
        q_label = "통과" if quality else f"미달 {data.get('quality_issues', [])}"
        print(f"  품질 검증    : {q_label}")

    report: str = data.get("retrospective_report", "")
    print(f"\n  ▶ 리포트:\n")
    for line in report.splitlines():
        print(f"    {line}")
    print(_SEP)


def main() -> None:
    base = _base_url()
    print(f"\n서버: {base}")

    with httpx.Client(base_url=base) as client:

        # ── 시나리오 1: task 부족 ─────────────────────────────────
        print("\n  [시나리오 1 실행 중...]")
        data = _run_demo(client, "user_lazy", _LOGS_TOO_FEW)
        _print_result(
            f"시나리오 1 | 로그 {len(_LOGS_TOO_FEW)}개 < 30 → too_few_tasks",
            "user_lazy", len(_LOGS_TOO_FEW), data,
        )

        # ── 시나리오 2: 실패 없음 ─────────────────────────────────
        print("\n  [시나리오 2 실행 중...]")
        data = _run_demo(client, "user_perfect", _LOGS_NO_FAILURES)
        _print_result(
            f"시나리오 2 | 로그 {len(_LOGS_NO_FAILURES)}개, 전부 완료 → minimal_report",
            "user_perfect", len(_LOGS_NO_FAILURES), data,
        )

        # ── 시나리오 3: 풀 파이프라인 ────────────────────────────
        print("\n  [시나리오 3 실행 중... LLM 분석 + 리포트 생성 중]")
        data = _run_demo(client, "user_A", _LOGS_FULL)
        _print_result(
            f"시나리오 3 | 로그 {len(_LOGS_FULL)}개, 26개 실패 → 풀 파이프라인",
            "user_A", len(_LOGS_FULL), data,
        )


if __name__ == "__main__":
    main()
