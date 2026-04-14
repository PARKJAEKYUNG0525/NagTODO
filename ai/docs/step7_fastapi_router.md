# Step 7: FastAPI 라우터 연결

## 목표
간섭(interference)과 월간 리포트(report) 두 엔드포인트를 FastAPI 앱에 등록하고 `main.py`를 완성한다.

---

## 수정/구현 파일

```
ai/
├── main.py                 ← 라우터 등록, lifespan 완성
└── report/
    └── router.py           ← POST /ai/report/monthly
```

(interference/router.py는 Step 3에서 이미 구현됨)

---

## `report/router.py`

- `POST /ai/report/monthly`
- 요청: `user_id`, `month_start`
- `report_graph.ainvoke(initial_state)` 호출 후 결과 반환
- 응답: `category_stats`, `clusters`, `cluster_summaries`, `report`, `quality_passed`, `quality_issues`
- initial_state의 모든 필드를 빈 값으로 초기화하여 그래프에 전달

---

## `main.py` 완성

```
lifespan:
  서버 시작 시 → get_embedding_model(), get_embedding_store() pre-load

라우터:
  app.include_router(interference_router)
  app.include_router(report_router)

헬스체크:
  GET /health → {"status": "ok"}
```

---

## 전체 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 확인 |
| POST | `/ai/interference` | 실시간 간섭 |
| POST | `/ai/report/monthly` | 월간 회고 리포트 |

---

## 에러 처리

- Ollama 서버 미실행 → `503 Service Unavailable`
- 백엔드 API 연결 실패 → `503 Service Unavailable`
- 그래프 실행 중 예외 → `500 Internal Server Error` + 메시지

---

## 주의사항

- 멀티 프로세스 시 faiss 인덱스 동기화 문제 → `--workers 1`로 실행
- `report_graph`는 `graph.py` 모듈 임포트 시 빌드됨 → 앱 시작 시 컴파일 에러 즉시 확인 가능

---

## 완료 조건

- [ ] `uvicorn main:app` 정상 기동
- [ ] `GET /health` → `{"status": "ok"}`
- [ ] `POST /ai/interference` 응답 형식 일치
- [ ] `POST /ai/report/monthly` 응답 형식 일치
- [ ] `/docs` Swagger UI에서 두 엔드포인트 스키마 확인
- [ ] Ollama 미실행 시 503 반환
