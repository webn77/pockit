# ISSUE-004 — Phase 4: `ai-native-backoffice` 통합 어댑터 설계 및 병렬 데모

## 한 문장 정의
> `ai-native-backoffice` 프로젝트의 데이터베이스 스키마(`payment.sql`) 및 CRUD 가드레일 요구사항을 어댑터 형태로 연동하여 코어 무수정 병렬 데모를 완성한다.

## 메타
- **phase**: scoped (대기 중)
- **created**: 2026-06-20
- **priority**: Medium
- **선행**: ISSUE-005 (MCP 보안 연동)

## Workflow Tasks
- [ ] **payment.sql 데이터베이스 툴 구현** — backoffice 어댑터 툴 구현 (`src/adapters/backoffice/tools.py`) / artifact: -
- [ ] **백오피스 CRUD 게이트 룰 구현** — 레코드 임계치 한도 및 JIT RBAC 정책 구현 (`src/adapters/backoffice/rules.py`) / artifact: -
- [ ] **병렬 시나리오 테스트 스크립트 작성** — 백오피스 통제 E2E 병렬 데모 구현 (`src/run_backoffice_demo.py`) / artifact: -
- [ ] **최종 통합 리뷰 및 가드레일 동작 증명** — Pockit 엔진이 실제 백오피스 요청을 안전하게 차단/리뷰하는지 입증 / artifact: -

## 가드레일 (스코프 보호)
- 실 가동 중인 백오피스(`ai-native-backoffice`) 코드는 절대 무수정으로 유지하고, 가상 DB 커넥션 및 어댑터 API 래퍼를 활용해 병렬 영역에서만 작동을 검증한다.
