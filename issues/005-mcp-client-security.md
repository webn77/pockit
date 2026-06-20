# ISSUE-005 — Phase 5: 사내 다중 MCP Client 연동 및 JIT 권한 보안 전파

## 한 문장 정의
> `pockit`이 MCP 클라이언트로서 Notion, 내부 DB 등 사내 다중 MCP 서버들을 동적으로 로드(stdio/SSE)하고, 호출 시점에 사용자 권한(JWT, Role)을 JIT(Just-In-Time) 방식으로 하위 서버에 주입하는 보안 프레임워크 모듈을 구현한다.

## 메타
- **phase**: completed (완료)
- **created**: 2026-06-20
- **priority**: Critical (최우선)
- **선행**: ISSUE-003 (평가셋 이원화)

## Workflow Tasks
- [x] **다중 MCP 연결 매니저 구현** — stdio 및 SSE transport 지원 및 지연 로딩 풀링 (`src/core/client/manager.py`) / artifact: -
- [x] **JIT 보안 토큰 주입 데코레이터 개발** — 툴 호출부 인자 밑단에 `_auth_context` JWT 자동 전파 / artifact: -
- [x] **다중 MCP 로컬 검증 Mock 서버 구현** — Notion 및 HR DB MCP 가상 서버 탑재 (`src/core/client/mock_servers.py`) / artifact: -
- [x] **테스트셋 보안 시나리오 검증** — 비인가 우회 호출 차단 및 JIT 전파 성공률 측정 / artifact: -

## 가드레일 (스코프 보호)
- downstream MCP 서버로 토큰을 보낼 때, Plain-text가 아닌 JWT 서명 검증이 가능하도록 프로토콜을 준수한다.
- stdio 연결 누수로 인한 OS 좀비 프로세스 방지를 위해 shutdown lifecycle 훅을 철저히 구현한다.
