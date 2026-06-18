# Roadmap — 고위험 도메인 LLM 가드레일 스타터킷

> 갱신: 2026-06-19 · 감독 목표: [GOAL-1](goal.md)

## Now (진행 중 — Phase 1: 결제 PoC 동작)
| 항목 | 이슈 | 상태 |
|---|---|---|
| 가드레일 스타터킷 (결제 PoC로 시작) | ISSUE-001 | discovery |

**Phase 1 작업 순서** (ISSUE-001 Workflow Tasks)
1. 레퍼런스 분석 (ro-anderson) → 설계 확정
2. 스캐폴딩 + 합성 거래 CSV + 툴 4개
3. RAG (Chroma 인덱싱·검색)
4. LangGraph 그래프 조립 → e2e 동작
5. MCP 서버 노출
6. 평가셋 30건 + 지표표
7. 포트폴리오 AT-23 등록

## Next (다음 — Phase 2: 재사용 증명)
| 항목 | 비고 |
|---|---|
| AT-17(`work/ai-native-backoffice`) 이식 | 코어/어댑터 경계 검증. Phase 1 완료 후 후속 이슈 생성 |

## Later (이후 — Phase 3: 오픈소스)
| 항목 | 비고 |
|---|---|
| 스타터킷 추출 → GitHub public repo 공개 | Phase 2가 재사용 증명한 뒤. README + 결제 번들 예시 |
| 포트폴리오 AT-23 "운영중" 전환 | 공개 후 |

## 의존 관계
```
Phase 1 (결제 동작) ──검증──> Phase 2 (AT-17 이식) ──증명──> Phase 3 (오픈소스 공개)
```
각 단계는 앞 단계의 산출물이 게이트. 건너뛰지 않는다.
