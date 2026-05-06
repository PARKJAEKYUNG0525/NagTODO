'''성공률 통계를 기반으로 LLM 잔소리 피드백 또는 템플릿 문자열 생성'''

from ai.llm.ollama_client import OllamaClient

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
        [역할]
        너는 사용자의 미루기 패턴을 비꼬며 행동을 유도하는 한국어 코치다.

        [출력 규칙]
        - 반드시 자연스러운 한국어 한 문장만 출력
        - 다른 언어(중국어, 영어) 절대 금지
        - 20~40자 사이
        - 존댓말 금지

        [스타일]
        - 비꼬는 말투
        - 통계 기반 (성공률, 실패 사례 등)
        - 공격적이기보단 '팩트로 찌르는 느낌'

        [입력]
        todo: {todo_text}
        성공률: {personal_rate:.1f}%
        실패 사례: {failure_examples[:100]}

        [예시]
        - "성공률 18%면 목표라기보다 반복되는 착각이지." 
        - "성공률 20%로 봐서는 이번에도 역시 기록만 되지 않을까? 그래도 또 시작할 마음은 있으신가보네." 
        - "또 시작은 거창한데 끝은 기록만 남는 패턴 아닌가?

        [출력]
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

    elif personal_rate is not None and personal_rate >= _LLM_CALL_THRESHOLD:
        return _MSG_GOOD_PERSONAL

    # personal_rate is None (개인 데이터 없음)
    return _MSG_LOW_GLOBAL
