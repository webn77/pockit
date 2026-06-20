# ISSUE-002 — Phase 2: Pockit 코어 라이브러리 구조화 및 Mock 모드 구현

## 한 문장 정의
> `poc-payment-agent` 가드레일 엔진의 핵심 로직을 독립 라이브러리(`pockit`)로 모듈화하고, API Key가 없는 가벼운 로컬 개발 환경을 지원하기 위해 `MockLLMClient`를 구현한다.

## 메타
- **phase**: completed (완료)
- **created**: 2026-06-19
- **priority**: High
- **선행**: ISSUE-001 (Phase 1, 완료)

## Workflow Tasks
- [x] **Core / Adapter 물리적 디렉토리 분리** — `src/core/` 및 `src/adapters/` 격리 구조 구축 / artifact: -
- [x] **Mock LLM 스위처 구현 (`src/core/client.py`)** — API Key가 없는 로컬 환경 대응 / artifact: -
- [x] **LangGraph Core 연결 교체** — `src/core/graph.py` 코드 업데이트 / artifact: -
- [x] **로컬 Mock 데모 구동 검증** — `python -m src.run_demo --mock` 통과 확인 / artifact: -

## 가드레일 (스코프 보호)
- `ai-native-backoffice` production(apps/·src/) 소스코드는 절대 직접 수정하지 않음.
- 모든 어댑터 결합 테스트는 병렬 데모 모듈로만 수행함.

## 세션 로그
- 2026-06-19: 정찰 및 Phase 2 병렬 데모 방향(C) 확정.
- 2026-06-20: '포킷(pockit)'으로 프로젝트명 최종 확정. 패키징 및 라이브러리화 구조에 맞게 이슈 작업 범위 구체화 후 active 전환.
