# ISSUE-001 — 고위험 도메인 LLM 가드레일 스타터킷 (결제 PoC로 시작)

## 한 문장 정의 (확정)
> **고위험 도메인에서 LLM 에이전트를 안전하게 운영하는 "가드레일 하네스".**
> 결제를 첫 예시로 동작 검증 → AT-17 이식으로 재사용 증명 → 검증된 코어를 오픈소스 스타터킷으로 공개.

## 메타
- **phase**: active
- **created**: 2026-06-19
- **started**: 2026-06-19
- **target end**: -
- **completed**: -
- **last updated**: 2026-06-19
- **priority**: High
- **owner**: 이동원
- **포트폴리오**: 바이브코딩 카테고리 / 신규 항목 AT-23 (상태: 실험중) / **별도 항목으로 등재 예정**

## 무엇을 만드나 (확정)

### 오픈하는 단위 = 가드레일 스타터킷 (결제 앱 아님)
| 코어 (재사용 · 그대로 이식·공개) | 갈아끼움 (도메인마다 교체) |
|---|---|
| LangGraph 그래프 골격 | 툴 정의 |
| risk_gate 엔진 (통제) | RAG 문서 (정책 코퍼스) |
| RAG 파이프라인 | 게이트 정책 (safe/sensitive 규칙) |
| 평가 하네스 | 평가 골든셋 |
| MCP 래퍼 | — |

