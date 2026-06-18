# Dashboard — 고위험 도메인 LLM 가드레일 스타터킷

> 갱신: 2026-06-19

| 항목 | 값 |
|---|---|
| 활성 목표 | GOAL-1 |
| 활성 이슈 | ISSUE-001 (Phase 1 완료) |
| 현재 Phase | Phase 1 ✅ 완료 → Phase 2 대기 |
| 다음 액션 | Phase 2 = AT-17 이식 후속 이슈 생성 |

## Phase 1 진행 현황 — ✅ 완료
- [x] 프로젝트 초기화 (git-files 모드)
- [x] GOAL-1 + Roadmap
- [x] 레퍼런스 분석 (ro-anderson) → 설계 확정
- [x] 스캐폴딩 + 합성 거래 15건 + 결제 툴 3개
- [x] RAG (Chroma + 다국어 임베딩 + search_policy)
- [x] 구독 LLM seam (llm_client.py, API 키 0)
- [x] risk_gate (ALLOW/REVIEW/BLOCK + RBAC, 경계 9/9)
- [x] LangGraph 조립 + e2e (interrupt/resume)
- [x] MCP 서버 (4툴 노출)
- [x] 평가셋 30건 (tool 100% · gate 100% · retrieval@3 80%)
- [x] 포트폴리오 AT-23 등록

## 지표 (golden 30건)
| tool_selection | gate_judgment | retrieval@3 |
|---|---|---|
| 100% | 100% | 80% |

## Phase 2/3 (후속)
- [ ] Phase 2 — AT-17 이식 (코어/어댑터 경계 검증)
- [ ] Phase 3 — 스타터킷 추출 → 오픈소스 공개
