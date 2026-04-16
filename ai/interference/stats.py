'''
유사 task 목록에서 전체/개인 성공률과 실패 task 목록 계산

Args:
    similar_tasks: EmbeddingStore.search() 결과 (todo_id, user_id, text, completed 포함)
    user_id: 개인 성공률 계산 기준 사용자 ID

Returns:
    global_rate: 전체 성공률(%), 데이터 없으면 None
    personal_rate: 개인 성공률(%), 개인 데이터 없으면 None
    similar_count: 유사 task 총 수
    personal_count: 개인 task 수
    similar_failures: 실패 task 텍스트 목록 (개인 실패 우선, 최대 10개)
'''

# 반환할 유사 실패 todo 최대 개수 (개인 실패 우선)
_MAX_FAILURES = 10

def compute_stats(similar_tasks: list[dict], user_id: str) -> dict:

    if not similar_tasks:
        return {
            "global_rate": None,
            "personal_rate": None,
            "similar_count": 0,
            "personal_count": 0,
            "similar_failures": [],
        }

    total = len(similar_tasks)
    completed_count = sum(1 for t in similar_tasks if t.get("completed", False))
    global_rate = completed_count / total * 100

    personal = [t for t in similar_tasks if t.get("user_id") == user_id]
    personal_count = len(personal)

    if personal:
        personal_completed = sum(1 for t in personal if t.get("completed", False))
        personal_rate: float | None = personal_completed / personal_count * 100
    else:
        personal_rate = None

    # 개인 실패 우선, 나머지 전체 실패로 채워 최대 10개
    personal_failures = [t["text"] for t in personal if not t.get("completed", False)]
    other_failures = [
        t["text"]
        for t in similar_tasks
        if not t.get("completed", False) and t.get("user_id") != user_id
    ]
    similar_failures = (personal_failures + other_failures)[:_MAX_FAILURES]

    return {
        "global_rate": global_rate,
        "personal_rate": personal_rate,
        "similar_count": total,
        "personal_count": personal_count,
        "similar_failures": similar_failures,
    }
