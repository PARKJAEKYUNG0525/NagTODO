import json

from ai.core.dependencies import get_ollama_client


async def llm_analysis(state: dict) -> dict:
    """cluster_summaries를 기반으로 LLM에게 실패 패턴 분석을 요청한다."""
    cluster_summaries: list[dict] = state["cluster_summaries"]

    clusters_json = json.dumps(cluster_summaries, ensure_ascii=False, indent=2)
    prompt = (
        "다음은 이번 달 실패한 TODO 클러스터 요약입니다.\n"
        "각 클러스터에 대해 실패 원인을 1~2문장으로 분석해주세요.\n\n"
        f"{clusters_json}\n\n"
        "분석 결과:"
    )

    client = get_ollama_client()
    pattern_analysis = await client.generate(prompt)

    return {"pattern_analysis": pattern_analysis}
