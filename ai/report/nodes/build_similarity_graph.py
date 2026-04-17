import numpy as np
import networkx as nx

from ai.core.config import settings


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
    for i in range(n):
        for j in range(i + 1, n):
            if sim_matrix[i, j] > threshold:
                graph.add_edge(i, j, weight=float(sim_matrix[i, j]))

    return {"similarity_graph": graph}
