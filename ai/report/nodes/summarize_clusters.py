from collections import Counter


def summarize_clusters(state: dict) -> dict:
    """각 클러스터를 LLM 입력용 요약 dict로 변환한다."""
    clusters: list[list[dict]] = state["clusters"]

    summaries = []
    for idx, cluster in enumerate(clusters):
        categories = [task.get("category", "기타") for task in cluster]
        dominant_category = Counter(categories).most_common(1)[0][0]
        sample_texts = [task["text"] for task in cluster[:3]]

        summaries.append({
            "cluster_id": idx,
            "size": len(cluster),
            "dominant_category": dominant_category,
            "sample_texts": sample_texts,
        })

    return {"cluster_summaries": summaries}
