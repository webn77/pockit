"""평가 하니스 (코어) — 골든셋으로 에이전트를 채점.

지표:
- tool_selection_accuracy : LLM이 고른 툴 == expected_tool (고유 지표)
- gate_judgment_accuracy  : 게이트 판정 == expected_gate (고유 지표 = 차별점)
- retrieval_precision@k   : 정답 정책섹션이 retrieved top-k에 포함 (RAGAS context precision 개념)
- faithfulness (옵션 --faith): 답변이 retrieved 근거에 충실한가 (구독 LLM judge)

RAGAS 풀 라이브러리는 LLM judge가 API 키를 요구 → 구독 환경 맞춰 직접 구현.

실행: python -m src.eval.run_eval [--faith]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.graph import retrieve, assistant, gate_node
from src.llm_client import complete

_GOLDEN = Path(__file__).parent / "golden.jsonl"


def _load() -> list[dict]:
    return [json.loads(line) for line in _GOLDEN.read_text(encoding="utf-8").splitlines() if line.strip()]


def _mean(xs: list[bool]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _judge_faithfulness(answer: str, retrieved: list[dict]) -> bool:
    """구독 LLM judge — 답변이 retrieved 근거에 충실(미근거 주장 없음)한가."""
    ctx = "\n".join(f"- {r['section']}: {r['text'][:200]}" for r in retrieved)
    out = complete(
        "아래 [근거]만으로 [답변]의 사실 주장이 모두 뒷받침되는지 판정하라.\n"
        f"[근거]\n{ctx}\n\n[답변]\n{answer}\n\n"
        "근거로 뒷받침되면 yes, 근거에 없는 주장이 있으면 no. yes 또는 no만 출력."
    )
    return out.strip().lower().startswith("yes")


def evaluate_item(item: dict, with_faith: bool = False) -> dict:
    st = {"query": item["query"], "role": item.get("role", "agent")}
    st.update(retrieve(st))
    st.update(assistant(st))
    st.update(gate_node(st))

    sel = st.get("selection") or {}
    tool = sel.get("tool")
    decision = st["gate"]["decision"]

    ret_ok = None
    if "expected_section" in item:
        secs = [r["section"] for r in st.get("retrieved", [])]
        ret_ok = any(item["expected_section"] in s for s in secs)

    faith_ok = None
    if with_faith and decision == "ALLOW" and tool in ("search_policy", "issue_refund"):
        from src.graph import respond, execute
        st.update(execute(st))
        st.update(respond(st))
        faith_ok = _judge_faithfulness(st.get("answer", ""), st.get("retrieved", []))

    return {
        "id": item["id"], "category": item["category"],
        "tool": tool, "tool_ok": tool == item["expected_tool"],
        "decision": decision, "gate_ok": decision == item["expected_gate"],
        "ret_ok": ret_ok, "faith_ok": faith_ok,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--faith", action="store_true", help="faithfulness LLM judge 포함(추가 호출)")
    args = ap.parse_args()

    items = _load()
    results = []
    for it in items:
        r = evaluate_item(it, with_faith=args.faith)
        mark = "✓" if (r["tool_ok"] and r["gate_ok"]) else "✗"
        print(f"  [{mark}] #{r['id']:>2} {r['category']:<13} tool={r['tool']}({'o' if r['tool_ok'] else 'x'}) gate={r['decision']}({'o' if r['gate_ok'] else 'x'})")
        results.append(r)

    tool_acc = _mean([r["tool_ok"] for r in results])
    gate_acc = _mean([r["gate_ok"] for r in results])
    ret = [r["ret_ok"] for r in results if r["ret_ok"] is not None]
    ret_prec = _mean(ret)
    faith = [r["faith_ok"] for r in results if r["faith_ok"] is not None]

    print("\n=== 지표 ===")
    print(f"  tool_selection_accuracy : {tool_acc:.1%}  ({sum(r['tool_ok'] for r in results)}/{len(results)})")
    print(f"  gate_judgment_accuracy  : {gate_acc:.1%}  ({sum(r['gate_ok'] for r in results)}/{len(results)})")
    print(f"  retrieval_precision@3   : {ret_prec:.1%}  ({sum(ret)}/{len(ret)})")
    if faith:
        print(f"  faithfulness            : {_mean(faith):.1%}  ({sum(faith)}/{len(faith)})")
    else:
        print(f"  faithfulness            : (--faith 로 측정)")


if __name__ == "__main__":
    main()
