
## 프로젝트 구조

```
ai/
├── main.py                    # FastAPI 앱 진입점
├── core/
│   ├── config.py              # 설정 (Ollama URL, 모델명 등)
│   └── dependencies.py        # 의존성 주입 (embedding model 등) : 앱 전체에서 공용으로 쓰는 객체를 꺼내오는 창구
├── embeddings/
│   ├── model.py               # multilingual-e5-small 로더/추론
│   ├── store.py               # 벡터 저장/검색 (faiss)
│   └── router.py              # POST/PUT/DELETE /ai/embeddings/todo
├── interference/
│   ├── __init__.py
│   ├── router.py              # POST /ai/interference
│   ├── retrieval.py           # top-20 유사 task 검색
│   ├── stats.py               # 전체/개인 성공률 계산
│   ├── feedback.py            # LLM 피드백 문장 생성
│   └── demo_router.py         # 데모 전용 라우터 (DEMO_MODE=1 시 활성화)
├── report/
│   ├── __init__.py
│   ├── router.py              # POST /ai/report/monthly
│   ├── demo_router.py         # 데모 전용 라우터 (DEMO_MODE=1 시 활성화)
│   ├── graph.py               # LangGraph 워크플로우 정의
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── load_logs.py       # async: 백엔드 API에서 월간 로그 + 카테고리 통계 fetch
│   │   ├── embed_failures.py  # 실패 task 임베딩 (list로 직렬화)
│   │   ├── build_similarity_graph.py  # cosine similarity 그래프 구성
│   │   ├── extract_clusters.py        # connected components 클러스터 추출
│   │   ├── summarize_clusters.py      # LLM 입력용 클러스터 요약
│   │   ├── llm_report.py      # async: 클러스터 분석 + 월간 회고 리포트 생성 (LLM 1회)
│   │   └── quality_check.py   # 리포트 품질 검증 (길이/bullet/숫자)
│   └── state.py               # ReportState(TypedDict) 정의
├── demo/                      # HTTP 데모 스크립트 모음
│   ├── interference.py        # 간섭 파이프라인 4가지 분기 확인
│   └── report.py              # 월간 리포트 3가지 분기 확인
├── data/                      # 런타임 자동 생성
│   ├── index.faiss            # faiss 벡터 인덱스
│   └── metadata.json          # 벡터 메타데이터 (todo_id, user_id, _vec 등)
└── llm/
    └── ollama_client.py       # Ollama HTTP 클라이언트 래퍼
```