# ISSUE-006 — Phase 6: pockit 깃허브 공개 준비 - pyproject.toml 패키징 빌드 구조 도입 및 pytest 테스트 인프라 마이그레이션

## 한 문장 정의
> `pockit` 코어를 독립적으로 설치할 수 있도록 `pyproject.toml` 빌드 규격을 도입하고, 수동으로 실행하던 E2E 테스트 스크립트들을 `pytest` 규격의 자동화 테스트로 마이그레이션한다.

## 메타
- **phase**: scoped (대기 중)
- **created**: 2026-06-20
- **priority**: High
- **선행**: ISSUE-005 (MCP 보안 연동)

## Workflow Tasks
- [ ] **pyproject.toml 빌드 파일 정의** — hatchling 기반의 PEP-517 패키징 정의 및 의존성 명세 / artifact: `pyproject.toml`
- [ ] **pytest 테스트 스펙 이관** — `src/core/client/test_mcp_security.py`를 `tests/` 하위 pytest 규격으로 리팩토링 / artifact: `tests/test_mcp_security.py`
- [ ] **pip install 설치성 테스트** — 로컬 가상환경에서 `pip install -e .` 명령어를 통한 정상 모듈 임포트 검증 / artifact: -
