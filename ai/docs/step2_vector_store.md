# Step 2: 벡터 스토어 (Vector Store)

## 목표
faiss 인덱스와 메타데이터를 함께 관리하는 저장소를 구현한다.
todo의 추가/삭제/수정/검색이 가능하며 디스크에 영구 저장된다.

---

## 구현 파일

```
ai/
├── embeddings/
│   └── store.py
└── data/               ← 런타임에 자동 생성
    ├── index.faiss
    └── metadata.json
```

---

## 데이터 구조

faiss는 벡터만 저장하므로 메타데이터를 별도 JSON 파일로 관리한다.
faiss 인덱스의 i번째 행 ↔ `metadata[i]` 가 1:1 대응된다.

**metadata.json 항목 필드**: `todo_id`, `user_id`, `category`, `text`, `completed`, `is_deleted`

---

## `embeddings/store.py`

`EmbeddingStore` 클래스, 메서드 목록:

| 메서드 | 설명 |
|--------|------|
| `search(query_vec, top_k)` | cosine similarity top-k 검색, `is_deleted=True` 항목 제외 |
| `add(todo_id, vec, meta)` | 벡터 + 메타데이터 추가 |
| `delete(todo_id)` | `is_deleted=True`로 마킹 (soft delete, 벡터는 유지) |
| `update(todo_id, new_vec, new_meta)` | delete → add 순서로 처리 |
| `rebuild()` | `is_deleted` 항목 완전 제거 후 인덱스 재구축 |
| `save()` | `index.faiss` + `metadata.json` 디스크 저장 |
| `load()` | 서버 시작 시 디스크에서 로드, 이후 `rebuild()` 호출 |

**faiss 인덱스 타입**: `IndexFlatIP` (내적 기반, 벡터 정규화 전제 시 cosine similarity와 동일)

---

## todo 수정 흐름

```
todo 수정 요청
→ store.delete(todo_id)
→ 새 텍스트 임베딩
→ store.add(todo_id, new_vec, new_meta)
→ store.save()

서버 재시작 시
→ store.load() → store.rebuild()   ← is_deleted 항목 완전 제거
```

---

## `core/dependencies.py` 업데이트

`get_embedding_store()` 팩토리 함수 추가 (`@lru_cache`, `load()` 호출 포함)

`main.py` lifespan에서 `get_embedding_store()` 호출하여 서버 시작 시 pre-load

---

## 주의사항

- `rebuild()` 시 faiss 내부 벡터를 직접 추출하는 API(`get_xb()`)는 버전에 따라 다를 수 있음
  - 대안: 원본 벡터를 metadata에 함께 저장 (메모리↑, 구현 단순↓)
- soft delete 방식이므로 `search()` 에서 반드시 `is_deleted` 필터링 필요
- 동시 쓰기 충돌 방지를 위해 서버는 단일 워커(`--workers 1`)로 실행

---

## 완료 조건

- [ ] `add` → `search` → 결과 반환 정상 동작
- [ ] `delete` 후 `search` 결과에서 제외 확인
- [ ] `save` → `load` 후 동일 데이터 복원
- [ ] `rebuild` 후 `is_deleted` 항목 완전 제거 확인
