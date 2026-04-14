## 기술 스택

| 역할 | 선택 |
|---|---|
| LLM | Qwen2.5:3b (Ollama) |
| 임베딩 | intfloat/multilingual-e5-small (sentence-transformers) |
| 벡터 검색 | faiss (로컬 디스크 영구 저장) |
| 워크플로우 | LangGraph |
| API | FastAPI |
| 그래프 클러스터링 | networkx (connected components) |
