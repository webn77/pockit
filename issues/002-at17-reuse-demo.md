# ISSUE-002 — Phase 2: AT-17 도메인으로 코어 재사용 증명 (병렬 데모)

## 한 문장 정의
> Phase 1 코어(graph·gate·rag·eval)를 **그대로 두고**, 어댑터 4개만 AT-17의 결제 도메인(`payment.sql`)용으로 교체해 **재사용을 증명**한다. AT-17 production은 무수정(병렬 데모).

## 메타
- **phase**: scoped (코드 미착수)
- **created**: 2026-06-19
- **priority**: High
- **선행**: ISSUE-001 (Phase 1, 완료)
- **방향 확정**: **C (병렬 재사용 데모)** — 2026-06-19 이동원 승인

## 배경 — 왜 "코어 통째 이식"이 아닌가 (정찰 결과)
- AT-17(`work/ai-native-backoffice`)은 **가동 중 실서비스(v2.2.0)**. 빈 타깃이 아니다.
- AT-17엔 이미 자기 가드레일이 있다: `llm/`·`mcp/`·`rbac/`·`approvals/`·`audit/`·`redactor`.
- AT-17엔 **없는 것** = RAG · LangGraph식 그래프 통제 · 평가 하니스 (= 우리 PoC 차별 요소).
- **라이브 백엔드 = NestJS(TS, :8002)**. `src/`의 Python(FastAPI 66파일)은 비가동. → Python 코어 직접 이식 불가, 언어 경계 존재.
- 결론: "코어가 통째로 갈아끼워진다"는 과장. 정직한 주장 = **"RAG+평가+그래프 통제는 포터블하다, 게이트·RBAC 개념은 AT-17에 이미 다른 형태로 존재한다."**

## 방향 C — 병렬 재사용 데모 (확정)
- 우리 Python 코어를 **AT-17의 결제 스키마(`domain_schemas/payment.sql`)로 인스턴스화**.
- AT-17 production 코드(apps/api NestJS, src/ Python) **무수정**. 별도 위치에서 데모.
- 증명 포인트: 코어(graph·gate·rag·eval) diff 0, 어댑터 4개만 교체.

## 코어 / 어댑터 경계 (Phase 1에서 확정된 것)
| 코어 (불변 — 재사용) | 어댑터 (AT-17 결제 도메인용 교체) |
|---|---|
| `graph.py` (LangGraph 척추) | `tools/` (payment.sql 테이블 기반 툴) |
| `gate/risk_gate.py` (판정 엔진) | 게이트 정책 (AT-17 금액·RBAC 규칙) |
| `rag/retriever.py` (RAG 파이프라인) | 정책 문서 (AT-17 결제 정책 코퍼스) |
| `eval/run_eval.py` (평가 하니스) | 평가 골든셋 (AT-17 결제 시나리오) |
| `llm_client.py` (구독 seam) | — |

## Workflow Tasks
- [ ] **payment.sql 스키마 분석** — AT-17 결제 도메인 테이블·필드 파악 / artifact: -
- [ ] **코어/어댑터 경계 코드 표시** — Phase 1 코드에서 코어 vs 어댑터 명시(주석/디렉토리) / artifact: -
- [ ] **AT-17 결제 어댑터 작성** — payment.sql 기반 툴·정책문서·게이트정책·골든셋 / artifact: -
- [ ] **코어 불변 검증** — graph/gate/rag/eval 파일 diff 0 확인 / artifact: -
- [ ] **재사용 데모 + 평가** — AT-17 도메인에서 e2e 동작 + 지표 측정 / artifact: -

## 가드레일 (스코프 보호)
- AT-17 production(apps/·src/) **절대 무수정**. work 도메인 = 실서비스.
- 실제 코드 작업은 worktree isolation 또는 별도 모듈. in-place 금지.
- 파일 수정 전 TaskCreate 필수 (global CLAUDE.md).
- 코어 파일을 고쳐야 동작한다면 = 경계가 틀린 것. 코어 수정은 재사용 증명 실패 신호.

## 세션 로그
- 2026-06-19: 정찰 + Phase 2 정의 재결정. "코어 통째 이식" 깨짐(AT-17은 완성 실서비스+TS 라이브). 방향 C(병렬 데모) 확정. 실제 이식 코드는 새 세션에서 착수.
