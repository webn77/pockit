# Pockit (포킷) 📦

> **기업용 LLM 에이전트를 위한 Just-In-Time(JIT) 보안 가드레일 및 오케스트레이션 엔진**
> 
> 본 프로젝트는 LLM 에이전트가 고위험 비즈니스 환경(금융, 의료, 법무 등)에서 오작동하거나 권한을 오남용하지 않도록 **결정론적 가드레일(Rule-based Gate)**과 **JIT 사용자 권한 전파(Multi-MCP 연결 제어)**를 결합하여 안전성을 물리적으로 보장하는 파이썬 라이브러리 엔진입니다.

---

## 💡 핵심 아키텍처 및 원칙

`pockit`은 자연어 이해(LLM)와 실제 도구 실행(Execution)의 권한 통제를 철저히 분리합니다.

* **비결정론적 Intent 파싱 (LLM)**: LLM은 오직 사용자의 요청에서 의도와 인자만 추출(Tool Selection)합니다. 가드레일 통제 및 승인 로직은 LLM의 프롬프트 제어나 자율 판단에 의존하지 않습니다.
* **결정론적 가드레일 통제 (Risk Gate)**: `gate_config.json` 설정을 기반으로 100% 안전성을 사전 검증하여 **ALLOW(허용)**, **REVIEW(심사대기-HITL 중단)**, **BLOCK(강제 차단)**을 판정합니다.
* **JIT 권한 전파 (Just-In-Time Security)**: 툴을 실행하는 찰나의 순간에 실제 로그인한 사용자의 신분증(JWT)을 하위 MCP(Model Context Protocol) 서버로 안전하게 전파하여 권한 도용을 방지합니다.

---

## 📂 프로젝트 폴더 구조

```text
pockit/
├── pyproject.toml              # 패키지 빌드 스펙 (pip install -e . 지원)
├── LICENSE                     # Apache 2.0 Open Source License
├── data/
│   ├── policies/               # RAG용 도메인 정책 문서 (.md)
│   ├── eval/                   # 골든셋 데이터셋 & 시각화 리포트 (report.html)
│   └── gate_config.json        # [외부주입] 가드레일 차단 임계값 & RBAC 설정
├── src/
│   ├── core/                   # ★ Pockit Core Engine (공통 독립 모듈)
│   │   ├── graph.py            # LangGraph 오케스트레이션 뼈대
│   │   ├── client/manager.py   # 다중 MCP 연결 및 JIT 권한 주입 제어
│   │   ├── gate/risk_gate.py   # RiskGateConfig 가드레일 판정 로직
│   │   ├── rag/retriever.py    # Chroma DB RAG 및 클라우드(OpenAI/Gemini) 임베딩 팩토리
│   │   └── eval/run_eval.py    # 평가셋 구동 및 Chart.js 리포트 빌더
│   └── adapters/               # ★ Domain Adapters (도메인 플러그인 영역)
│       └── payment/            # 결제 PoC 어댑터 예시 번들
└── tests/                      # pytest 자동화 테스트 수트
```

---

## ⚡ 빠른 시작 (Getting Started)

### 1. 패키지 설치
`pockit`은 독립적인 파이썬 라이브러리로 패키징되어 있어 로컬 가상환경에 즉시 라이브러리로 설치할 수 있습니다:
```bash
# Clone the repository
git clone https://github.com/webn77/pockit.git
cd pockit

# 가상환경 활성화 상태에서 개발자 편집 모드 설치
pip install -e ".[test]"
```

### 2. 가드레일 자가 진단 및 평가 실행
환경 설정이 정상인지 진단하고, 30개 시나리오 골든셋에 대해 정확도 및 지연 속도, 토큰 사용량을 평가합니다:
```bash
# 1. 시스템 자가 진단
python src/core/doctor.py

# 2. 골든셋 평가셋 채점 및 시각화 리포트 생성 (data/eval/report.html 생성)
MOCK_LLM=true python src/core/eval/run_eval.py
```
* 채점이 완료되면 `data/eval/report.html` 경로에 미려하게 디자인된 **Chart.js 기반 PoC 검증 보고서**가 생성됩니다.

### 3. pytest 자동화 테스트 구동
보안 매니저 및 JIT 권한 주입 로직의 회귀 테스트를 상시 실행합니다:
```bash
pytest tests/
```

---

## ⚙️ 타 프로젝트에 pockit 이식하기 (재사용 방법)
회사 내 다른 서비스(예: 백오피스봇, 사내 챗봇 등)에 `pockit` 가드레일을 적용하려면 아래 **3가지 단계**를 따라 연동합니다.

### 1단계: 패키지 추가
타 프로젝트의 가상환경 내에서 `pockit`이 위치한 경로를 통해 라이브러리를 설치합니다.
```bash
# 타 프로젝트 가상환경에서 실행
pip install -e /path/to/pockit
```

### 2단계: 가드레일 및 권한 모델 구성
설정 파일(`gate_config.json`)을 인젝션하고, 요청을 수행할 사용자의 세션 정보(`UserContext`)를 정의합니다.
```python
from pockit.core.gate.risk_gate import RiskGateConfig, evaluate
from pockit.core.client.manager import ConnectionManager, MCPServerConfig, UserContext

# 1. 가드레일 규칙 로드
config = RiskGateConfig.from_file("/path/to/gate_config.json")

# 2. 다운스트림 연동할 사내 MCP 등록
manager = ConnectionManager()
manager.register_server(MCPServerConfig(
    name="internal-hr-db",
    transport="stdio",
    command="python",
    args=["-m", "my_mcp_server"]
))

# 3. 로그인한 사용자의 JIT 사원증 Context 생성
user = UserContext(
    user_id=45601,
    email="dongwon@enterprise.com",
    role="agent",
    jwt_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
)
```

### 3단계: 도구(Tool) 호출 제어 및 실행
```python
# 1단계: 가드레일 사전 차단 평가 (AI 응답 신호등 판정)
decision = evaluate(
    tool_name="get_payroll_details", 
    args={"target_employee_id": 45601}, 
    role=user.role, 
    config=config
)

# 2단계: 승인(ALLOW)인 경우에만 다운스트림 MCP 호출 실행 (JIT 권한 자동 주입)
if decision.decision == "ALLOW":
    res = await manager.call_tool_securely(
        server_name="internal-hr-db",
        tool_name="get_payroll_details",
        arguments={"target_employee_id": 45601},
        user_context=user
    )
    print("실행 결과:", res.content[0].text)
elif decision.decision == "REVIEW":
    print("⏸ 사람의 승인이 필요하여 일시 중단되었습니다:", decision.reason)
else:
    print("❌ 가드레일이 요청을 강제 차단했습니다:", decision.reason)
```