결제는 **번들 예시(instantiation #1)**. 남들은 자기 툴·정책·평가셋만 갈아끼워 자기 도메인에 사용.

### 대상 사용자 / 가치 제안
- **대상**: 고위험 도메인(금융·의료·법무)에서 LLM 에이전트를 만드는 **개발자**
- **공백(실증)**: 벤치마킹한 레포 대부분이 데모/문서챗봇 → **통제(게이트)+정량평가를 같이 갖춘 스타터는 거의 없음**
- **가치**: "남들이 빼먹는 통제+평가를 기본 탑재한 스타터킷"

## 3단계 로드맵 (스코프 보호 — 첫 수는 안 바뀜)
| 단계 | 내용 | 산출물 |
|---|---|---|
| **Phase 1** | 결제 에이전트 flat하게 동작 + 평가표 | 동작하는 PoC + 지표표 |
| **Phase 2** | AT-17(`work/ai-native-backoffice`) 이식 → 코어/어댑터 경계 검증 | 재사용 증명 |
| **Phase 3** | 검증된 코어를 스타터킷으로 추출 → GitHub 오픈소스 공개 | public repo + README |

> ⚠️ 과설계 가드: 처음부터 범용 프레임워크로 짜지 않는다. 소비자가 결제 하나뿐일 때 추상화하면 경계를 틀린다. **Phase 1은 flat하게.** 코어 추출은 Phase 2가 경계를 증명한 뒤.

## 기술 매핑 (공고 6개 키워드)
| 기술 | 구현 | 막는 위험 |
|---|---|---|
| AI Agent | fetch_context→retrieve(RAG 노드 강제)→assistant→route(safe/sensitive)→tools 루프 | — |
| LangGraph | 위 그래프를 통제·재개·관찰 가능하게 (앱 내 라이브러리). interrupt_before로 민감 툴 직전 중단, MemorySaver로 재개 | LLM 폭주 |
| RAG | 정책 문서 Chroma 검색. **노드로 강제**(LLM 재량 아님) → 환불은 항상 정책 근거 | 환각 |
| Tool Calling | 순수 함수 4개: get_transaction·search_policy·calc_fee·issue_refund (실행은 코드). safe 3 / sensitive 1 | 계산 오류 |
| MCP | 같은 순수 함수 4개를 표준 포트로 노출 (외부 Claude도 호출) | — |
| 평가셋 | 골든 30건 + RAGAS(context precision·faithfulness) + 고유(툴선택·게이트판정 정확도). 게이트는 ALLOW/REVIEW/BLOCK 명시 출력 → 채점 가능 | "되는 줄 알았는데" |

### 설계 확정 (2026-06-19, 레퍼런스 분석 후)
- **그래프**: `START→fetch_context→retrieve(RAG 노드)→assistant→route→{safe_tools / [interrupt]sensitive_tools}→assistant→END`. ro-anderson 정답지에서 multi-agent 계층은 제거(단일 결제 도메인 = flat).
- **safe 툴**: get_transaction · search_policy · calc_fee / **sensitive 툴**: issue_refund (금액 임계·RBAC 결정론 규칙 + interrupt 게이트)
- **3대 확정**: (1) RAG=노드 강제 (2) 툴=순수함수 1벌→LangGraph+MCP 래퍼 (3) 게이트=ALLOW/REVIEW/BLOCK 명시 출력
- **버림**: Docker·compose·Poetry·vectorizer 서비스 분리 → 임베디드 Chroma + venv + flat .py
- **LLM = 구독 기반(2026-06-19 결정)**: API 키 대신 Claude 구독(`claude` CLI). `src/llm_client.py` 단일 seam(complete/complete_json). LLM은 "어떤 툴+인자" **structured selection JSON만** 반환 → 판정·실행은 LangGraph. (게이트가 LangGraph 안에 남음 = 공고 LangGraph 요구 충족). reuser는 seam 한 파일만 교체해 API로 전환. anthropic/langchain-anthropic 의존 제거.
- **assistant에 정책 안 줌(self-gating 방지)**: 정책을 LLM에 주면 LLM이 스스로 거절 → 게이트가 일하는 모습이 가려짐. LLM은 의도→툴만, 위반 판단은 코드 게이트가.
- **역할 분리 (명시)**: 게이트 = **임계값 기반 결정론**(금액·RBAC 하드코딩, RAG 텍스트 안 씀). RAG = **답변 근거 + eval(faithfulness) 채점 대상**(결정엔 안 씀). 즉 "항상 근거"는 *결정*이 아니라 *답변*에 대한 주장. respond는 gate.policy_refs가 아닌 실제 retrieved 청크를 인용해야 faithsfulness 채점이 유효.
- **e2e 테스트 원칙**: interrupt/resume 배선은 selection 주입으로 결정론 검증. 실제 LLM e2e는 해피패스 1건만(LLM 변덕에 회귀 테스트가 인질 잡히지 않게).

## Acceptance Criteria (Phase 1 기준) — ✅ 전부 충족
- [x] LangGraph 그래프 end-to-end 1회 정상 실행 (run_demo 3시나리오)
- [x] RAG 검색이 정책 문서에서 관련 청크 반환 (retrieval@3 80%)
- [x] 4개 툴 정상 호출 + MCP 서버로도 동일 호출 가능 (check_mcp 4/4)
- [x] risk_gate가 민감 툴을 REVIEW/BLOCK로 라우팅 (safe/sensitive 분리, 경계 9/9)
- [x] 평가셋 30건 측정 → README에 지표 결과표 기재 (tool 100%·gate 100%)
- [x] 코어/어댑터 경계(갈아끼움 4개)에 이름표만 부여 (README 재사용 표)
- [x] 포트폴리오 ai-tech.json에 AT-23(실험중) 등록

## 벤치마크 레퍼런스
- ro-anderson/multi-agent-rag-customer-support — safe/sensitive 툴 분리 + 체크포인터 재개 (핵심 정답지)
- pedarias/langgraph-rag-mcp — RAG를 MCP로 노출
- teddynote-lab/langgraph-mcp-agents — 한국어 ReAct+MCP 핸즈온
- LangSmith Evaluation — context precision · faithfulness 지표 표준

## Workflow Tasks
- [x] **레퍼런스 분석** — ro-anderson 구조 분석 → 설계 확정 / artifact: 이슈 "설계 확정" 섹션
- [x] **(P1) 스캐폴딩** — 디렉토리 + 합성 거래 CSV(15건) + 결제 툴 3개(순수함수, smoke test 9/9 PASS) / artifact: `src/tools/payment_tools.py`, `data/transactions.csv`
- [x] **(P1) RAG** — 정책문서 2종 + Chroma 인덱싱(10청크) + search_policy(다국어 임베딩). 베이스라인 검색 정밀도 한계는 평가셋이 정량화 예정 / artifact: `src/rag/retriever.py`, `data/policies/`
- [x] **(P1) 구독 LLM seam** — claude CLI 단발 호출, structured selection JSON 검증 / artifact: `src/llm_client.py`
- [x] **(P1) risk_gate** — 결정론 ALLOW/REVIEW/BLOCK + RBAC, 경계값 9/9 검증. 정책 §3·§6과 1:1 / artifact: `src/gate/risk_gate.py`
- [x] **(P1) LangGraph 조립** — retrieve(강제)+assistant+gate+interrupt+execute+respond. e2e 3시나리오 검증(ALLOW 실제LLM / REVIEW→승인재개 / BLOCK 거부, 후 2개 주입 결정론) / artifact: `src/graph.py`, `src/run_demo.py`
- [x] **(P1) MCP 서버** — FastMCP로 4툴 노출(얇은 래퍼, 로직 중복 0). stdio 클라이언트로 list+호출 4/4 검증 / artifact: `src/mcp_server.py`, `src/check_mcp.py`
- [x] **(P1) 평가셋** — golden 30건 + run_eval.py. tool 100% · gate 100% · retrieval@3 80%(#28 미스=임베딩 한계 정량화) · faithfulness judge 검증 / artifact: `src/eval/golden.jsonl`, `src/eval/run_eval.py`, README 지표표
- [x] **(P1) 포트폴리오 등록** — AT-23(바이브코딩·실험중) 추가, JSON 검증. 배포는 git push 대기 / artifact: `portfolio-dongwon-v2/data/ai-tech.json`
- [ ] **(P2) AT-17 이식** — 코어/어댑터 경계 검증 → 별도 후속 이슈 / artifact: -
- [ ] **(P3) 스타터킷 추출·공개** — public repo + README → 별도 후속 이슈 / artifact: -

## 관련 이슈
- (후속) Phase 2 — AT-17 이식 이슈 (`work/ai-native-backoffice`)
- (후속) Phase 3 — 스타터킷 오픈소스 공개 이슈

## 세션 로그
- 2026-06-19: 이슈 생성 → 정의 진화·확정. "결제 PoC"에서 "가드레일 스타터킷(결제=첫 예시)"으로 격상. 3단계 로드맵 확정(결제 동작→AT-17 이식→오픈소스).
- 2026-06-19: **Phase 1 전부 완료.** 레퍼런스 분석(ro-anderson) → 스캐폴딩+툴3 → RAG(다국어 임베딩) → 구독 LLM seam(API키 0) → risk_gate → LangGraph 조립 e2e → MCP 서버 → 평가 30건 → AT-23 등록. 지표: tool 100%·gate 100%·retrieval@3 80%(#28 임베딩 한계 정량화). AC 7/7 충족. 다음=Phase 2(AT-17 이식) 후속 이슈.
