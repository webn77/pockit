# ISSUE-003 — Phase 3: Validation / Test 데이터셋 이원화 및 RAGAS 평가 고도화

## 한 문장 정의
> 에이전트 프롬프트 오버피팅을 방지하기 위해 `validation.jsonl`과 `test.jsonl` 데이터셋을 이원화하고, 평가 스크립트(`run_eval.py`)가 셋옵션에 따라 세분화된 지표를 측정하도록 개선한다.

## 메타
- **phase**: completed (완료)
- **created**: 2026-06-20
- **priority**: Medium
- **선행**: ISSUE-002 (Pockit 라이브러리화)

## Workflow Tasks
- [x] **Validation 데이터셋 구축** — 기존 golden.jsonl 마이그레이션 및 30문항 규격 정리 / artifact: `data/eval/validation.jsonl`
- [x] **Test 데이터셋 구축** — 보안 공격 우려 및 엣지 케이스 30문항 블라인드 구축 / artifact: `data/eval/test.jsonl`
- [x] **평가 엔진 개선 (`run_eval.py`)** — `--set [validation|test]` 스위칭 및 시각화 리포트 출력 / artifact: -
- [x] **이원화 평가 검증** — 검증셋과 테스트셋의 개별 평가지표 동작 테스트 / artifact: -

## 가드레일 (스코프 보호)
- Test 데이터셋은 개발 과정 중 프롬프트 튜닝 시 들여다보지 않는 "블라인드 컴플라이언스 셋"으로 유지한다.
- RAGAS 평가 시 토큰 낭비를 유발하는 과도한 LLM Judge 호출 방지 옵션을 유지한다.
