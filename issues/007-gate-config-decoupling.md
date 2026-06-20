# ISSUE-007 — Phase 7: 가드레일 하드코딩 설정(임계값/RBAC) 분리 및 외부 주입형 RiskGateConfig 구축

## 한 문장 정의
> `risk_gate.py` 내부에 하드코딩되어 있던 거래 제한 한도 금액 및 역할별 RBAC 임계값 상수들을 외부 설정(`config.json` 등)에서 동적으로 로드 및 주입할 수 있도록 개선한다.

## 메타
- **phase**: scoped (대기 중)
- **created**: 2026-06-20
- **priority**: High
- **선행**: ISSUE-006 (패키징 및 테스트 이관)

## Workflow Tasks
- [ ] **RiskGateConfig 설계** — 한도 및 역할 권한을 나타내는 pydantic 기반의 설정 모델 구축 / artifact: -
- [ ] **게이트 제어 로직 리팩토링** — `risk_gate.py`가 글로벌 상수가 아닌 주입받은 Config 인스턴스를 기준으로 ALLOW/REVIEW/BLOCK을 판정하도록 수정 / artifact: -
- [ ] **설정 주입 E2E 검증** — 다른 한도가 지정된 YAML/JSON 파일을 적용했을 때 게이트가 변경된 한도로 정상 판정하는지 검증 / artifact: -
