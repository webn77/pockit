# LangGraph 기반 기업용 에이전트 벤치마킹

> 조사 기준: 2026년 6월

## 1. 주요 레포 비교표

| # | 레포 | Stars | 포지셔닝 | Gate | RBAC | RAG강제 | Eval | 도메인이식 |
|---|------|-------|---------|------|------|---------|------|----------|
| 1 | langchain-ai/langgraph | ~44,600 | 공식 코어 프레임워크 | ❌ | ❌ | ❌ | ❌ | ❌ (기반) |
| 2 | NVIDIA/NeMo-Guardrails | ~6,100 | 대화형 AI safety rail | LLM | ❌ | ❌ | ❌ | 부분 |
| 3 | wassim249/fastapi-langgraph | 수백 | FastAPI + LangGraph 프로덕션 인프라 | ❌ | ❌ | ❌ | 있음 | ❌ |
| 4 | ac12644/langgraph-starter-kit | 수백 | npx 한 줄 멀티에이전트 패턴 스캐폴딩 | ❌ | ❌ | ❌ | ❌ | ❌ |
| 5 | eng-mostafa-alrahal/clean-arch | ~28 | 클린 아키텍처 LangGraph | ❌ | ❌ | ❌ | ❌ | ❌ |
| 6 | RishabhMathur06/Guardrails | 소규모 | 금융 에이전트 3-레이어 defense-in-depth | LLM | ❌ | ❌ | ❌ | ❌ |
| 7 | FareedKhan-dev/agentic-guardrails | ~42 | 정책→Python 검증코드 자동 생성 | LLM | ❌ | ❌ | ❌ | ❌ |
| 8 | jamjet-labs/jamjet | 소규모 | Rust 기반 runtime safety control plane | YAML | 부분 | ❌ | ❌ | 부분 |
| 9 | ro-anderson/multi-agent-rag | 소규모 | 멀티에이전트 RAG 고객지원 (여행) | UX확인 | ❌ | ❌ | ❌ | ❌ |
| **우리** | **poc-payment-agent** | - | **결정론 gate + RAG강제 + 정량eval + 이식** | **결정론** | **✅** | **✅** | **✅** | **✅** |

---

## 2. ro-anderson/multi-agent-rag-customer-support 상세 분석

> 이 프로젝트를 설계 레퍼런스로 참고했으므로 가장 중요하게 비교.

### 구조
```
Primary Assistant (라우터)
  ├── Flight Booking Assistant → safe/sensitive tools
  ├── Car Rental Assistant → safe/sensitive tools
  ├── Hotel Booking Assistant → safe/sensitive tools
  └── Excursion Assistant → safe/sensitive tools
```

### 비교표

| 항목 | ro-anderson | poc-payment-agent |
|---|---|---|
| 에이전트 구조 | 4-specialist + Primary (복잡) | Single-domain linear graph (심플) |
| Gate 판정 | LLM/UX 확인 (사용자가 approve) | 결정론 rule engine (ALLOW/REVIEW/BLOCK) |
| RBAC | ❌ | ✅ role 기반 금액 임계 자동 판정 |
| RAG 역할 | 도메인 라우팅 + 정보 검색 | 정책 근거 강제 주입 (retrieve 노드 항상 선행) |
| 평가 | ❌ | ✅ golden.jsonl 기반 정량 eval 하네스 |
| 재사용성 | 여행 도메인 특화 | core/adapter 분리 (어댑터 4개만 교체) |

---

## 3. LangChain/LangGraph 공식 Auth 패턴

```python
@auth.authenticate
async def authenticate(headers: dict) -> str:
    token = headers.get("Authorization")
    user = verify_jwt(token)
    return user.identity

@auth.on.threads.read
async def can_read(ctx: Auth.types.AuthContext, thread_id: str):
    if ctx.user.id != get_thread_owner(thread_id):
        raise HTTPException(403)
```

- Thread/Assistant/Cron 3가지 리소스
- create/read/update/delete/search 5가지 액션 조합으로 RBAC/ABAC 구현

---

## 4. 생태계 트렌드 요약

```
고star (검증됨)
  langchain-ai/langgraph ★44.6k  ← 우리 기반
  NVIDIA/NeMo-Guardrails  ★6.1k  ← LLM safety 미들웨어 best-in-class

중간 (프로덕션 인프라 중심)
  wassim249/fastapi-langgraph  ← 인프라 완비, gate 없음
  ac12644/langgraph-starter-kit ← DX/scaffolding, gate 없음

소규모 (아이디어/컨셉)
  RishabhMathur06/Guardrails  ← defense-in-depth 아키텍처 레퍼런스
  FareedKhan-dev/agentic-guardrails ← policy→코드 자동생성 실험적
  jamjet-labs/jamjet          ← Rust 기반 runtime safety control plane
```

## 5. 우리 차별점

1. **결정론 Gate 분리** — LLM 판단과 실행 결정 완전 분리. `risk_gate.py`는 순수 Python 규칙 코드
2. **RAG 강제 선행** — retrieve가 항상 먼저. faithfulness 평가와 연결
3. **정량 평가 하네스 내장** — golden.jsonl + run_eval.py. 벤치마크 대상 중 유일
4. **Core/Adapter 4-swap 설계** — 도메인 이식 가능
5. **ALLOW/REVIEW/BLOCK 3-tier 명시 스키마** — 이 3-tier를 명시 스키마로 정의한 레포 없음

## 6. 우리가 없는 것 (개선 기회)

| 항목 | 참고 레포 | 우선순위 |
|---|---|---|
| 입력 guardrail (prompt injection, PII) | NeMo Guardrails, Llama Guard | Phase 3 |
| 감사 로그 / Audit Trail | jamjet-labs/jamjet | Phase 2 |
| OAuth2 / JWT Auth 통합 | langchain-ai/custom-auth | Phase 3 |
| 운영 인프라 (Prometheus, Grafana) | wassim249 | Phase 3 |
