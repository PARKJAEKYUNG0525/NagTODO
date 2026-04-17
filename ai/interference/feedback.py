from ai.llm.ollama_client import OllamaClient

'''성공률 통계를 기반으로 LLM 잔소리 피드백 또는 템플릿 문자열 생성'''

# LLM 호출 임계값
_LLM_CALL_THRESHOLD = 30.0

# 고정 문자열 (유사 데이터 없을 때)
_MSG_NO_DATA = "기록도 없는데 이번엔 잘 할 거라는 근거가 뭐야?"

# 성공률 양호 템플릿 (personal_rate >= 30%)
_MSG_GOOD_PERSONAL = (
    "이번엔 잘했네. 근데 얼마나 갈지는 두고봐야 알겠지."
)

# 개인 데이터 없음 + 낮은 전체 성공률 템플릿
_MSG_LOW_GLOBAL = (
    "다들 이런 건 거창하게 적어놓고 흐지부지 끝내더라."
)


def _build_prompt(todo_text: str, stats: dict) -> str:
    '''LLM에 전달할 한국어 잔소리 프롬프트 생성 — personal_rate가 None이면 호출 불가'''
    personal_rate = stats["personal_rate"]
    if personal_rate is None:
        raise ValueError("_build_prompt은 personal_rate가 존재할 때만 호출해야 함")
    failures = stats.get("similar_failures", [])
    failure_examples = "\n".join(f"- {f}" for f in failures) if failures else "없음"

    return (
        f"""
        당신은 사용자의 미루기 습관을 정확히 기억하고 비꼬아 행동을 유도하는 냉정한 생산성 코치다.
        반복된 실패 패턴을 근거로 사용자의 자기합리화를 짚어 불편함을 유도하라.
        반드시 한국어로 출력해야 한다.

        새 todo : '{todo_text}'
        과거 비슷한 task의 개인 성공률: {personal_rate:.1f}%
        과거 실패 사례:
        {failure_examples}

        위 데이터를 바탕으로 사용자가 뜨끔하고 불편함을 느껴 바로 행동하고 싶어지도록,
        비꼬는 말투의 한국어 피드백을 1~2문장으로 작성하라.

        예시:
        - "성공률 18%면 목표라기보다 반복되는 착각이지."
        - "또 시작은 거창한데 끝은 기록만 남는 패턴 아닌가?"
        - "실패 사례 내용이 전부 비슷한데 아직도 이번만 다를 거라고 믿는 거야?"
        - "동일 실패 기록이 이렇게 쌓였는데도 아직 계획 세우는 단계가 의미 있다고 믿는 거야?"
        """
    )

'''
LLM 호출 분기:
- 유사 데이터 없음            → 고정 문자열
- personal_rate >= 30%      → 템플릿 (잘하고 있음)
- personal_rate 없음        → 템플릿 (전체 성공률 낮음 안내)
- personal_rate < 30%       → LLM 호출 (잔소리)
'''
async def generate_feedback(
    todo_text: str,
    stats: dict,
    ollama: OllamaClient,
) -> str:

    if stats["similar_count"] == 0:
        return _MSG_NO_DATA

    personal_rate = stats["personal_rate"]

    # LLM 호출 조건: personal_rate가 존재하고 30% 미만일 때만
    if personal_rate is not None and personal_rate < _LLM_CALL_THRESHOLD:
        prompt = _build_prompt(todo_text, stats)
        return await ollama.generate(prompt)

    if personal_rate is not None and personal_rate >= _LLM_CALL_THRESHOLD:
        return _MSG_GOOD_PERSONAL

    # personal_rate is None (개인 데이터 없음)
    return _MSG_LOW_GLOBAL
