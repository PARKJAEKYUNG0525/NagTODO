# NagTODO 리팩토링 계획

## 핵심 원칙

리팩토링은 배포 안정성을 먼저 확보한 뒤 내부 품질을 개선하는 순서로 진행한다.

우선순위:

1. 배포를 막는 문제
2. 보안/데이터 무결성 문제
3. API 계약 정리
4. 테스트 기준 정리
5. 내부 코드 품질 개선

Backend, AI, Frontend는 서로 HTTP 계약에 의존한다. 따라서 계약이 바뀌는 작업은 반드시 의존 파트를 함께 수정한다.

---

## Wave 0. Baseline 확보

목표:

- 현재 상태를 고정해서 리팩토링 중 새로 생긴 실패를 구분할 수 있게 한다.
- 이 단계에서는 기능 코드를 수정하지 않는다.

작업:

```bash
cd backend
pytest
```

```bash
cd ai
pytest
```

```bash
cd frontend/front
npm run build
```

기록할 것:

- backend 테스트 통과/실패/xfail 개수
- ai 테스트 통과/실패/xfail 개수
- frontend build 성공 여부
- 이미 알려진 실패 목록

완료 기준:

- 현재 실패 상태가 문서화되어 있다.
- Wave 1 이후 실패가 새로 생긴 것인지 기존 실패인지 구분할 수 있다.
- 실행 결과 기록: `docs/wave0_baseline.md` (2026-05-14)

---

## Wave 1. 배포 차단 이슈 수정

목표:

- Railway/Vercel/Capacitor 배포 전에 반드시 정리해야 하는 문제를 먼저 해결한다.
- 순수 코드 취향 리팩토링은 이 단계에서 하지 않는다.

### 1-1. Frontend가 ai-server를 직접 호출하지 않게 수정

현재 문제:

- `frontend/front/src/hooks/useReport.jsx`가 `VITE_AI_URL || http://localhost:8000`으로 ai-server를 직접 호출한다.
- 배포 구조에서는 frontend가 backend만 호출해야 한다.
- OpenAI API key는 ai-server 내부에만 있어야 하며 frontend bundle에 노출되면 안 된다.

수정 방향:

- 리포트 생성 요청은 backend API로 보낸다.
- backend가 ai-server를 호출한다.
- frontend에서는 `VITE_AI_URL` 사용을 제거한다.

완료 기준:

- frontend 코드에서 ai-server URL을 직접 참조하지 않는다.
- Vercel/Android 앱은 `VITE_API_URL` 하나만 알면 된다.

### 1-2. Backend CORS 환경변수화

현재 문제:

- `backend/main.py`의 CORS origin이 localhost/ngrok 중심으로 하드코딩되어 있다.

수정 방향:

```env
CORS_ORIGINS=https://<vercel-domain>,http://localhost:5173,capacitor://localhost
```

- `settings.py`에서 `CORS_ORIGINS`를 읽는다.
- `main.py`는 환경변수 값을 split해서 `allow_origins`에 넣는다.
- `allow_credentials=True`를 유지한다.

완료 기준:

- Vercel production URL에서 cookie 인증 요청이 CORS 오류 없이 동작한다.
- Capacitor 앱 origin인 `capacitor://localhost`를 허용할 수 있다.

### 1-3. AI 서버 LLM 백엔드 교체 준비

이 작업은 배포 계획의 핵심과 연결된다.

주의:

- ai-server 자체를 제거하지 않는다.
- backend가 OpenAI API를 직접 호출하게 만들지 않는다.
- ai-server 내부의 LLM 호출 구현만 Ollama에서 OpenAI API로 바꾼다.

수정 방향:

- `ai/llm/openai_client.py` 추가
- `OpenAIClient.generate(prompt: str) -> str` 구현
- 기존 `OllamaClient.generate(prompt)`와 같은 상위 인터페이스 유지
- `ai/core/config.py`에 `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_TIMEOUT` 추가
- `ai/requirements.txt`에 `openai` 추가

완료 기준:

- 로컬에서 Ollama를 켜지 않아도 LLM 기능이 동작한다.
- OpenAI API key는 서버 환경변수로만 주입된다.

