# 03. Enterprise PoC to Production Workflow

기업에서 LLM 에이전트를 도입하고 PoC(Proof of Concept) 단계에서 실제 운영(Production) 단계로 넘어가려 할 때 직면하는 현실적인 과제와 이를 극복하기 위한 아키텍처 패턴을 정리합니다.

## 1. PoC → Production 실패 원인 (Gartner / McKinsey 분석)

대부분의 기업용 에이전트 프로젝트가 PoC 단계에 머무르고 실제 운영 환경으로 승인받지 못하는 원인은 기술력의 부족이 아니라 **Governance & Safety 격차** 때문입니다.

* **Auditable Trail 부재**: 에이전트가 어떤 생각 과정(Thought Process)을 거쳐 툴을 호출하고 답변했는지에 대해 보안팀/감사팀이 추적할 수 없는 블랙박스 구조.
* **비결정론적 행위의 위험성**: 금융 거래, 환자 처방전 조회, 기업 기밀 열람 등의 작업을 전적으로 LLM의 자율적 판단에 맡길 때 발생하는 오동작 리스크.
* **JIT (Just-In-Time) RBAC 부족**: 에이전트 실행 시 사용자의 권한이 에이전트 및 툴 호출 레이어까지 정확하게 전파 및 검증되지 않음.
* **정량적 회귀 평가 미비**: 프롬프트나 가드레일 룰을 수정했을 때, 기존 성능이 하락하는지 여부를 실시간으로 측정할 방법이 없음.

---

## 2. Enterprise Governance & Safety 패턴

본 프로젝트(`governed-agent`)는 이러한 문제를 해결하기 위해 다음과 같은 엔터프라이즈 설계 패턴을 구현합니다.

### A. Human-in-the-Loop (HITL) 3가지 모델
1. **HITL (Human-in-the-Loop / Active Approval)**:
   * 송금액 초과, 고위험 작업 등 특정 임계값 도달 시 에이전트 그래프가 실행을 멈추고(Interrupt) 관리자의 명시적 승인을 기다립니다.
2. **HOTL (Human-on-the-Loop / Passive Veto)**:
   * 에이전트가 작업을 실행하되 실시간으로 대시보드 등에 로깅하여 관리자가 즉시 취소(Veto)할 수 있게 합니다.
3. **HOOTL (Human-out-of-the-Loop / Full Autonomy)**:
   * 검증된 안전 영역 내에서 에이전트가 자율적으로 연속 작업을 수행합니다.

### B. Audit Trail & Explainability
* LangGraph의 State History와 Checkpointer를 이용하여 사용자의 프롬프트, LLM의 파라미터 추출 결과, 결정론적 Gate 통과 기록, 최종 툴 실행 결과를 타임스탬프와 함께 데이터베이스에 직렬화하여 기록합니다.

### C. JIT RBAC (Role-Based Access Control)
* 사용자 JWT 토큰에서 파싱된 역할(Role, 예: `junior`, `manager`)과 사원 ID를 툴 실행 직전의 Gate 노드로 전달하여 권한을 강제 검증합니다.

---

## 3. 산업군별 적용 아키텍처 패턴

| 산업군 | RAG 데이터 원천 | 주요 툴 (Tools) | 결정론적 Gate 규칙 예시 |
|---|---|---|---|
| **핀테크 / 결제** | 약관, 거래 한도 정책 | 송금 API, 계좌 조회, 취소 API | - 거래 금액 > 100만원: REVIEW<br>- 거래 금액 > 150만원: BLOCK<br>- 비인증 계좌 송금: BLOCK |
| **헬스테크 / 의료** | 진료 지침, 약물 DB | 환자 차방 조회, 처방전 발행 | - 마약류 처방: BLOCK<br>- 비급여 약물 처방: REVIEW<br>- 전문의가 아닌 경우 처방전 발행: BLOCK |
| **리걸테크 / 법무** | 사내 판례, 표준 계약서 | 표준 계약서 템플릿, 판례 검색 | - 소송 금액 > 1억: REVIEW<br>- NDA 외 계약 수정: REVIEW |
