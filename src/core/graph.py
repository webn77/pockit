"""LangGraph 조립 (코어 척추).

흐름:
  START → retrieve(RAG 강제) → assistant(LLM 툴선택) → gate(결정론 판정)
        → ALLOW          → execute → respond → END
        → REVIEW/BLOCK   → human_review[interrupt] → 승인? execute : respond(거부) → END

게이트 thesis: LLM은 retrieve 근거를 받아 "어떤 툴+인자"만 고른다(assistant).
판정(gate)·중단(interrupt)·실행(execute)은 전부 LangGraph 안에서 결정론적으로.
"""

from __future__ import annotations

from typing import Any, Literal, Optional, TypedDict

from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from src.core.rag.retriever import search_policy
from src.core.gate.risk_gate import evaluate, GateDecision
from src.adapters.payment.tools.payment_tools import get_transaction, calc_fee, issue_refund
from src.core.llm_client import complete_json

# 툴 디스패치 — 순수 함수 1벌을 그대로 호출(로직 중복 없음)
TOOLS = {
    "get_transaction": lambda a: get_transaction(**a),
    "calc_fee": lambda a: calc_fee(**a),
    "issue_refund": lambda a: issue_refund(**a),
    "search_policy": lambda a: search_policy(**a),
}

TOOL_SPEC = """사용 가능한 툴:
- get_transaction(transaction_id): 거래 조회
- calc_fee(amount, method): 수수료 계산
- issue_refund(transaction_id, amount): 환불 실행 (민감 — 금액 필수)
- search_policy(query): 정책 검색"""


class State(TypedDict, total=False):
    query: str
    role: str
    retrieved: list[dict[str, Any]]
    selection: dict[str, Any]       # {tool, args}
    gate: dict[str, Any]            # GateDecision.to_dict()
    approved: Optional[bool]        # 사람 결정(재개 시 외부 주입)
    tool_result: dict[str, Any]
    answer: str


def retrieve(state: State) -> dict:
    """RAG 노드(강제) — 항상 정책 근거를 먼저 가져온다."""
    res = search_policy(state["query"], k=3)
    return {"retrieved": res.get("results", [])}


def assistant(state: State) -> dict:
    """LLM 노드 — 툴 1개를 structured selection.

    정책 근거는 일부러 주지 않는다: 주면 LLM이 self-gating(스스로 거절)해서
    게이트가 일하는 모습이 가려진다. 게이트 thesis = "LLM을 믿지 않는다".
    주입 모드(테스트): selection 이 이미 있으면 LLM 호출을 건너뛴다.
    """
    if state.get("selection"):
        return {"selection": state["selection"]}
    prompt = (
        "너는 결제 운영 어시스턴트다. 사용자 요청을 처리할 툴 1개를 골라라.\n\n"
        f"{TOOL_SPEC}\n\n"
        f"[요청] {state['query']}\n\n"
        "규칙: 요청에 거래ID·금액이 있으면 조회를 건너뛰고 목적 툴을 바로 골라라. "
        "환불 요청이면 issue_refund + transaction_id·amount. "
        "정책 위반 여부는 네가 판단하지 말고, 사용자 의도대로 툴만 선택하라.\n"
        'JSON만 출력: {"tool":"...","args":{...}}'
    )
    return {"selection": complete_json(prompt)}


def gate_node(state: State) -> dict:
    """risk_gate 판정 — LLM 없음. LLM 출력은 비결정론이라 tool 누락을 가드."""
    # 0) Destructive request pre-filtering
    query_lower = (state.get("query") or "").lower()
    if any(k in query_lower for k in ["삭제", "delete", "remove", "clear", "destroy"]):
        d = GateDecision("BLOCK", "보안 정책 위반: 파괴적이거나 권한 없는 리소스 변경 시도 감지", requires_human=True)
        return {"gate": d.to_dict()}

    sel = state.get("selection") or {}
    tool = sel.get("tool")
    if not tool:
        d = GateDecision("BLOCK", f"툴 선택 실패: {sel.get('reason', 'no tool')}", requires_human=True)
        return {"gate": d.to_dict()}
    d = evaluate(tool, sel.get("args", {}), state.get("role", "agent"))
    return {"gate": d.to_dict()}


def route_gate(state: State) -> Literal["execute", "human_review"]:
    return "execute" if state["gate"]["decision"] == "ALLOW" else "human_review"


def human_review(state: State) -> dict:
    """interrupt_before 가 이 노드 직전 그래프를 중단. 재개 시 통과만 한다."""
    return {}


def route_after_review(state: State) -> Literal["execute", "respond"]:
    return "execute" if state.get("approved") else "respond"


def execute(state: State) -> dict:
    sel = state["selection"]
    fn = TOOLS.get(sel["tool"])
    if fn is None:
        return {"tool_result": {"ok": False, "reason": f"unknown tool: {sel['tool']}"}}
    return {"tool_result": fn(sel.get("args", {}))}


def respond(state: State) -> dict:
    gate = state["gate"]
    sel = state.get("selection", {})
    # 답변 근거 = 실제 retrieved 청크(RAGAS faithfulness 채점 대상). gate.policy_refs와 구분.
    retrieved = state.get("retrieved", [])
    refs = ", ".join(f"{r['source']}·{r['section']}" for r in retrieved) or "-"
    suffix = f" (정책 근거: {refs})"

    if gate["decision"] != "ALLOW" and not state.get("approved"):
        return {"answer": f"[{gate['decision']}] 자동 처리하지 않았습니다. 사유: {gate['reason']}{suffix}"}

    result = state.get("tool_result", {})
    return {"answer": f"[처리완료] {sel.get('tool')} 실행 → {result}{suffix}"}


def build_graph():
    b = StateGraph(State)
    for name, fn in [
        ("retrieve", retrieve), ("assistant", assistant), ("gate", gate_node),
        ("human_review", human_review), ("execute", execute), ("respond", respond),
    ]:
        b.add_node(name, fn)

    b.add_edge(START, "retrieve")
    b.add_edge("retrieve", "assistant")
    b.add_edge("assistant", "gate")
    b.add_conditional_edges("gate", route_gate, {"execute": "execute", "human_review": "human_review"})
    b.add_conditional_edges("human_review", route_after_review, {"execute": "execute", "respond": "respond"})
    b.add_edge("execute", "respond")
    b.add_edge("respond", END)

    return b.compile(checkpointer=MemorySaver(), interrupt_before=["human_review"])
