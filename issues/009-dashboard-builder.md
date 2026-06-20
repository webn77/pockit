# ISSUE-009 — Phase 9: Pockit 로컬 정적 대시보드 및 리포트 빌더 구축

## 한 문장 정의
> 에이전트 평가셋 구동 결과 및 JIT 가드레일 차단 내역을 시각적으로 한눈에 파악할 수 있도록, 렌더링 엔진을 추가하여 예쁘고 직관적인 정적 HTML 대시보드 리포트 빌더를 개발한다.

## 메타
- **phase**: scoped (대기 중)
- **created**: 2026-06-20
- **priority**: Medium
- **선행**: ISSUE-005 (MCP 보안 연동)

## Workflow Tasks
- [ ] **대시보드 HTML 템플릿 설계** — 차트 및 스코어 보드를 포함한 세련된 모던 CSS 기반의 HTML 템플릿 작성 / artifact: `src/core/eval/templates/dashboard.html`
- [ ] **자동 리포트 빌더 모듈 구현** — `run_eval.py` 채점 완료 후 지표 데이터를 수집해 HTML 리포트로 출력하는 빌더 클래스 추가 / artifact: -
- [ ] **RAG 문서 기여도 시각화** — 각 문항 RAGAS retrieval precision 지표 및 context 노드 도달 히스토리 매핑 시각화 / artifact: -
- [ ] **E2E 대시보드 자동 갱신 테스트** — 평가 구동 후 HTML 리포트 생성 및 브라우저 열기 연동 검증 / artifact: -

## 가드레일 (스코프 보호)
- 외부 복잡한 DB나 서버 없이 더블 클릭만으로 브라우저에서 실행 가능한 정적 HTML 파일 구조로 설계한다.