### 1-4. AI 서버 의존성 배포 가능하게 수정

현재 문제:

- `ai/requirements.txt`에 `faiss-gpu`가 있다.
- Railway 기본 환경에서는 GPU/CUDA를 기대하기 어렵다.

수정 방향:

```txt
faiss-cpu
```

완료 기준:

- Railway CPU 환경에서 ai-server dependency install이 가능하다.

---

## Wave 2. Backend 보안/데이터 무결성 수정

목표:

- 이미 테스트로 드러난 critical 문제를 먼저 고친다.
- API 응답 형식은 가능한 유지한다.

### 2-1. Todo 소유권 변경 방지

현재 문제:

- `PATCH /todos/{todo_id}`에서 `user_id` 변경으로 todo 소유자가 바뀔 수 있다.

수정 방향:

- todo 수정 요청에서 `user_id` 변경을 금지한다.
- 더 좋은 방향은 인증 사용자 기준으로 소유권을 검증하는 것이지만, 현재 API가 `user_id` 기반이면 우선 변경 금지만 적용한다.

완료 기준:

- `test_cannot_change_todo_owner`가 통과한다.
- 기존 todo 수정 기능은 유지된다.

### 2-2. Todo title 검증

현재 문제:

- 빈 제목과 공백 제목이 허용된다.
- 256자 초과 제목이 Pydantic 레벨에서 차단되지 않는다.

수정 방향:

- `TodoCreate`, `TodoUpdate` schema에서 title 검증 추가
- strip 후 빈 문자열 금지
- 최대 길이 255 제한

완료 기준:

- 빈 제목 생성/수정이 422를 반환한다.
- 공백 제목 생성/수정이 422를 반환한다.
- 256자 초과 제목이 422를 반환한다.

### 2-3. Todo enum 검증

현재 문제:

- `todo_status`, `visibility`가 Pydantic 레벨에서 명확히 검증되지 않는다.
- 잘못된 값이 DB 오류로 내려가거나 환경에 따라 저장될 수 있다.

수정 방향:

- schema에 Literal 또는 Enum 적용
- 허용 값 명시

예:

```python
todo_status: Literal["시작전", "진행중", "완료"]
visibility: Literal["친구공개", "비공개"]
```

완료 기준:

- 잘못된 `todo_status`가 422를 반환한다.
- 잘못된 `visibility`가 422를 반환한다.
- DB 제약 오류가 아니라 request validation 단계에서 막힌다.

### 2-4. Backend 테스트 정리

수정 후:

- 고쳐진 xfail 테스트는 xfail 제거
- 현재 구현 확인용 테스트는 제거하거나 새 기대값으로 변경

완료 기준:

```bash
cd backend
pytest
```

- critical xfail이 실제 통과 테스트로 전환된다.

---

## Wave 3. API 계약 정리

목표:

- Backend, AI, Frontend 사이의 HTTP 계약을 명확히 한다.
- 이후 리팩토링 중 응답 형식이 흔들리지 않게 한다.

정리할 계약:

- todo 생성 응답
- todo 수정 응답
- todo 삭제 응답
- 월간 통계 응답
- 리포트 생성 요청/응답
- AI 간섭 요청/응답
- AI 서버 실패 시 backend 응답 정책

현재 유지할 정책:

- todo 생성 시 AI 간섭 호출 실패는 todo 생성을 막지 않는다.
- 임베딩 수정/삭제 실패는 todo 수정/삭제를 막지 않는다.
- 리포트 생성은 AI 결과가 핵심이므로 실패 정책을 별도로 정한다.

문서화 위치:

- `docs/api_contract.md` 신규 작성 권장

완료 기준:

- frontend hook과 ai-server client가 같은 계약을 기준으로 동작한다.
- response shape가 테스트로 최소 검증된다.

---

## Wave 4. Backend 내부 리팩토링

목표:

- 기능과 API 계약을 유지하면서 내부 코드를 단순화한다.

대상:

- `backend/app/services/todo.py`
- `backend/app/services/ai_client.py`
- `backend/app/db/database.py`

작업:

