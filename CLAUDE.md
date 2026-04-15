# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

**NagTODO** — AI 기반 잔소리꾼 TODO 앱. todo 생성 시 유사 task의 과거 성공률을 분석해 따끔한 피드백을 제공하고, 월간 회고 리포트를 생성한다.

## 디렉터리 구조

```
NagTODO/
├── backend/          # 백엔드 서버 (미구현)
├── frontend/         # 프론트엔드 (미구현)
└── ai/               # AI 서버 (FastAPI) ← 현재 개발 중
    ├── main.py
    ├── core/         # 설정 및 의존성 주입
    ├── embeddings/   # 임베딩 모델 + faiss 벡터 스토어
    ├── interference/ # 실시간 간섭 파이프라인
    ├── report/       # LangGraph 월간 리포트
    ├── llm/          # Ollama 클라이언트
    └── data/         # faiss 인덱스 + 메타데이터 (런타임 생성)
```

## 구현 순서 (단계별)

`ai/docs/` 하위에 각 단계별 상세 명세가 있다:

1. `step1_foundation.md` — config, dependencies, EmbeddingModel, OllamaClient
2. `step2_vector_store.md` — EmbeddingStore (faiss)
3. `step3_interference.md` — 실시간 간섭 파이프라인
4. `step4_langgraph_nodes.md` — LangGraph 노드 개별 구현
5. `step5_graph_assembly.md` — 그래프 조립 및 조건부 엣지
6. `step6_quality_check.md` — 품질 검증 노드
7. `step7_fastapi_router.md` — 라우터 연결 및 main.py 완성
8. `step8_integration_test.md` — 통합 테스트

## rules

Read ai/docs/TECHSPEC.md and ai/docs/ARCHITECTURE.md before conducting your work.
개발 후 디렉토리 구조가 변경될 시 반드시 ai/docs/ARCHITECTURE.md에 변경 내용 명시

1. 구현 작업 원칙
    - SOLID 원칙 사용
    - 핵심 로직은 TDD로 구현할 것
    - Clean Architecture를 사용해서 구현 : 책임과 관심사를 명확히 분리하여 구현
2. 코드 품질 원칙
    - 단순성 : 언제나 복잡한 솔루션보다 가장 단순한 솔루션을 우선시할 것
    - 중복 방지 : 코드 중복을 피하고, 가능한 기존 기능을 재사용할 것
    - 가드레일 : 테스트 외에는 개발이나 프로덕션 환경에서 모의 데이터를 사용하지 말 것
    - 효율성 : 명확성을 희생하지 않으면서 토큰 사용을 최소화하도록 출력을 최적화할 것
3. 언어
    - 문서와 주석 한국어로 작성
    - 기술적인 용어나 라이브러리 이름 등은 원문 유지
4. 문서화
    - 문서는 코드와 함께 업데이트
    - 복잡한 로직이나 알고리즘은 주석으로 설명할 것
