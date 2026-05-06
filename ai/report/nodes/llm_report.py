import json

from ai.core.dependencies import get_ollama_client


async def llm_report(state: dict) -> dict:
    """cluster_summaries와 category_stats를 바탕으로 월간 회고 리포트를 생성한다."""
    cluster_summaries: list[dict] = state.get("cluster_summaries") or []
    category_stats: dict = state.get("category_stats") or {}
    retry_count: int = state.get("retry_count", 0)
    quality_issues: list[str] = state.get("quality_issues", [])

    stats_json = json.dumps(category_stats, ensure_ascii=False, indent=2)
    clusters_json = json.dumps(cluster_summaries, ensure_ascii=False, indent=2)

    base_prompt = (
        "다음 정보를 바탕으로 월간 회고 리포트를 작성하라.\n\n"
        f"[카테고리별 달성률]\n{stats_json}\n\n"
        f"[실패 클러스터 요약]\n{clusters_json}\n\n"

        "요구사항:\n"
        "- 전체 300자 이상\n"
        "- bullet 항목(-, •, *, 번호 목록) 포함\n"
        "- 모든 분석에 구체적인 숫자(%, 횟수 등) 포함\n"
        "- 단순 요약이 아닌 '원인 분석 + 개선 전략' 중심으로 작성\n\n"

        "출력 구조:\n"
        "1. 핵심 요약\n"
        "- 이번 달 성과를 한 문단으로 요약 (달성률 포함)\n\n"

        "2. 실패 클러스터 분석\n"
        "- 각 실패 클러스터별로 아래 항목 포함:\n"
        "  • 주요 실패 패턴\n"
        "  • 발생 비율 또는 횟수\n"
        "  • 근본 원인 (행동, 환경, 시간 관리 등 구체적으로)\n\n"

        "3. 개선 전략\n"
        "- 각 실패 원인에 대응되는 개선 액션 제시\n"
        "- 반드시 '측정 가능'하고 '구체적 행동'으로 작성\n"
        "  (예: '운동 더 하기' ❌ → '주 3회, 30분 운동' ⭕)\n\n"
    )

    if retry_count > 0 and quality_issues:
        issues_text = "\n".join(f"- {issue}" for issue in quality_issues)
        base_prompt += (
            f"\n이전 시도에서 다음 문제가 있었습니다:\n{issues_text}\n"
            "위 문제를 반드시 수정하여 다시 작성하세요.\n"
        )

    base_prompt += "\n리포트:"

    client = get_ollama_client()
    retrospective_report = await client.generate(base_prompt) or ""

    return {
        "retrospective_report": retrospective_report,
        "retry_count": retry_count + 1,
    }
