# Step 3: 실시간 간섭 파이프라인 (Interference)

## 목표
todo 생성 시 유사 task 성공률을 계산하고, 낮으면 LLM이 잔소리 피드백을 생성한다.
retrieval → stats → feedback 세 단계 파이프라인으로 구성된다.

---

## 구현 파일

```
ai/interference/
├── router.py
├── retrieval.py
├── stats.py
└── feedback.py
```

---

## 각 파일 역할

### `interference/retrieval.py`
- `retrieve_similar(todo_text, model, store) -> list[dict]`
- `EmbeddingModel.encode()`로 쿼리 벡터 생성 후 `EmbeddingStore.search()` 호출
- `top_k`는 `settings.TOP_K_SIMILAR` (기본 20) 사용

### `interference/stats.py`
- `compute_stats(similar_tasks, user_id) -> dict`
- 반환 필드: `global_rate`, `personal_rate`, `similar_count`, `personal_count`, `similar_failures`
- `global_rate`: top-k 전체 중 `completed / total * 100`
- `personal_rate`: `user_id` 매칭 항목만 따로 계산, 데이터 없으면 `None`
- `similar_failures`: 실패 task 텍스트 목록 (개인 실패 우선, 최대 5개)

### `interference/feedback.py`
- `async generate_feedback(todo_text, stats, ollama) -> str`
- LLM 호출 조건: `personal_rate < 30%` 일 때만
- 그 외에는 템플릿 문자열 반환 → LLM 비용 절감

**LLM 호출 분기표**:

| 조건 | 동작 |
|------|------|
| 유사 데이터 없음 | 고정 문자열 반환 |
| `personal_rate >= 30%` | 템플릿 반환 |
| `personal_rate` 없음 + `global_rate < 30%` | 템플릿 반환 |
| `personal_rate < 30%` | LLM 호출 (잔소리) |

### `interference/router.py`
- `POST /ai/interference`
- 요청: `todo_text`, `category`, `user_id`
- 응답: `global_rate`, `personal_rate`, `similar_count`, `feedback`, `similar_failures`
- `EmbeddingModel`, `EmbeddingStore`는 `Depends()`로 주입

---

## 파이프라인 흐름

```
POST /ai/interference
  │
  ├─ 1. encode(todo_text)             → 384-dim 쿼리 벡터
  ├─ 2. store.search(vec, top_k=20)   → 유사 task 목록
  ├─ 3. compute_stats(results, user_id) → 성공률 계산
  └─ 4. generate_feedback(...)
         ├─ personal_rate < 30% → LLM 잔소리
         └─ 그 외             → 템플릿 문자열
```

---

## 주의사항

- `similar_tasks`가 빈 리스트일 때 stats 함수가 안전하게 처리되어야 함
- 피드백 생성에서 LLM 호출 여부가 `personal_rate` 기준임에 주의
  (`global_rate`가 낮아도 `personal_rate`가 없거나 높으면 LLM 미호출)

---

## 완료 조건

- [ ] `POST /ai/interference` 200 응답, 명세 형식 일치
- [ ] 빈 벡터 스토어에서도 에러 없이 동작
- [ ] `personal_rate < 30%`일 때만 LLM 호출됨을 확인
- [ ] `similar_failures` 개인 실패 우선 정렬 확인
