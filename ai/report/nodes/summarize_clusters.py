import json

from ai.core.dependencies import get_ollama_client

MAX_CLUSTERS = 4


async def summarize_clusters(state: dict) -> dict:
    """상위 4개 클러스터를 요약하고, LLM으로 각 클러스터 주제명을 생성한다."""
    clusters: list[list[dict]] = state["clusters"]
    top_clusters = clusters[:MAX_CLUSTERS]  # extract_clusters에서 이미 size 내림차순 정렬됨

    if not top_clusters:
        return {"cluster_summaries": []}

    summaries = [
        {
            "cluster_id": idx,
            "size": len(cluster),
            "sample_texts": [task["text"] for task in cluster[:3]],
        }
        for idx, cluster in enumerate(top_clusters)
    ]

    topics = await _generate_topics(summaries)

    for s in summaries:
        i = s["cluster_id"]
        s["topic"] = topics[i] if i < len(topics) and isinstance(topics[i], str) and topics[i].strip() else f"클러스터 {i + 1}"

    return {"cluster_summaries": summaries}


async def _generate_topics(summaries: list[dict]) -> list[str]:
    """LLM에 클러스터 샘플 텍스트를 보내고 주제명 목록을 반환한다."""
    lines = "\n".join(
        f"클러스터 {s['cluster_id']}: {', '.join(s['sample_texts'])}"
        for s in summaries
    )
    prompt = (
        "아래는 실패한 할 일들을 유사도 기반으로 묶은 클러스터입니다.\n"
        "각 클러스터의 핵심 주제를 10자 이내 한국어로 요약하세요.\n"
        "다른 설명 없이 JSON 배열로만 응답하세요. 예: [\"주제1\", \"주제2\"]\n\n"
        f"{lines}\n\n응답:"
    )
    client = get_ollama_client()
    try:
        raw = await client.generate(prompt)
        start, end = raw.find("["), raw.rfind("]") + 1
        if start == -1 or end <= start:
            return []
        return json.loads(raw[start:end])
    except Exception:
        return []
