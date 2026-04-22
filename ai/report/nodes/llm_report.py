import json

from ai.core.dependencies import get_ollama_client


async def llm_report(state: dict) -> dict:
    """pattern_analysis와 category_stats를 바탕으로 월간 회고 리포트를 생성한다."""
    pattern_analysis: str = state["pattern_analysis"]
    category_stats: dict = state["category_stats"]
    retry_count: int = state.get("retry_count", 0)
    quality_issues: list[str] = state.get("quality_issues", [])

    stats_json = json.dumps(category_stats, ensure_ascii=False, indent=2)

    base_prompt = (
        "다음 정보를 바탕으로 월간 회고 리포트를 작성해주세요.\n\n"
        f"[카테고리별 달성률]\n{stats_json}\n\n"
        f"[실패 패턴 분석]\n{pattern_analysis}\n\n"
        "요구사항:\n"
        "- 100자 이상으로 작성\n"
        "- bullet 항목(-, •, *, 번호 목록) 포함\n"
        "- 구체적인 숫자 수치 포함\n"
    )

    if retry_count > 0 and quality_issues:
        issues_text = "\n".join(f"- {issue}" for issue in quality_issues)
        base_prompt += (
            f"\n이전 시도에서 다음 문제가 있었습니다:\n{issues_text}\n"
            "위 문제를 반드시 수정하여 다시 작성하세요.\n"
        )

    base_prompt += "\n리포트:"

    client = get_ollama_client()
    retrospective_report = await client.generate(base_prompt)

    return {
        "retrospective_report": retrospective_report,
        "retry_count": retry_count + 1,
    }
