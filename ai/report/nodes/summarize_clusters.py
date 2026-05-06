import json
import logging
import re

from ai.core.dependencies import get_ollama_client

logger = logging.getLogger(__name__)

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
    logger.debug("LLM 주제명 생성 결과: %s (클러스터 수: %d)", topics, len(summaries))

    for s in summaries:
        i = s["cluster_id"]
        topic = topics[i] if i < len(topics) and isinstance(topics[i], str) and topics[i].strip() else None
        s["topic"] = topic if topic else _fallback_topic(s["sample_texts"])

    return {"cluster_summaries": summaries}


def _fallback_topic(sample_texts: list[str]) -> str:
    """LLM 실패 시 샘플 텍스트의 첫 단어들로 주제명을 구성한다."""
    first_words = [t.split()[0] for t in sample_texts if t.strip()]
    return "/".join(dict.fromkeys(first_words))[:12] if first_words else "미분류"


async def _generate_topics(summaries: list[dict]) -> list[str]:
    """LLM에 클러스터 샘플 텍스트를 보내고 주제명 목록을 반환한다."""
    lines = "\n".join(
        f"클러스터 {s['cluster_id'] + 1}: {', '.join(s['sample_texts'])}"
        for s in summaries
    )
    prompt = (
        "아래는 실패한 할 일들을 유사도 기반으로 묶은 클러스터입니다.\n"
        "각 클러스터의 핵심 주제를 10자 이내 한국어로 요약하세요.\n"
        "반드시 JSON 배열 형식으로만 응답하세요. 예: [\"주제1\", \"주제2\"]\n"
        "설명이나 다른 텍스트는 절대 포함하지 마세요.\n\n"
        f"{lines}\n\n응답:"
    )
    client = get_ollama_client()
    try:
        raw = await client.generate(prompt)
        logger.debug("LLM 원본 응답: %r", raw[:200])
        return _parse_topics(raw, len(summaries))
    except Exception as e:
        logger.warning("주제명 LLM 호출 실패: %s", e)
        return []


def _parse_topics(raw: str, expected_count: int) -> list[str]:
    """LLM 응답에서 주제명 배열을 파싱한다. JSON 실패 시 따옴표 기반으로 fallback."""
    start, end = raw.find("["), raw.rfind("]") + 1
    if start != -1 and end > start:
        try:
            parsed = json.loads(raw[start:end])
            if isinstance(parsed, list) and len(parsed) == expected_count:
                return parsed
        except json.JSONDecodeError:
            pass

    # JSON 파싱 실패 시 따옴표로 감싼 짧은 문자열 추출
    candidates = re.findall(r'"([^"]{1,12})"', raw)
    if len(candidates) >= expected_count:
        return candidates[:expected_count]

    logger.warning("주제명 파싱 실패 — raw: %r", raw[:200])
    return []
