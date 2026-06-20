# Dashboard — 고위험 도메인 LLM 가드레일 스타터킷 (Pockit)

> 갱신: 2026-06-21

| 항목 | 값 |
|---|---|
| 활성 목표 | GOAL-1 |
| 활성 이슈 | none (전체 10개 이슈 완료) |
| 현재 Phase | Phase 10 ✅ 완료 |
| 다음 액션 | 사내 타 PoC 프로젝트 연동 지원 |

## 진행 현황 (Issues Status)
- [x] **ISSUE-001**: 가드레일 스타터킷 (결제 PoC로 시작) ✅
- [x] **ISSUE-002**: AT-17 이식 데모 ✅
- [x] **ISSUE-003**: 평가셋 이원화 (분리) ✅
- [x] **ISSUE-004**: 백오피스 연동 검증 ✅
- [x] **ISSUE-005**: 다중 MCP Client 연동 및 JIT 권한 전파 ✅
- [x] **ISSUE-006**: pockit 패키징 빌드 구조 도입 및 pytest 마이그레이션 ✅
- [x] **ISSUE-007**: 가드레일 하드코딩 설정(임계값/RBAC) 분리 및 RiskGateConfig 구축 ✅
- [x] **ISSUE-008**: retriever.py 클라우드 임베딩 API 옵션화 및 Apache 2.0 라이선스 적용 ✅
- [x] **ISSUE-009**: Pockit 로컬 정적 대시보드 및 리포트 빌더 구축 ✅
- [x] **ISSUE-010**: pockit 리포지토리 명칭 변경 및 데모 가이드 문서 고도화 ✅

## 지표 (Golden Set 30건 검증 결과)
| 지표 항목 | 목표치 | 현재 달성도 | 상태 |
|---|---|---|---|
| 툴 선택 정확도 (Tool Selection) | 100% | 100% | ✅ 패스 |
| 가드레일 판정 정확도 (Gate Judgment) | 100% | 100% | ✅ 패스 |
| RAG 검색 정확도 (Retrieval@3) | 80% | 80% | ✅ 패스 |
