import networkx as nx

from ai.core.config import settings


def extract_clusters(state: dict) -> dict:
    """similarity_graph에서 연결 컴포넌트를 클러스터로 추출한다."""
    graph: nx.Graph = state["similarity_graph"]
    failed_tasks: list[dict] = state["failed_tasks"]
    min_size = settings.MIN_CLUSTER_SIZE

    raw_components = list(nx.connected_components(graph))

    clusters = sorted(
        [
            [failed_tasks[i] for i in component]
            for component in raw_components
            if len(component) >= min_size
        ],
        key=len,
        reverse=True,
    )

    return {"clusters": clusters}
