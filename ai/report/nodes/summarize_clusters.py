import json
import logging
import re

from ai.core.dependencies import get_openai_client

# Backward-compatible alias for existing tests/patch paths.
get_ollama_client = get_openai_client

logger = logging.getLogger(__name__)

MAX_CLUSTERS = 4


async def summarize_clusters(state: dict) -> dict:
    """Summarize top clusters and generate short topics with LLM."""
    clusters: list[list[dict]] = state["clusters"]
    top_clusters = clusters[:MAX_CLUSTERS]
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
    logger.debug("Generated topics: %s (clusters=%d)", topics, len(summaries))

    for summary in summaries:
        idx = summary["cluster_id"]
        topic = topics[idx] if idx < len(topics) and isinstance(topics[idx], str) and topics[idx].strip() else None
        summary["topic"] = topic if topic else _fallback_topic(summary["sample_texts"])

    return {"cluster_summaries": summaries}


def _fallback_topic(sample_texts: list[str]) -> str:
    first_words = [text.split()[0] for text in sample_texts if text.strip()]
    return "/".join(dict.fromkeys(first_words))[:12] if first_words else "미분류"


async def _generate_topics(summaries: list[dict]) -> list[str]:
    lines = "\n".join(
        f"클러스터 {s['cluster_id'] + 1}: {', '.join(s['sample_texts'])}"
        for s in summaries
    )
    prompt = (
        "아래 실패 문장들은 유사도 기반으로 묶인 클러스터입니다.\n"
        "각 클러스터의 공통 주제를 10자 이내 한국어로 요약하세요.\n"
        "반드시 JSON 배열 형식으로만 답하세요. 예: [\"주제1\", \"주제2\"]\n"
        "설명이나 다른 텍스트는 포함하지 마세요.\n\n"
        f"{lines}\n\n응답:"
    )

    client = get_openai_client()
    try:
        raw = await client.generate(prompt)
        logger.debug("Raw LLM topic response: %r", raw[:200])
        return _parse_topics(raw, len(summaries))
    except Exception as e:
        logger.warning("Topic generation failed: %s", e)
        return []


def _parse_topics(raw: str, expected_count: int) -> list[str]:
    start, end = raw.find("["), raw.rfind("]") + 1
    if start != -1 and end > start:
        try:
            parsed = json.loads(raw[start:end])
            if isinstance(parsed, list) and len(parsed) == expected_count:
                return parsed
        except json.JSONDecodeError:
            pass

    candidates = re.findall(r'"([^"]{1,12})"', raw)
    if len(candidates) >= expected_count:
        return candidates[:expected_count]

    logger.warning("Topic parse failed. raw=%r", raw[:200])
    return []
