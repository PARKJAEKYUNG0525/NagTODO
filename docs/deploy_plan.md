# NagTODO 배포 계획

## 핵심 정리

이 계획은 **AI 서버 자체를 OpenAI API로 대체하는 계획이 아니다.**

Railway에는 기존처럼 `ai-server` FastAPI 서비스를 배포한다. 바뀌는 것은 AI 서버 내부에서 LLM 응답을 생성하던 부분이다.

```text
기존:
backend -> ai-server FastAPI -> Ollama local LLM

변경 후:
backend -> ai-server FastAPI -> OpenAI API
```

유지하는 것:

- `ai-server` FastAPI 앱
- 간섭/피드백 API
- 리포트 API
- 임베딩 모델
- FAISS 벡터 저장소
- backend와 ai-server의 분리 구조

바꾸는 것:

- `OllamaClient`가 호출하던 로컬 Ollama LLM
- `OLLAMA_*` 환경변수
- Ollama 전용 테스트

---

## 목표 아키텍처

```text
사용자 브라우저 / Android 앱
        |
        | HTTPS
        v
Vercel - React frontend
        |
        | HTTPS, VITE_API_URL
        v
Railway - backend FastAPI
        |
        | Railway private network
        +--> Railway MySQL
        |
        | Railway private network
        +--> Railway ai-server FastAPI
                 |
                 +--> OpenAI API  (LLM 응답 생성만 담당)
                 +--> Railway Volume /app/data  (FAISS index, metadata)
```

서비스 위치:

| 구성요소 | 배포 위치 |
|----------|-----------|
| frontend React 웹 | Vercel |
| backend FastAPI | Railway |
| ai-server FastAPI | Railway |
| MySQL | Railway MySQL |
| FAISS 파일 | Railway Volume |
| LLM | OpenAI API |

---

## Step 0. 배포 범위 확정

이번 1차 배포 목표:

- React 웹을 Vercel에 배포
- backend를 Railway에 배포
- ai-server를 Railway에 배포
- MySQL을 Railway MySQL로 이전
- ai-server 내부 LLM 호출만 Ollama에서 OpenAI API로 변경

이번 단계에서 제외:

- Play Store 배포
- Push notification / FCM
- 운영 수준의 Alembic 마이그레이션 체계 완성

완료 기준:

- 브라우저에서 회원가입, 로그인, todo CRUD, 리포트/간섭 기능이 동작한다.

---

## Step 1. 로컬 코드 정리

### 1-1. ai-server의 LLM 백엔드 교체

현재 상태:

- `ai/llm/ollama_client.py`
- `ai/core/config.py`의 `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT`
- `ai/core/dependencies.py`의 `get_ollama_client`
- 일부 리포트/간섭 코드가 `OllamaClient` 타입에 의존

수정 방향:

- `ai/llm/openai_client.py` 추가
- `OpenAIClient.generate(prompt: str) -> str` 인터페이스 유지
- 기존 `client.generate(prompt)`를 호출하는 상위 로직은 최대한 그대로 둔다.

