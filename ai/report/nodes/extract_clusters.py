import logging

import networkx as nx

from ai.core.config import settings

logger = logging.getLogger(__name__)


def extract_clusters(state: dict) -> dict:
    """similarity_graph에서 연결 컴포넌트를 클러스터로 추출한다."""
    graph: nx.Graph = state["similarity_graph"]
    failed_tasks: list[dict] = state["failed_tasks"]
    min_size = settings.MIN_CLUSTER_SIZE

    raw_components = list(nx.connected_components(graph))
    logger.debug(
        "연결 컴포넌트: 전체=%d, min_size(%d) 이상=%d",
        len(raw_components),
        min_size,
        sum(1 for c in raw_components if len(c) >= min_size),
    )

    clusters = sorted(
        [
            [failed_tasks[i] for i in component]
            for component in raw_components
            if len(component) >= min_size
        ],
        key=len,
        reverse=True,
    )

    logger.debug("클러스터 추출 완료: %d개, 크기=%s", len(clusters), [len(c) for c in clusters])
    return {"clusters": clusters}
