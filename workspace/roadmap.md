# Roadmap — 고위험 도메인 LLM 가드레일 스타터킷 (Pockit)

> 갱신: 2026-06-20 · 감독 목표: [GOAL-1](goal.md)

## Completed (완료된 작업)
| 항목 | 이슈 | 상태 |
|---|---|---|
| 가드레일 스타터킷 (결제 PoC로 시작) | [ISSUE-001](../issues/001-payment-ops-agent-poc.md) | completed |
| AT-17 이식 데모 | [ISSUE-002](../issues/002-at17-reuse-demo.md) | completed |
| 평가셋 이원화 (분리) | [ISSUE-003](../issues/003-eval-split.md) | completed |
| 백오피스 연동 검증 | [ISSUE-004](../issues/004-backoffice-integration.md) | completed |
| 다중 MCP Client 연동 및 JIT 권한 전파 | [ISSUE-005](../issues/005-mcp-client-security.md) | completed |

## Now (진행 예정 — Phase 6: 패키징 및 테스트 자동화)
| 항목 | 이슈 | 상태 |
|---|---|---|
| pockit 패키징 빌드 구조 도입 및 pytest 마이그레이션 | [ISSUE-006](../issues/006-packaging-and-pytest.md) | scheduled (대기 중) |

## Next (다음 단계 — Phase 7 & 8: 가드레일 설정화 및 클라우드 임베딩)
| 항목 | 이슈 | 상태 |
|---|---|---|
| 가드레일 설정(임계값/RBAC) 분리 및 RiskGateConfig 구축 | [ISSUE-007](../issues/007-gate-config-decoupling.md) | scheduled (대기 중) |
| retriever.py 클라우드 임베딩 API 옵션화 및 Apache 2.0 적용 | [ISSUE-008](../issues/008-embedding-and-license.md) | scheduled (대기 중) |

## Later (이후 — Phase 9: 시각화 도구)
| 항목 | 이슈 | 상태 |
|---|---|---|
| Pockit 로컬 정적 대시보드 및 리포트 빌더 구축 | [ISSUE-009](../issues/009-dashboard-builder.md) | scheduled (대기 중) |

## 의존 관계
```
[ISSUE-001 ~ 005 완료] ──> ISSUE-006 (패키징/pytest) ──> ISSUE-007 (설정 분리) ──> ISSUE-008 (임베딩/라이선스) ──> ISSUE-009 (대시보드)
```
각 단계는 앞 단계의 산출물이 검증되어야 진행됩니다.