환경변수:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30
```

수정 대상:

- `ai/requirements.txt`
- `ai/core/config.py`
- `ai/core/dependencies.py`
- `ai/interference/feedback.py`
- `ai/report/nodes/llm_report.py`
- `ai/report/nodes/summarize_clusters.py`
- `ai/tests/*` 중 Ollama를 직접 가정하는 테스트

주의:

- AI 서버를 없애면 안 된다.
- backend가 OpenAI API를 직접 호출하도록 바꾸는 것도 이번 계획이 아니다.
- OpenAI API key는 frontend나 Android 앱에 절대 넣지 않는다.

### 1-2. AI 서버 의존성 수정

현재 `ai/requirements.txt`에는 `faiss-gpu`가 있다. Railway 기본 환경에서는 GPU/CUDA를 기대하기 어렵다.

수정:

```txt
faiss-cpu
openai
```

주의:

- `sentence-transformers`는 첫 실행 때 모델 다운로드가 필요하다.
- Railway 첫 배포/첫 부팅이 느릴 수 있다.
- 메모리 부족이 나면 ai-server 플랜을 올리거나 임베딩 구조를 다시 검토한다.

### 1-3. backend CORS 설정 정리

현재 backend CORS는 localhost와 ngrok 중심이다. Vercel 도메인과 Capacitor origin을 환경변수로 관리하는 방식으로 바꾼다.

권장 환경변수:

```env
CORS_ORIGINS=https://<vercel-domain>,http://localhost:5173,capacitor://localhost
```

주의:

- `allow_credentials=True`를 쓰므로 운영에서 `allow_origins=["*"]`는 쓰지 않는다.
- Vercel preview URL까지 허용할지, production URL만 허용할지 결정한다.

### 1-4. 쿠키 설정 확인

현재 인증 쿠키는 `secure=True`, `samesite="none"`이다. Vercel과 Railway가 모두 HTTPS이면 방향은 맞다.

확인할 것:

- frontend axios의 `withCredentials: true` 유지
- backend CORS에 정확한 Vercel origin 추가
- 로컬 HTTP 개발에서는 secure cookie가 저장되지 않을 수 있으므로 개발/운영 설정 분리 고려

### 1-5. seed 정책 확인

현재 `backend/main.py`는 시작 시 다음을 실행한다.

- `Base.metadata.create_all`
- `run_all_seeds`

1차 배포에서는 이 방식으로 빠르게 검증할 수 있다. 다만 운영 방식으로는 Alembic migration이 더 적절하다.

반드시 설정할 환경변수:

```env
ADMIN_EMAIL=<admin email>
ADMIN_PW=<strong password>
```

설정하지 않으면 기본 관리자 비밀번호가 `admin1234`가 될 수 있다.

완료 기준:

- 로컬에서 backend와 ai-server가 실행된다.
- ai-server가 Ollama 없이 OpenAI API로 LLM 응답을 만든다.
- 기존 API 라우팅 구조는 유지된다.

---

## Step 2. 로컬 검증

backend 테스트:

```bash
cd backend
pytest
```

ai-server 테스트:

```bash
cd ai
pytest
```

프론트 빌드:

```bash
cd frontend/front
npm run build
```

수동 확인:

- backend 실행
- ai-server 실행
- frontend 실행
- 로그인
- todo CRUD
- 리포트/간섭 기능

완료 기준:

- 로컬에서 Ollama를 켜지 않아도 LLM 기능이 동작한다.
- frontend build가 성공한다.

---

## Step 3. Railway 프로젝트 생성

Railway 프로젝트 하나를 만들고, 그 안에 서비스 3개를 둔다.

```text
backend      FastAPI
ai-server    FastAPI
mysql        Railway MySQL
```

원칙:

- backend와 ai-server는 public domain이 필요할 수 있다.
- MySQL은 외부 공개하지 않는다.
- ai-server는 가능하면 public domain 없이 private network로만 backend에서 호출한다.

완료 기준:

- Railway 프로젝트에 `backend`, `ai-server`, `mysql`이 보인다.

---

## Step 4. Railway MySQL 설정

Railway에서 MySQL을 추가하면 다음 변수가 제공된다.

```env
MYSQL_HOST
MYSQL_PORT
MYSQL_USER
MYSQL_PASSWORD
MYSQL_DATABASE
```

backend 서비스에는 기존 코드의 설정명에 맞춰 매핑한다.

```env
DB_HOST=${{MySQL.MYSQL_HOST}}
DB_PORT=${{MySQL.MYSQL_PORT}}
DB_USER=${{MySQL.MYSQL_USER}}
DB_PASSWORD=${{MySQL.MYSQL_PASSWORD}}
DB_NAME=${{MySQL.MYSQL_DATABASE}}
```

완료 기준:

- backend 서비스에서 `DB_*` 환경변수를 모두 참조할 수 있다.

---

## Step 5. backend Railway 배포

Railway 설정:

```text
Root Directory: /
Install Command: pip install -r backend/requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT --app-dir backend
```

환경변수:

```env
SECRET_KEY=<32바이트 이상 랜덤 문자열>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE=900
REFRESH_TOKEN_EXPIRE=604800

DB_HOST=${{MySQL.MYSQL_HOST}}
DB_PORT=${{MySQL.MYSQL_PORT}}
DB_USER=${{MySQL.MYSQL_USER}}
DB_PASSWORD=${{MySQL.MYSQL_PASSWORD}}
DB_NAME=${{MySQL.MYSQL_DATABASE}}

AI_SERVER_URL=http://${{ai-server.RAILWAY_PRIVATE_DOMAIN}}:<ai-server-port>
CORS_ORIGINS=https://<vercel-domain>,http://localhost:5173,capacitor://localhost

ADMIN_EMAIL=<admin email>
ADMIN_PW=<strong password>
```

주의:

- `AI_SERVER_URL`은 Step 6에서 ai-server 배포 후 실제 private domain/port로 다시 맞춘다.
- 첫 배포 시 DB 테이블과 seed가 생성되는지 로그를 확인한다.

검증:

```text
GET https://<backend-public-domain>/docs
```

완료 기준:

- backend가 Railway에서 기동된다.
- `/docs` 접근이 된다.
- MySQL 연결 오류가 없다.

---

## Step 6. ai-server Railway 배포

Railway 설정:

```text
Root Directory: /
Install Command: pip install -r ai/requirements.txt
Start Command: uvicorn ai.main:app --host 0.0.0.0 --port $PORT
```

환경변수:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30

BACKEND_API_URL=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:<backend-port>
FAISS_INDEX_PATH=/app/data/index.faiss
FAISS_METADATA_PATH=/app/data/metadata.json
DEMO_MODE=false
```

Volume:

```text
Mount Path: /app/data
```

주의:

- `FAISS_INDEX_PATH`, `FAISS_METADATA_PATH`는 반드시 Volume 아래 경로여야 한다.
- 컨테이너 로컬 파일시스템에 저장하면 재배포 때 사라질 수 있다.
- 초기에는 FAISS 데이터가 비어 있을 수 있다. 기존 데이터가 필요하면 별도의 재색인 스크립트를 만들어야 한다.

검증:

```text
GET https://<ai-server-public-domain>/health
```

ai-server를 외부 공개하지 않는다면 Railway 내부에서 backend를 통해 간접 검증한다.

완료 기준:

- ai-server가 Railway에서 기동된다.
- `/health`가 정상 응답한다.
- OpenAI API key 오류가 없다.
- backend에서 ai-server 호출이 성공한다.

---

## Step 7. Vercel frontend 배포

Vercel 설정:

```text
Root Directory: frontend/front
Build Command: npm run build
Output Directory: dist
```

환경변수:

```env
VITE_API_URL=https://<backend-public-domain>.up.railway.app
```

현재 상태:

- `frontend/front/src/utils/api.js`는 이미 `import.meta.env.VITE_API_URL`을 사용한다.
- `ngrok-skip-browser-warning` 헤더는 운영에서는 불필요하다.
- `frontend/front/src/hooks/useReport.jsx`는 `VITE_AI_URL` 또는 localhost AI URL을 직접 사용한다.

권장 수정:

- 프론트가 ai-server를 직접 호출하지 않게 한다.
- 리포트/간섭 기능은 backend API를 통해 호출한다.
- ai-server는 backend 내부 의존 서비스로 둔다.

검증:

- 회원가입
- 로그인
- todo 생성/조회/수정/삭제
- 리포트 또는 간섭 기능
- 새로고침 후 로그인 유지

완료 기준:

- Vercel URL에서 주요 기능이 동작한다.
- 브라우저 콘솔에 CORS/Cookie 오류가 없다.

---

## Step 8. 배포 후 정리

필수 확인:

- Railway 로그에서 DB 연결 오류 없음
- Railway 로그에서 OpenAI API 인증 오류 없음
- Vercel 환경변수에 backend public URL 설정 완료
- backend CORS에 Vercel production URL 포함
- OpenAI API key가 frontend bundle에 포함되지 않음

운영 전 개선:

- `Base.metadata.create_all` 대신 Alembic migration 사용
- seed 실행을 앱 시작 로직에서 분리
- 관리자 계정 생성 방식을 별도 관리 명령으로 분리
- Railway Volume 백업 방식 정리
- MySQL 백업/복구 절차 정리
- OpenAI 사용량 상한/알림 설정

---

## Step 9. Capacitor Android 앱 준비

목표:

- React 웹 빌드를 Capacitor Android 앱으로 감싼다.
- Play Store 출시는 하지 않는다.
- 실기기 또는 에뮬레이터에서 설치/실행 가능한 APK까지 만든다.

전제 조건:

- Step 7까지 완료되어 Vercel 웹 배포가 안정적으로 동작한다.
- `VITE_API_URL`이 Railway backend public URL을 가리킨다.
- backend CORS에 `capacitor://localhost`가 포함되어 있다.
- Android Studio 설치
- JDK 17 이상 설치

주의:

- Android 앱 안에는 OpenAI API key를 넣지 않는다.
- Android 앱은 frontend만 포함한다.
- 앱은 backend API만 호출하고, ai-server는 직접 호출하지 않는 구조를 유지한다.

---

## Step 10. Capacitor 설치와 초기화

작업 위치:

```bash
cd frontend/front
```

패키지 설치:

```bash
npm install @capacitor/core @capacitor/cli @capacitor/android
```

Capacitor 초기화:

```bash
npx cap init NagTODO com.nagtodo.app --web-dir dist
```

Android 플랫폼 추가:

```bash
npx cap add android
```

완료 기준:

- `frontend/front/capacitor.config.*` 파일이 생성된다.
- `frontend/front/android/` 디렉터리가 생성된다.

---

## Step 11. Capacitor 설정 확인

`capacitor.config.ts` 또는 `capacitor.config.json`에서 다음 값을 확인한다.

```ts
import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.nagtodo.app',
  appName: 'NagTODO',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
  },
};

export default config;
```

확인할 것:

- `webDir`가 `dist`인지 확인
- `appId`는 나중에 바꾸기 번거로우므로 초기에 확정
- 앱 이름은 Android 런처에 보이는 이름이므로 `NagTODO`로 유지

완료 기준:

- Capacitor가 Vite 빌드 결과물인 `dist`를 Android 앱에 포함하도록 설정된다.

---

## Step 12. Android용 frontend 빌드

환경변수:

```env
VITE_API_URL=https://<backend-public-domain>.up.railway.app
```

빌드:

```bash
npm run build
```

Capacitor 동기화:

```bash
npx cap sync android
```

주의:

- frontend 코드에서 `localhost` API URL fallback에 기대면 안 된다.
- `VITE_API_URL`이 비어 있으면 Android 앱에서 backend를 찾지 못한다.
- `frontend/front/src/hooks/useReport.jsx`처럼 AI 서버를 직접 호출하는 코드가 있으면 Android에서도 문제가 된다. backend API를 통해 호출하도록 정리한다.

완료 기준:

- `dist/`가 생성된다.
- `android/` 프로젝트에 최신 웹 빌드가 반영된다.

---

## Step 13. Android Studio에서 실행

Android Studio 열기:

```bash
npx cap open android
```

Android Studio에서 할 일:

- Gradle sync 완료 확인
- 에뮬레이터 또는 USB 연결된 실기기 선택
- Run 실행

실기기 테스트 체크리스트:

- 앱 실행
- 회원가입
- 로그인
- todo 생성/조회/수정/삭제
- 리포트 또는 간섭 기능
- 앱 종료 후 재실행
- 로그인 쿠키 유지 여부 확인

문제가 자주 나는 지점:

- CORS에 `capacitor://localhost`가 빠짐
- `VITE_API_URL`이 잘못됨
- secure cookie가 Android WebView에서 기대와 다르게 동작함
- AI 기능이 frontend에서 ai-server를 직접 호출함

완료 기준:

- Android 앱에서 웹과 동일한 주요 플로우가 동작한다.

---

## Step 14. APK 생성

Play Store 출시는 제외하므로, 우선 디버그 APK 또는 내부 공유용 APK만 만든다.

디버그 APK 생성:

```bash
cd frontend/front/android
./gradlew assembleDebug
```

Windows PowerShell:

```powershell
cd frontend/front/android
.\gradlew.bat assembleDebug
```

생성 위치:

```text
frontend/front/android/app/build/outputs/apk/debug/app-debug.apk
```

주의:

- debug APK는 내부 테스트용이다.
- 외부 배포나 장기 사용 목적이면 release APK와 서명 키를 따로 관리해야 한다.
- Play Store 출시는 이번 계획에서 제외한다.

완료 기준:

- `app-debug.apk`가 생성된다.
- APK를 실기기에 설치해 실행할 수 있다.

---

## Step 15. Android 앱 배포 후 정리

확인할 것:

- backend CORS에 `capacitor://localhost` 포함
- Railway backend public URL이 HTTPS
- Android 앱 bundle에 OpenAI API key 없음
- Android 앱이 ai-server를 직접 호출하지 않음
- 앱 재실행 후 인증 상태 동작 확인

추후 개선:

- release APK 서명 키 관리
- 앱 아이콘/splash screen 정리
- Android 권한 최소화
- 앱 버전명/versionCode 관리
- 푸시 알림이 필요해질 때만 FCM 검토

---

## 비용 추정

개인 프로젝트 기준 대략:

| 항목 | 예상 |
|------|------|
| Railway backend + ai-server + MySQL + Volume | 약 $10~25/월 |
| Vercel 웹 | 무료 플랜 가능 |
| OpenAI API | 사용량 적으면 약 $1~10/월 |

주의:

- Railway는 서비스가 2개 이상이고 MySQL, Volume까지 쓰므로 무료처럼 운용하기 어렵다.
- `sentence-transformers`가 메모리를 꽤 사용하므로 낮은 플랜에서 메모리 부족이 날 수 있다.
- 비용은 트래픽보다 AI 호출 횟수, Railway 메모리/CPU 사용량, Volume 사용량에 따라 달라진다.
