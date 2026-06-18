"""e2e 데모.

설계 원칙(advisor): interrupt/resume 배선은 LLM 변덕에 인질 잡히면 안 된다.
- case1 = 실제 LLM 해피패스("진짜 도는 것" 1건)
- case2/3 = selection 주입으로 interrupt/resume 배선을 결정론 검증
"""

from __future__ import annotations

from src.graph import build_graph


def run(graph, thread_id, query, role="agent", approve=None, selection=None):
    config = {"configurable": {"thread_id": thread_id}}
    init = {"query": query, "role": role}
    if selection is not None:
        init["selection"] = selection  # 주입 모드 → assistant 가 LLM 건너뜀
    mode = "주입" if selection is not None else "실제LLM"
    print(f"\n=== [{thread_id}] {query} (role={role}, {mode}) ===")

    state = graph.invoke(init, config)
    print(f"  selection : {state.get('selection')}")
    print(f"  gate      : {state['gate']['decision']} — {state['gate']['reason']}")

    snap = graph.get_state(config)
    if snap.next:  # interrupt (human_review 직전 중단)
        print(f"  ⏸  중단 (다음={snap.next}) → 사람 결정 필요")
        graph.update_state(config, {"approved": approve})
        state = graph.invoke(None, config)
        print(f"  ▶  재개: approved={approve}")

    print(f"  ANSWER    : {state.get('answer')}")
    return state


if __name__ == "__main__":
    g = build_graph()

    # 1) 실제 LLM 해피패스 — 소액 환불 자동 실행
    run(g, "case1-allow", "TX1003 거래 8000원 환불해줘", role="agent")

    # 2) REVIEW → 매니저 승인 재개 (배선 결정론)
    run(g, "case2-review", "TX1004 거래 120만원 환불해줘", role="agent", approve=True,
        selection={"tool": "issue_refund", "args": {"transaction_id": "TX1004", "amount": 1200000}})

    # 3) BLOCK → 거부 (배선 결정론)
    run(g, "case3-block", "TX1015 거래 200만원 환불해줘", role="agent", approve=False,
        selection={"tool": "issue_refund", "args": {"transaction_id": "TX1015", "amount": 2000000}})
