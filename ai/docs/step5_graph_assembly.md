# Step 5: LangGraph 그래프 조립

## 목표
Step 4에서 구현한 노드들을 LangGraph `StateGraph`로 연결한다.
조건부 엣지, 재시도 루프, 종료 조건을 포함한 완전한 워크플로우를 완성한다.

---

## 구현 파일

```
ai/report/
└── graph.py
```

---

## 그래프 구조

```
START
  ↓
[load_monthly_logs]
  ↓
<task 수 < 10?>
  ├─ YES → [too_few_tasks] → END
  └─ NO  ↓
[compute_category_stats]
  ↓
[embed_failures]
  ↓
<실패 task 수 < 3?>
  ├─ YES → [minimal_report] → END
  └─ NO  ↓
[build_similarity_graph]
  ↓
[extract_clusters]
  ↓
[summarize_clusters]
  ↓
[llm_pattern_analysis]
  ↓
[llm_retrospective_report]
  ↓
[quality_check]
  ↓
<quality_passed?>
  ├─ YES → END
  └─ NO  ↓
<retry_count < 2?>
  ├─ YES → [llm_retrospective_report]   ← 재시도
  └─ NO  → END
```

---

## `report/graph.py` 구성

### 조건부 엣지 함수 (3개)

| 함수 | 판단 기준 | 분기 대상 |
|------|-----------|-----------|
| `_check_task_count` | `len(monthly_logs) < MIN_MONTHLY_TASKS` | `too_few_tasks` / `compute_category_stats` |
| `_check_failure_count` | `len(failed_tasks) < 3` | `minimal_report` / `build_similarity_graph` |
| `_route_after_quality` | `quality_passed`, `retry_count < 2` | `END` / `llm_retrospective_report` |

### 노드 등록 목록

`too_few_tasks`, `minimal_report` 두 터미널 노드도 이 파일에 인라인으로 정의한다.

### 그래프 빌드

`build_report_graph()` 함수로 `StateGraph` 구성 후 `.compile()` 반환.
모듈 하단에 `report_graph = build_report_graph()` 싱글턴 인스턴스 생성.

---

## 재시도 루프 설계

`quality_check` 실패 시 `llm_retrospective_report`로 되돌아간다.
`retry_count`는 `llm_report.py` 노드가 실행될 때마다 +1한다.
`retry_count >= 2`이면 품질 미달이어도 현재 리포트를 그대로 반환하고 종료한다.

---

## 주의사항

- LangGraph 조건부 엣지 함수는 `state`를 보고 **노드 이름 문자열** 또는 `END`를 반환해야 함
- `_route_after_quality` 하나의 함수에서 `quality_passed`와 `retry_count`를 함께 확인하는 것이 단순함
  (중간에 별도 분기 노드를 두지 않아도 됨)
- `similarity_graph`(nx.Graph)는 state에 저장되지만 LangGraph가 내부적으로 직렬화를 시도할 수 있음
  → 문제가 생기면 `build_similarity_graph` 노드에서 graph를 인접 행렬 등으로 변환하여 저장하는 방식으로 대체

---

## 완료 조건

- [ ] `build_report_graph()` 컴파일 에러 없음
- [ ] task 수 < 10 → `too_few_tasks` 경로 실행
- [ ] 실패 수 < 3 → `minimal_report` 경로 실행
- [ ] `quality_passed=True` → END 도달
- [ ] `quality_passed=False`, `retry_count=0` → `llm_retrospective_report` 재실행
- [ ] `quality_passed=False`, `retry_count=2` → 재시도 없이 END 도달
