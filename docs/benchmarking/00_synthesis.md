# 00. 벤치마킹 종합 보고서 (Synthesis)

본 문서는 `governed-agent`의 시장 포지셔닝과 차별점, 기업용 AI 에이전트 PoC 도입 시 마주하는 과제들과 본 프로젝트의 해결책을 벤치마킹 분석을 기반으로 종합한 보고서입니다.

## 1. 경쟁 포지셔닝 맵

```
                    범용 (Generic)
                         ▲
                         │
         LangGraph ──────┼────── CrewAI
         (오케스트레이션)  │       (오케스트레이션)
                         │
LLM-기반 판정 ◄──────────┼──────────────► 결정론 판정
                         │                    ▲
         NeMo      wassim249                  │
         (safety미들웨어)  │           ★ governed-agent (우리 포지션)
                         │           "결정론적 게이트(Gate) +
        ro-anderson      │            RAG 강제 선행 +
        (RAG 고객지원)     │            정량적 평가셋 통합"
                         │
        Harvey AI, Clio  │
        (단일도메인       │
         수직통합)        │
                         ▼
                    도메인 특화 (Specialized)
```

**결론**: 범용 오케스트레이션 도구(LangGraph)와 LLM 판정 기반 가드레일(NeMo) 사이에서, 고위험 도메인을 위한 **"결정론적 규칙 게이트 + RAG 강제 + 정량적 평가 하네스"**의 조합은 시장의 완전한 공백 지대입니다.

---

## 2. 주요 경쟁자 비교표

| 프로젝트 | Stars | Gate 방식 | RBAC | RAG 강제 | Eval 내장 | 도메인 이식성 |
|---|---|---|---|---|---|---|
| langchain-ai/langgraph | 44.6k | ❌ | ❌ | ❌ | ❌ | ❌ (인프라 툴) |
| NVIDIA/NeMo-Guardrails | 6.1k | LLM 판정 | ❌ | ❌ | ❌ | 부분적 |
| wassim249/fastapi-langgraph | 수백 | ❌ | ❌ | ❌ | ✅ | ❌ (보일러플레이트) |
| ro-anderson/multi-agent-rag | 소규모 | Human-in-the-Loop (UX) | ❌ | ❌ | ❌ | ❌ |
| jamjet-labs/jamjet | 소규모 | YAML 정책 | 부분적 | ❌ | ❌ | 부분적 |
| **governed-agent (본 프로젝트)** | - | **결정론적 Python** | **✅** | **✅** | **✅** | **✅ (어댑터 구조)** |

---

## 3. 핵심 차별점 (Core Pillars)

1. **결정론적 Gate 분리**: LLM은 자연어 요청으로부터 '의도(Intent)'와 '파라미터'만 추출하고, 실제 승인/반려/검토 등의 비즈니스 로직(Gate)은 순수 결정론적 Python 코드로 실행합니다.
2. **RAG 노드 강제 선행**: 에이전트의 답변 생성 전에 반드시 RAG(기업 검색) 노드를 거치도록 Graph 구조를 강제하며, 이를 Ragas 기반의 Faithfulness 정량 평가와 연동합니다.
3. **정량 평가 하네스(Harness) 내장**: Golden Set 데이터(`golden.jsonl`)와 평가 실행 스크립트(`run_eval.py`)를 함께 동봉하여 코드가 바뀔 때마다 즉각 회귀 테스트가 가능합니다.
4. **Adapter 기반 4-Swap 설계**: Core 엔진은 그대로 유지한 채, `Tool 어댑터`, `정책 문서 어댑터`, `Gate 규칙 어댑터`, `Golden Set 평가 어댑터` 4개만 교체하면 어떤 고위험 도메인으로도 즉시 이식이 가능합니다.
5. **ALLOW / REVIEW / BLOCK 3-Tier 스키마**: 권한(RBAC) 및 송금액 등 임계값 규칙에 따라 즉시 차단(BLOCK), 관리자 승인 대기(REVIEW), 즉시 실행(ALLOW) 단계를 차단 조건 스키마로 명시하여 에이전트 오동작을 원천 봉쇄합니다.
