# Step 8: 통합 테스트 (Integration Test)

## 목표
AI 서버와 백엔드를 실제로 연동하여 데이터 흐름 전체를 검증한다.
단위 테스트에서 발견하지 못한 API 형식 불일치, 연결 문제, 성능 이슈를 찾아낸다.

---

## 테스트 환경

```
백엔드 서버  :8000   ← todo 데이터 제공
AI 서버     :8001   ← 분석 기능
Ollama      :11434  ← qwen2.5:3b
```

---

## 선결 과제: 백엔드 연동 방식 결정

현재 설계에서 벡터 스토어에 데이터를 채우는 방법이 명시되어 있지 않다.
두 가지 방식 중 하나를 백엔드 팀과 협의하여 결정해야 한다.

| 방식 | 설명 | 장단점 |
|------|------|--------|
| **Push (권장)** | 백엔드가 todo CRUD 시 AI 서버에 `POST/PUT/DELETE /ai/embed` 호출 | 실시간 동기화, 백엔드 수정 필요 |
| **Pull** | AI 서버 시작 시 백엔드 `GET /todos?all=true` 호출하여 전체 동기화 | 구현 단순, 실시간성 없음 |

결정에 따라 `embeddings/router.py` (Push 방식) 또는 `main.py` lifespan (Pull 방식) 추가 구현 필요.

---

## 테스트 시나리오

### 시나리오 A: 벡터 스토어 동기화 확인
- 백엔드에서 todo 생성 → AI 서버 벡터 스토어에 반영되는지 확인
- `POST /ai/interference` 호출 시 `similar_count > 0` 확인

### 시나리오 B: 실시간 간섭 E2E
- 과거 유사 실패 데이터가 있는 상태에서 같은 유형 todo 추가
- 기대값: `feedback` 비어있지 않음, `personal_rate < 30%`이면 LLM 잔소리 포함

### 시나리오 C: 월간 리포트 E2E
- 실제 사용자 한 달치 데이터로 리포트 생성

| 데이터 조건 | 기대 응답 |
|-------------|-----------|
| `monthly_logs < 10` | "열심히 살아" 잔소리 포함 |
| `failed_tasks < 3` | "데이터 부족" 메시지 |
| 정상 데이터 | `category_stats` 채워짐, `report` 100자 이상, `quality_passed=true` |

### 시나리오 D: 재시도 로직
- LLM이 품질 미달 응답을 반환하는 상황에서 재시도 횟수와 최종 종료 확인
- `retry_count`가 2에서 멈추는지 확인

---

## 백엔드 API 호환성 체크리스트

AI 서버가 호출하는 `GET /todos` 응답 형식 사전 합의:

- [ ] 응답은 리스트(`[]`) 형태
- [ ] 각 항목에 `todo_id`, `text`, `category`, `completed` 필드 존재
- [ ] `completed`는 boolean (`true`/`false`, 0/1 아님)
- [ ] `category`가 null인 경우 처리 방식 합의 ("기타"로 처리 등)
- [ ] 날짜 필터링(`month_start`)이 서버 측에서 처리됨

---

## 성능 기준

| 항목 | 목표 |
|------|------|
| `/ai/interference` (LLM 없을 때) | < 500ms |
| `/ai/interference` (LLM 있을 때) | < 5초 |
| `/ai/report/monthly` | < 60초 |
| 벡터 검색 top-20 | < 100ms |

---

## 알려진 잠재 이슈

- `faiss rebuild()` 의 `get_xb()` API가 faiss 버전에 따라 다름 → 실제 동작 확인 필요
- `nx.Graph` state 직렬화 문제 → LangGraph가 checkpoint 기능 사용 시 문제 발생 가능
- Qwen2.5 3B 한국어 응답 품질이 낮을 수 있음 → 실제 출력 확인 후 프롬프트 튜닝 필요

---

## 완료 조건

- [ ] 연동 방식 결정 및 구현
- [ ] 시나리오 A~D 모두 기대 결과와 일치
- [ ] 백엔드 API 호환성 체크리스트 완료
- [ ] 성능 기준 달성 확인
