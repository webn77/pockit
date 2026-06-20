# LLM 에이전트 가드레일/보안 프레임워크 벤치마킹

> 조사 기준: 2026년 6월

## 1. 프레임워크별 비교표

| 프레임워크 | Stars | 접근 방식 | RBAC | Threshold | HITL | MCP | RAG | Eval |
|---|---|---|---|---|---|---|---|---|
| **NVIDIA NeMo Guardrails** | ~5,600 | 혼합(Colang DSL+LLM) | ❌ | ⚠️ intent score | ❌ | ❌ | ⚠️ 필터링 | ❌ |
| **Guardrails AI** | ~9,000 | 혼합(rules+LLM judge) | ❌ | ✅ confidence | ❌ | ❌ | ❌ | ❌ |
| **Meta LlamaGuard** | ~2,000 | 순수 LLM (12B) | ❌ | ✅ safe/unsafe | ❌ | ❌ | ❌ | ✅ MLCommons |
| **Microsoft Presidio** | ~8,600 | 결정론(regex+NLP) | ❌ | ✅ recognizer score | ❌ | ❌ | ⚠️ 프리프로세서 | ❌ |
| **promptfoo** | ~22,200 | 혼합(정적+LLM공격) | ❌ | ✅ pass/fail | ❌ | ❌ | ✅ RAG eval | ✅ YAML |
| **LLM Guard** | ~2,500 | 혼합(15+스캐너) | ❌ | ✅ score | ❌ | ❌ | ❌ | ❌ |
| **poc-payment-agent** | - | **결정론(순수규칙)** | **✅** | **✅ 금액임계** | **✅** | **✅** | **✅ 강제** | **✅ 30건** |

---

## 2. 프레임워크별 상세

### NVIDIA NeMo Guardrails
- **핵심**: Colang v2.0 상태머신 + Input/Dialog/Retrieval/Execution/Output 5단계 레일
- **특화**: 대화 흐름 제어, 토픽 범위 제한, 챗봇 가드레일
- **한계**: Colang 학습 곡선 높음, RBAC/HITL 부재

### Guardrails AI
- **핵심**: Guardrails Hub 200+ 플러그인, PII 감지, 구조화 출력 강제
- **특화**: 출력 구조화, 입출력 validation
- **한계**: 오케스트레이션 없음, 점 방어 (파이프라인 전체 아님)

### Meta LlamaGuard (4세대)
- **핵심**: 12B 멀티모달 분류기, MLCommons S1-S14 해저드 분류
- **특화**: 콘텐츠 안전성 분류, 멀티모달 판정
- **한계**: 추론 비용 큼, LLM 자체가 비결정론

### Microsoft Presidio
- **핵심**: PII 분석(Analyzer) + 비식별화(Anonymizer), regex+NLP
- **특화**: PII/PHI 탐지·마스킹, GDPR·HIPAA
- **한계**: PII 전용, 오케스트레이션 없음

### promptfoo (OpenAI 인수)
- **핵심**: 50+ 공격 플러그인 레드팀, CI/CD 통합
- **특화**: 배포 전 취약점 스캔, 레드팀 자동화
- **한계**: **런타임 보호 아님** (사전 테스팅 전용)

---

## 3. RBAC + Threshold + HITL 조합 분석

**세 가지를 한 번에 다루는 프로젝트?**

| 요건 | NeMo | Guardrails AI | LlamaGuard | Presidio | promptfoo | **poc-payment-agent** |
|---|---|---|---|---|---|---|
| RBAC | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Threshold | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Human-in-loop | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| LangGraph 오케스트레이션 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| RAG 통합 | ⚠️ | ❌ | ❌ | ⚠️ | ✅ | ✅ |
| 평가셋 내장 | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| MCP 노출 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

> **결론: RBAC + Threshold + HITL을 동시에 구현한 오픈소스 스타터킷은 사실상 없다.**

---

## 4. MCP 보안 특화 프로젝트들

| 프로젝트 | 특징 |
|---|---|
| **GUARDRAIL** | MCP 생태계용 보안 프레임워크 (DLP·정책 기반 접근 제어) |
| **mcp-context-protector** (Trail of Bits) | Trust-on-first-use 핀닝, 툴 description 검증 |
| **MCP-guardrails** | 엔터프라이즈 보안 게이트웨이, DLP + 정책 접근 제어 |

**MCP 주요 위협 벡터**: 프롬프트 인젝션, 툴 poisoning, 히스토리 탈취  
**공통 권고**: 최소 권한, 입출력 검증, HITL 확인, OAuth 2.1 기반 인증

---

## 5. 포지셔닝 맵

```
                    [결정론 (Rule-based)]
                           │
              Presidio ●   │   ● poc-payment-agent ★
              (PII rule)   │   (RBAC+임계+HITL+RAG+평가 통합)
                           │
  [특화 도메인]─────────────┼─────────────[범용/이식 가능]
                           │
    LLM Guard ●    NeMo●   │   ● Guardrails AI
    (스캐너특화)  (대화특화) │   (범용 validator)
                           │
         LlamaGuard●       │   ● promptfoo
         (콘텐츠분류)       │   (범용 레드팀)
                           │
                    [LLM 기반]
```

**우리 포지션**: 결정론×범용 사분면 — 현재 공백 구역

---

## 6. 인접 생태계 (참고 도구)

| 도구 | 분류 | Stars |
|---|---|---|
| DeepEval | 평가 프레임워크 (50+ 지표) | ~7,000 |
| RAGAS | RAG 평가 | ~8,000 |
| Langfuse | 관측성/트레이싱 | - |
| Lakera Guard | 런타임 보호 (Cisco 인수) | 상용 |
