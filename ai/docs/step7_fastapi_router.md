# Step 7: FastAPI 라우터 연결

## 목표
간섭(interference)과 월간 리포트(report) 두 엔드포인트를 FastAPI 앱에 등록하고 `main.py`를 완성한다.

---

## 수정/구현 파일

```
ai/
├── main.py                 ← 라우터 등록, lifespan 완성
├── embeddings/
│   └── router.py           ← POST/PUT/DELETE /ai/embeddings/todo (신규)
└── report/
    └── router.py           ← POST /ai/report/monthly
```

(interference/router.py는 Step 3에서 이미 구현됨)

---

## `report/router.py`

- `POST /ai/report/monthly`
- 요청: `user_id`
- `month_start`는 요청 시각 기준 -30일로 서버에서 계산하여 initial_state에 주입
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
  app.include_router(embeddings_router)

헬스체크:
  GET /health → {"status": "ok"}
```

---

## `embeddings/router.py` (신규)

FAISS 스토어에 TODO 벡터를 관리하는 엔드포인트.
백엔드가 TODO 상태(완료/실패)가 확정될 때 호출한다.

### `POST /ai/embeddings/todo`

TODO 완료 또는 실패 확정 시 임베딩을 생성하여 FAISS에 저장한다.

- 요청: `todo_id`, `user_id`, `category`, `text`, `completed`
- 처리: `model.encode(text)` → `store.add(todo_id, vec, meta)` → `store.save()`
- 응답: `{"todo_id": "...", "indexed": true}`
- 중복 `todo_id` 요청 시 `409 Conflict`

### `DELETE /ai/embeddings/todo/{todo_id}`

TODO 삭제 시 FAISS에서 soft delete한다.

- 처리: `store.delete(todo_id)` → `store.save()`
- 응답: `{"todo_id": "...", "deleted": true}`

### `PUT /ai/embeddings/todo/{todo_id}`

TODO 텍스트 수정 시 임베딩을 재생성한다.

- 요청: `user_id`, `category`, `text`, `completed`
- 처리: `store.update(todo_id, new_vec, new_meta)` → `store.save()`
- 응답: `{"todo_id": "...", "updated": true}`

> **설계 근거**: `store.add()`는 완료/실패 확정 이후에만 호출한다.
> 미완료 TODO는 저장하지 않아 유사도 검색 품질을 보장한다.

---

## 전체 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 확인 |
| POST | `/ai/interference` | 실시간 간섭 |
| POST | `/ai/report/monthly` | 월간 회고 리포트 |
| POST | `/ai/embeddings/todo` | TODO 완료 시 임베딩 저장 |
| DELETE | `/ai/embeddings/todo/{todo_id}` | TODO 삭제 시 soft delete |
| PUT | `/ai/embeddings/todo/{todo_id}` | TODO 수정 시 임베딩 갱신 |

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
- [ ] `POST /ai/embeddings/todo` → FAISS 저장 및 디스크 반영 확인
- [ ] 중복 `todo_id` 요청 시 `409 Conflict` 반환
- [ ] `DELETE /ai/embeddings/todo/{todo_id}` → soft delete 확인
- [ ] `PUT /ai/embeddings/todo/{todo_id}` → 임베딩 갱신 확인
- [ ] `/docs` Swagger UI에서 두 엔드포인트 스키마 확인
- [ ] Ollama 미실행 시 503 반환
