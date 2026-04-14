# Step 4: LangGraph 노드 독립 구현

## 목표
월간 리포트 워크플로우를 구성하는 각 노드를 독립적으로 구현하고 단위 테스트한다.
각 노드는 `ReportState`를 받아 변경된 필드만 반환하는 함수다.

---

## 구현 파일

```
ai/report/
├── state.py
└── nodes/
    ├── load_logs.py
    ├── compute_stats.py
    ├── embed_failures.py
    ├── build_similarity_graph.py
    ├── extract_clusters.py
    ├── summarize_clusters.py
    ├── llm_analysis.py
    ├── llm_report.py
    └── quality_check.py
```

---

## `report/state.py`

`ReportState(TypedDict)` 정의, 필드 목록:

| 필드 | 타입 | 설명 |
|------|------|------|
| `user_id` | str | 입력 |
| `month_start` | str | 입력 ("YYYY-MM-DD") |
| `monthly_logs` | list[dict] | 이번 달 전체 task |
| `failed_tasks` | list[dict] | 실패 task만 |
| `category_stats` | dict | 카테고리별 달성률 |
| `failure_embeddings` | list | 실패 task 벡터 (list로 직렬화) |
| `similarity_graph` | Optional[Any] | nx.Graph (직렬화 불가 주의) |
| `clusters` | list[list[dict]] | 클러스터 목록 |
| `cluster_summaries` | list[dict] | 클러스터 요약 |
| `pattern_analysis` | str | LLM 패턴 분석 결과 |
| `retrospective_report` | str | 최종 리포트 |
| `quality_passed` | bool | 품질 검증 통과 여부 |
| `quality_issues` | list[str] | 품질 실패 이유 목록 |
| `retry_count` | int | LLM 재시도 횟수 |

---

## 노드별 역할

### `load_logs.py` — `async` 노드
- 백엔드 API `GET /todos`에서 해당 유저의 월간 로그 fetch
- `monthly_logs`, `failed_tasks` 업데이트

### `compute_stats.py`
- `monthly_logs`에서 카테고리별 `total`, `completed`, `rate` 집계
- `category_stats` 업데이트

### `embed_failures.py`
- `failed_tasks` 각 텍스트를 `encode_passage()`로 변환
- nx.Graph 직렬화 문제를 피하기 위해 np.ndarray 대신 list로 저장
- `failure_embeddings` 업데이트

### `build_similarity_graph.py`
- `failure_embeddings`로 cosine similarity 행렬 계산
- threshold(`settings.COSINE_THRESHOLD = 0.75`) 초과 쌍을 엣지로 추가
- `similarity_graph`(nx.Graph) 업데이트

### `extract_clusters.py`
- `nx.connected_components()`로 클러스터 추출
- `min_size`(`settings.MIN_CLUSTER_SIZE = 2`) 미만 고립 노드 제외
- 클러스터 크기 내림차순 정렬
- `clusters` 업데이트

### `summarize_clusters.py`
- 각 클러스터의 `cluster_id`, `size`, `dominant_category`, `sample_texts`(최대 3개) 집계
- LLM 입력 크기를 줄이기 위한 사전 요약
- `cluster_summaries` 업데이트

### `llm_analysis.py` — `async` 노드
- `cluster_summaries`를 JSON으로 직렬화하여 프롬프트 구성
- LLM에게 각 클러스터 실패 원인 1-2문장 분석 요청
- `pattern_analysis` 업데이트

### `llm_report.py` — `async` 노드
- `pattern_analysis` + `category_stats`를 바탕으로 최종 리포트 생성
- 재시도 시(`retry_count > 0`) `quality_issues`를 프롬프트에 포함하여 개선 유도
- `retrospective_report`, `retry_count` 업데이트

### `quality_check.py`
- 3가지 규칙으로 리포트 품질 검증 (아래 표)
- `quality_passed`, `quality_issues` 업데이트

**검증 규칙**:

| 규칙 | 기준 |
|------|------|
| 최소 길이 | 리포트 >= 100자 |
| bullet 항목 | `-, •, *, 번호 목록` 중 하나 이상 |
| 숫자 인용 | 리포트에 숫자(`\d+`) 포함 |

---

## 특수 터미널 노드

그래프 조립(Step 5)에서 등록할 두 개의 조기 종료 노드.
별도 파일 없이 `report/graph.py` 내에 인라인으로 작성해도 무방하다.

- `too_few_tasks`: task 수 부족 시 잔소리 메시지 반환 후 종료
- `minimal_report`: 실패 데이터 부족 시 간단 통계만 반환 후 종료

---

## 주의사항

- 비동기 노드(`load_logs`, `llm_*`)는 반드시 `async def`로 정의
- 각 노드는 담당 필드만 dict로 반환 (전체 state 반환 X)
- `nx.Graph`는 JSON 직렬화 불가 → state 필드 타입을 `Optional[Any]`로 선언
- `failure_embeddings`는 `np.ndarray`가 아닌 `list`로 저장하여 직렬화 문제 회피

---

## 완료 조건

- [ ] 모든 노드가 `state: dict → dict` 시그니처로 구현
- [ ] 비동기 노드는 `async def` 사용
- [ ] `quality_check` 규칙 3가지 모두 동작 확인
- [ ] 각 노드 입출력 단위 테스트 통과