- `services/todo.py`의 넓은 `except Exception`을 가능한 구체화
- DB rollback이 필요한 예외와 HTTPException을 분리
- `services/ai_client.py`의 timeout/fallback 정책을 함수별로 명확히 유지
- `db/database.py`의 session close/rollback 중복 try/except 단순화

주의:

- AI 서버 실패가 todo CRUD를 막지 않는 현재 정책은 유지한다.
- 예외 메시지를 바꿀 경우 테스트 기대값도 함께 수정한다.

완료 기준:

```bash
cd backend
pytest
```

- 기존 backend API 동작이 유지된다.

---

## Wave 5. AI 내부 리팩토링

목표:

- OpenAI 전환 후 ai-server 내부 구조를 정리한다.
- report/interference 파이프라인의 실패 지점을 명확히 한다.

대상:

- `ai/core/config.py`
- `ai/core/dependencies.py`
- `ai/llm/`
- `ai/interference/feedback.py`
- `ai/report/nodes/quality_check.py`
- `ai/report/nodes/llm_report.py`
- `ai/report/nodes/summarize_clusters.py`
- `ai/report/graph.py`

작업:

- `OllamaClient` 이름과 타입 힌트 제거
- LLM client 인터페이스 이름을 provider 중립적으로 정리
- `feedback.py`의 프롬프트 문자열 오류와 타입 의존성 정리
- `quality_check.py`의 품질 기준을 테스트 가능한 함수로 분리
- `report/graph.py`의 조건부 라우팅 함수를 별도 함수로 유지하되 테스트 추가
- OpenAI 응답이 빈 문자열이거나 실패할 때 fallback 정책 명확화

완료 기준:

```bash
cd ai
pytest
```

- Ollama 없이 테스트가 통과한다.
- LLM 호출부는 mock으로 테스트 가능하다.

---

## Wave 6. Frontend 내부 리팩토링

목표:

- Backend/API 계약이 안정된 뒤 hooks와 UI 코드를 정리한다.

대상:

- `frontend/front/src/utils/api.js`
- `frontend/front/src/hooks/*`
- `frontend/front/src/App.jsx`
- 주요 page/component

작업:

- `utils/api.js`의 ngrok 전용 헤더 제거 여부 결정
- `buildFileUrl`이 계속 단순 passthrough면 제거하거나 의미 있는 asset URL builder로 변경
- hooks의 에러 처리 방식을 통일
- `console.warn`만 하는 실패와 사용자에게 알려야 하는 실패를 구분
- `App.jsx`의 `ALERT_HOURS`를 컴포넌트 밖 상수 또는 별도 util로 분리
- 즉시 모드 테스트 주석 제거

완료 기준:

```bash
cd frontend/front
npm run build
```

수동 확인:

- 로그인
- todo CRUD
- 리포트 생성
- 간섭 팝업
- 배경/음악/마이페이지 주요 기능

---

## Wave 7. 배포 전 최종 검증

목표:

- 리팩토링 후 배포 계획과 충돌이 없는지 확인한다.

검증:

```bash
cd backend
pytest
```

```bash
cd ai
pytest
```

```bash
cd frontend/front
npm run build
```

확인할 것:

- frontend가 ai-server를 직접 호출하지 않음
- frontend bundle에 OpenAI API key 없음
- backend CORS가 환경변수로 관리됨
- ai-server가 Ollama 없이 동작함
- `faiss-cpu` 사용
- backend와 ai-server의 Railway start command가 배포 계획과 일치

완료 기준:

- `docs/deploy_plan.md`를 따라 배포 가능한 상태다.

---

## 전체 순서 요약

```text
Wave 0  Baseline 확보
Wave 1  배포 차단 이슈 수정
Wave 2  Backend 보안/데이터 무결성 수정
Wave 3  API 계약 정리
Wave 4  Backend 내부 리팩토링
Wave 5  AI 내부 리팩토링
Wave 6  Frontend 내부 리팩토링
Wave 7  배포 전 최종 검증
```

원칙:

- Wave 1~3은 배포 안정성 작업이다. 우선순위가 가장 높다.
- Wave 4~6은 내부 품질 개선이다. 배포 일정이 급하면 뒤로 미룰 수 있다.
- 각 Wave는 테스트와 수동 검증까지 끝난 뒤 다음 Wave로 넘어간다.
