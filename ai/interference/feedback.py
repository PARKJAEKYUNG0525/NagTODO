"""Generate feedback text using simple thresholds and LLM fallback."""

from ai.llm.openai_client import OpenAIClient

_LLM_CALL_THRESHOLD = 30.0

_MSG_NO_DATA = "기록이 없는데 이번에도 미룰 거라고? 근거가 뭐야?"
_MSG_GOOD_PERSONAL = "이번엔 해냈네. 근데 얼마나 갈지는 끝까지 찍고 보자."
_MSG_LOW_GLOBAL = "다들 이런 건 꾸준히 적어놓고도 자주 무너진다."


def _build_prompt(todo_text: str, stats: dict) -> str:
    personal_rate = stats["personal_rate"]
    if personal_rate is None:
        raise ValueError("_build_prompt requires personal_rate")

    failures = stats.get("similar_failures", [])
    failure_examples = "\n".join(f"- {f}" for f in failures) if failures else "없음"

    return (
        f"""
[역할]
너는 사용자의 미루기 패턴을 비꼬면서도 행동하게 만드는 냉정한 코치다.

[출력 규칙]
- 반드시 자연스러운 한국어 한 문장만 출력
- 다른 언어(중국어/영어) 금지
- 20~40자 사이
- 존댓말 금지

[스타일]
- 비꼬는 말투
- 통계 기반 (성공률, 실패 사례 활용)
- 공격적이기보다 팩트로 찌르는 톤

[입력]
todo: {todo_text}
성공률: {personal_rate:.1f}%
실패 사례:
{failure_examples[:100]}

[예시]
- "성공률 18%면 목표가 아니라 반복되는 착각이지."
- "성공률 20%로 꾸며서 또 미룰 거면 기록은 왜 쓰냐."
- "시작은 거창한데 끝은 기록만 남는 패턴 아닌가?"

[출력]
"""
    )


async def generate_feedback(
    todo_text: str,
    stats: dict,
    llm_client: OpenAIClient,
) -> str:
    if stats["similar_count"] == 0:
        return _MSG_NO_DATA

    personal_rate = stats["personal_rate"]

    if personal_rate is not None and personal_rate < _LLM_CALL_THRESHOLD:
        prompt = _build_prompt(todo_text, stats)
        return await llm_client.generate(prompt)

    if personal_rate is not None and personal_rate >= _LLM_CALL_THRESHOLD:
        return _MSG_GOOD_PERSONAL

    return _MSG_LOW_GLOBAL
