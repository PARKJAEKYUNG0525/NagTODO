# NagTODO AI 파트 상세 구현 계획

## Feature 1: 실시간 간섭 (Todo 생성 시)

### API

```
POST /ai/interference
{
  "todo_text": "밤 11시에 하체 운동 1시간",
  "category": "운동",
  "user_id": "user_123"
}

→ {
  "global_rate": 23,
  "personal_rate": 10,
  "similar_count": 20,
  "feedback": "지난 3번의 유사한 '밤 운동' todo는 모두 실패했습니다. 정말 이번엔 다를 것 같으세요?",
  "similar_failures": ["밤 11시 런닝", ...]
}
```

### 흐름 상세

```
1. embeddings/model.py
   - query_prefix = "query: " + todo_text  ← e5 모델 규칙
   - encode() → 384-dim vector

2. embeddings/store.py
   - 전체 todo 벡터 DB에서 cosine similarity top-20 검색
   - (필터: category 동일 우선 (가중치 부여 가능))

3. interference/stats.py
   - global_rate = top-20 중 completed / total * 100
   - personal_rate = user_id 매칭된 것만 계산

4. interference/feedback.py
   - personal_rate < 30% → LLM 호출
   - 그 외 → 템플릿 문장만 사용 (LLM 비용 절감)

5. llm/ollama_client.py
   - prompt: "사용자가 '{todo}'를 추가했다. 유사 task 성공률은 {rate}%다.
              잔소리꾼 AI로서 짧고 날카롭게 한 마디 해라."
   - /api/generate (stream=False)
```

### 임베딩 저장소 설계

faiss는 벡터만 저장하므로 메타데이터를 별도 파일로 함께 관리합니다.

```
ai/data/
├── index.faiss        # 벡터 인덱스 (faiss)
└── metadata.json      # 벡터와 1:1 대응 메타데이터
```

```python
class EmbeddingStore:
    index: faiss.IndexFlatIP      # 내적 기반 cosine similarity (정규화 전제)
    metadata: list[dict]          # todo_id, user_id, category, completed, text, is_deleted

    def search(query_vec, top_k=20) -> list[dict]  # is_deleted=True 필터링
    def add(todo_id, vec, meta)
    def delete(todo_id)           # metadata의 is_deleted = True로 마킹
    def update(todo_id, new_vec, new_meta)  # delete → add
    def rebuild()                 # is_deleted 항목 제거 후 인덱스 재구축
    def save()                    # index.faiss + metadata.json 디스크 저장
    def load()                    # 서버 시작 시 디스크에서 로드 + rebuild 호출
```

**todo 수정 흐름**
```
todo 수정 요청
→ delete(todo_id)       # 기존 벡터 soft delete
→ 새 텍스트 임베딩
→ add(todo_id, new_vec, new_meta)
→ save()

서버 시작 시
→ load() → rebuild()   # is_deleted 항목 제거, 인덱스 정리
```

---

## Feature 2: 월간 리포트 (LangGraph)

### API

```
POST /ai/report/monthly
{
  "user_id": "user_123",
  "month_start": "2026-04-07"
}

→ {
  "category_stats": [...],
  "clusters": [...],
  "report": "...",
  "improvements": [...]
}
```

### LangGraph State

```python
class ReportState(TypedDict):
    user_id: str
    month_start: str

    # 데이터 레이어
    monthly_logs: list[dict]          # 이번 주 전체 task 로그
    failed_tasks: list[dict]         # 실패 task만

    # 통계 레이어
    category_stats: dict             # 카테고리별 달성률

    # 클러스터 레이어
    failure_embeddings: np.ndarray   # 실패 task 임베딩
    similarity_graph: nx.Graph       # cosine threshold 그래프
    clusters: list[list[dict]]       # 클러스터 목록
    cluster_summaries: list[dict]    # 각 클러스터 요약 (LLM 입력용)

    # 리포트 레이어
    pattern_analysis: str            # LLM 패턴 분석
    retrospective_report: str        # 최종 리포트

    # 검증
    quality_passed: bool
    quality_issues: list[str]
    retry_count: int
```

### LangGraph 그래프 구조

> **LangGraph 개념 정리**
> - **노드 (Node)**: 실제 로직을 실행하는 함수. `state`를 받아 처리 후 변경된 state 일부를 반환.
> - **엣지 (Edge)**: 노드 간 연결. 항상 다음 노드로 이동.
> - **조건부 엣지 (Conditional Edge)**: 분기 함수. state를 보고 다음에 실행할 노드 이름을 반환. `add_conditional_edges()`로 등록.

```
# ─────────────────────────────────────────────
# [노드]           실제 로직 실행
# <조건부 엣지>    state를 보고 다음 노드를 결정하는 분기
# ─────────────────────────────────────────────

START
  ↓
[노드] load_monthly_logs
  ↓
<조건부 엣지> task 수 < 10?
  ├─ YES → [노드] too_few_tasks        → END  (열심히 살고 분석 요청하라고 잔소리)
  └─ NO  ↓
[노드] compute_category_stats
  ↓
[노드] embed_failures
  ↓
<조건부 엣지> 실패 task 수 < 3?
  ├─ YES → [노드] minimal_report       → END  (실패 데이터 부족, 간단 리포트 반환)
  └─ NO  ↓
[노드] build_similarity_graph          (cosine threshold: 0.75)
  ↓
[노드] extract_clusters                (connected components, min_size=2)
  ↓
[노드] summarize_clusters              (클러스터별 메타 집계)
  ↓
[노드] llm_pattern_analysis            (Qwen2.5 3B)
  ↓
[노드] llm_retrospective_report        (Qwen2.5 3B)
  ↓
[노드] quality_check
  ↓
<조건부 엣지> 검증 통과?
  ├─ YES → END
  └─ NO  ↓
<조건부 엣지> retry_count < 2?
  ├─ YES → [노드] llm_retrospective_report  (재시도)
  └─ NO  → END                             (최대 재시도 초과, 현재 결과 반환)
```

---

## 환경 설정

```python
# core/config.py
class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b"
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"
    BACKEND_API_URL: str = "http://localhost:8000"

    FAISS_INDEX_PATH: str = "data/index.faiss"
    FAISS_METADATA_PATH: str = "data/metadata.json"

    COSINE_THRESHOLD: float = 0.75   # 클러스터 threshold
    MIN_CLUSTER_SIZE: int = 2
    TOP_K_SIMILAR: int = 20
    MIN_MONTHLY_TASKS: int = 10      # 리포트 최소 task 수
```

## 의존성

```
# requirements.txt
fastapi
uvicorn
sentence-transformers
faiss-gpu
numpy        # faiss 내부 연산용
networkx
langgraph
langchain
httpx        # Ollama 클라이언트
pydantic-settings
```

---

## 구현 순서

1. **기반 구축** - embedding model 로더, Ollama 클라이언트, config
2. **벡터 스토어** - faiss 인덱스 구축, 디스크 저장/로드
3. **실시간 간섭** - retrieval → stats → feedback 파이프라인
4. **LangGraph 노드** - 각 노드 독립 구현 및 단위 테스트
5. **그래프 조립** - 노드 연결, 조건부 엣지, 리트라이 로직
6. **품질 검증** - quality_check 규칙 구현
7. **FastAPI 라우터** - 두 엔드포인트 연결
8. **통합 테스트** - 백엔드와 연동 테스트
