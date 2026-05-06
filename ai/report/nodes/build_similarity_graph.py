import logging

import numpy as np
import networkx as nx

from ai.core.config import settings

logger = logging.getLogger(__name__)


def build_similarity_graph(state: dict) -> dict:
    """failure_embeddings의 cosine similarity로 유사도 그래프를 구성한다."""
    embeddings: list[list[float]] = state["failure_embeddings"]
    n = len(embeddings)

    graph = nx.Graph()
    graph.add_nodes_from(range(n))

    if n < 2:
        return {"similarity_graph": graph}

    # L2 정규화된 벡터이므로 내적 = cosine similarity
    mat = np.array(embeddings, dtype=np.float32)
    sim_matrix = mat @ mat.T

    threshold = settings.COSINE_THRESHOLD
    pair_sims = [sim_matrix[i, j] for i in range(n) for j in range(i + 1, n)]
    logger.debug(
        "유사도 분포: n=%d, min=%.3f, max=%.3f, mean=%.3f, threshold=%.2f",
        n, float(np.min(pair_sims)), float(np.max(pair_sims)), float(np.mean(pair_sims)), threshold,
    )

    for i in range(n):
        for j in range(i + 1, n):
            if sim_matrix[i, j] > threshold:
                graph.add_edge(i, j, weight=float(sim_matrix[i, j]))

    logger.debug("그래프 구성 완료: nodes=%d, edges=%d", n, graph.number_of_edges())
    return {"similarity_graph": graph}
