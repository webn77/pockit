# ISSUE-008 — Phase 8: retriever.py 고성능 클라우드 임베딩 API 옵션화 및 Apache 2.0 라이선스 적용

## 한 문장 정의
> CPU 연산 지연을 줄이기 위해 외부 고성능 클라우드 임베딩 API(Gemini/OpenAI 등) 스위칭 기능을 RAG 인프라에 추가하고, 오픈소스 배포를 위해 Apache 2.0 라이선스를 적용한다.

## 메타
- **phase**: scoped (대기 중)
- **created**: 2026-06-20
- **priority**: Medium
- **선행**: ISSUE-007 (설정 분리)

## Workflow Tasks
- [ ] **RAG 클라우드 임베딩 어댑터 개발** — `retriever.py`에서 로컬 sentence-transformers 외에 API 호출 기반 임베딩을 지원하도록 개선 / artifact: -
- [ ] **Apache 2.0 LICENSE 파일 추가** — 레포지토리 루트에 공식 오픈소스 라이선스 파일 배치 / artifact: `LICENSE`
- [ ] **RAG 속도 벤치마크 테스트** — 로컬 CPU 임베딩과 클라우드 API 임베딩의 응답 속도 지연(Latency) 비교 분석 / artifact: -
