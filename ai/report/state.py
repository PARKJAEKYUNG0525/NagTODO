from __future__ import annotations

from typing import Any, Optional
from typing_extensions import TypedDict

'''ReportState(TypedDict) 정의'''

class ReportState(TypedDict, total=False):
    # 입력
    user_id: str
    month_start: str  # "YYYY-MM-DD"

    # 로그 로드
    monthly_logs: list[dict]
    failed_tasks: list[dict]

    # 통계
    category_stats: dict  # {category: {total, completed, rate}}

    # 임베딩
    failure_embeddings: list  # list[list[float]] — np.ndarray 직렬화 문제 방지

    # 그래프 / 클러스터링
    similarity_graph: Optional[Any]  # nx.Graph (JSON 직렬화 불가)
    clusters: list[list[dict]]
    cluster_summaries: list[dict]

    # LLM 결과
    pattern_analysis: str
    retrospective_report: str
    retry_count: int

    # 품질 검증
    quality_passed: bool
    quality_issues: list[str]
