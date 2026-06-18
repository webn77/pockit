# 고위험 도메인 LLM 가드레일 스타터킷

고위험 도메인에서 LLM 에이전트를 **안전하게** 운영하는 가드레일 하네스.
첫 예시 = **결제(payment) PoC**. 남들이 빼먹는 **통제(게이트) + 정량평가**를 기본 탑재.

> 상태: Phase 1 (결제 동작 검증) 진행 중 · 합성 데이터만 사용

## 구조

```
src/
├── tools/         # 순수 함수 1벌 (도메인 어댑터) — get_transaction·calc_fee·issue_refund
├── rag/           # Chroma 인덱싱·검색 = search_policy (코어)
├── gate/          # risk_gate 규칙 + ALLOW/REVIEW/BLOCK (코어)
├── graph.py       # LangGraph 조립 (코어)
├── mcp_server.py  # 툴 MCP 노출 (코어)
└── eval/          # golden.jsonl + run_eval.py (코어)
data/
└── transactions.csv  # 합성 거래 데이터
```

## 그래프 (결제)

```
START → fetch_context → retrieve(정책 RAG, 노드 강제)
      → assistant(LLM, 근거 + 툴 바인딩)
      → route: 전부 safe → safe_tools ─┐
                sensitive 끼면 →[게이트 interrupt]→ sensitive_tools ─┤→ assistant
                없음 → END
```

- **safe 툴**: `get_transaction` · `search_policy` · `calc_fee`
- **sensitive 툴**: `issue_refund` (금액 임계·RBAC 결정론 규칙 + interrupt 게이트)

## 핵심 기술 (채용 공고 6개 매핑)

AI Agent · LangGraph · RAG · Tool Calling · MCP · 평가 데이터셋 — 자세한 매핑은 `issues/001`.

## 평가 결과

**재현 가능(결정론 — 매번 동일):**

| 지표 | 결과 | 의미 |
|---|---|---|
| risk_gate 단위테스트 | **9/9** | 게이트 자체의 판정 정확도(금액 경계·RBAC). LLM 무관, 항상 재현 |
| retrieval_precision@3 | **80%** (4/5) | 정답 정책섹션이 top-3에 포함. #28 미스(유사 섹션 혼동) |

**LLM 의존(stochastic — 모델 변동 있음):**

| 지표 | 결과 | 비고 |
|---|---|---|
| tool_selection_accuracy | 30/30 | *2회 실행 기준. 단발 선택이라 run마다 변동 가능* |
| gate_judgment_accuracy | 30/30 | *tool selection 위에서 파생 — 위 단위 9/9가 진짜 게이트 근거* |
| faithfulness | judge 검증 | 구독 LLM judge(`--faith`). 참/거짓 주장 구분 확인 |

> retrieval 20% 미스(#28)는 임베딩 한계를 평가셋이 **정량화**한 것 — "기본 임베딩 → 평가로 약점 발견 → 개선"이 이 킷의 사용 패턴.
> tool/gate 30/30은 단일 모델·소표본 결과라 결정론 지표(9/9·80%)와 구분해 읽어야 한다.
> 실행: `python -m src.eval.run_eval [--faith]`

## 셋업

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# LLM = Claude 구독(claude CLI) 기반 — API 키 불필요. .env.example 참고.
python -m src.rag.retriever     # 정책 인덱싱(최초 1회)
python -m src.run_demo          # e2e 3시나리오
python -m src.eval.run_eval     # 평가 30건
```

## 재사용 (코어/어댑터)

| 코어 (그대로 이식) | 어댑터 (도메인마다 교체) |
|---|---|
| graph 골격 · risk_gate 엔진 · RAG 파이프라인 · 평가 하네스 · MCP 래퍼 | 툴 · 정책문서 · 게이트정책 · 평가 골든셋 |

결제는 instantiation #1. 자기 도메인은 어댑터 4개만 갈아끼운다.
