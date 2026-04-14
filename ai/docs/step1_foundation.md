# Step 1: 기반 구축 (Foundation)

## 목표
임베딩 모델 로더, Ollama 클라이언트, 전역 설정을 구현한다.
이후 모든 모듈이 이 기반 위에서 동작하므로 가장 먼저 완성해야 한다.

---

## 구현 파일

```
ai/
├── main.py
├── core/
│   ├── config.py
│   └── dependencies.py
├── embeddings/
│   └── model.py
└── llm/
    └── ollama_client.py
```

---

## 각 파일 역할

### `core/config.py`
- `pydantic-settings`의 `BaseSettings`를 상속한 `Settings` 클래스
- `.env` 파일이 있으면 우선 적용, 없으면 기본값 사용
- plan.md의 환경 설정 섹션에 정의된 모든 변수 포함
- 모듈 하단에 `settings = Settings()` 싱글턴 인스턴스 생성

### `core/dependencies.py`
- `@lru_cache`를 이용한 `get_embedding_model()` 함수
- FastAPI `Depends()`와 함께 사용할 싱글턴 팩토리
- Step 2 완료 후 `get_embedding_store()`도 여기에 추가

### `embeddings/model.py`
- `SentenceTransformer` 모델을 래핑한 `EmbeddingModel` 클래스
- `encode(text)` : 검색 쿼리용 인코딩 — `"query: "` 접두어 필요 (e5 모델 규칙)
- `encode_passage(text)` : todo 저장용 인코딩 — `"passage: "` 접두어
- 두 메서드 모두 L2 정규화된 `float32` 벡터 반환 (내적 = cosine similarity)

### `llm/ollama_client.py`
- Ollama `/api/generate` 엔드포인트를 호출하는 `OllamaClient` 클래스
- `async def generate(prompt: str) -> str`
- `httpx.AsyncClient` 사용 (FastAPI async 환경 호환)
- `stream=False`로 전체 응답을 한 번에 수신

### `main.py`
- FastAPI 앱 인스턴스 생성
- `lifespan` 이벤트 핸들러에서 서버 시작 시 모델 pre-load
- 라우터 등록은 Step 7에서 추가

---

## 주의사항

- `EmbeddingModel`은 로딩이 무거우므로 반드시 싱글턴으로 관리
- e5 모델은 `query:` / `passage:` 접두어 유무에 따라 벡터 품질이 달라짐
- Ollama 타임아웃은 로컬 Qwen2.5 3B 기준 여유롭게 설정 (60초 이상)

---

## 완료 조건

- [ ] `EmbeddingModel().encode("테스트")` → shape `(384,)` 반환
- [ ] `OllamaClient().generate("안녕")` → 문자열 응답 반환
- [ ] `uvicorn main:app` 기동 성공
