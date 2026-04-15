
## 프로젝트 구조

```
ai/
├── main.py                    # FastAPI 앱 진입점
├── core/
│   ├── config.py              # 설정 (Ollama URL, 모델명 등)
│   └── dependencies.py        # 의존성 주입 (embedding model 등) : 앱 전체에서 공용으로 쓰는 객체를 꺼내오는 창구
├── embeddings/
│   ├── model.py               # multilingual-e5-small 로더/추론
│   └── store.py               # 벡터 저장/검색 (faiss)
├── interference/
│   ├── router.py              # POST /ai/interference
│   ├── retrieval.py           # top-20 유사 task 검색
│   ├── stats.py               # 전체/개인 성공률 계산
│   └── feedback.py            # LLM 피드백 문장 생성
├── report/
│   ├── router.py              # POST /ai/report/monthly
│   ├── graph.py               # LangGraph 워크플로우 정의
│   ├── nodes/
│   │   ├── load_logs.py
│   │   ├── compute_stats.py
│   │   ├── embed_failures.py
│   │   ├── build_similarity_graph.py
│   │   ├── extract_clusters.py
│   │   ├── summarize_clusters.py
│   │   ├── llm_analysis.py
│   │   ├── llm_report.py
│   │   └── quality_check.py
│   └── state.py               # LangGraph State 타입 정의
├── data/                      # 런타임 자동 생성
│   ├── index.faiss            # faiss 벡터 인덱스
│   └── metadata.json          # 벡터 메타데이터 (todo_id, user_id, _vec 등)
└── llm/
    └── ollama_client.py       # Ollama HTTP 클라이언트 래퍼
```