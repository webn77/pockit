"""평가 하니스 (코어) — 골든셋으로 에이전트를 채점.

지표:
- tool_selection_accuracy : LLM이 고른 툴 == expected_tool (고유 지표)
- gate_judgment_accuracy  : 게이트 판정 == expected_gate (고유 지표 = 차별점)
- retrieval_precision@k   : 정답 정책섹션이 retrieved top-k에 포함 (RAGAS context precision 개념)
- faithfulness (옵션 --faith)

실행: python -m src.eval.run_eval [--faith]
"""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path

from src.core.graph import retrieve, assistant, gate_node
from src.core.llm_client import complete

_ROOT = Path(__file__).resolve().parents[3]
_EVAL_DIR = _ROOT / "data" / "eval"


class ReportBuilder:
    """평가 결과를 단일 독립형 정적 HTML 대시보드로 컴파일하고 저장하는 빌더."""
    @staticmethod
    def generate_report(eval_set: str, results: list[dict], metrics: dict) -> Path:
        template_path = Path(__file__).resolve().parent / "templates" / "dashboard.html"
        output_dir = _ROOT / "data" / "eval"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "report.html"

        if not template_path.exists():
            # Fallback
            template_path = Path(__file__).resolve().parent / "templates" / "dashboard.html"

        template_content = template_path.read_text(encoding="utf-8")

        gen_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html_rendered = template_content \
            .replace("{{GEN_DATE}}", gen_date) \
            .replace("{{EVAL_SET}}", eval_set) \
            .replace("{{RESULTS_JSON}}", json.dumps(results, ensure_ascii=False)) \
            .replace("{{METRICS_JSON}}", json.dumps(metrics, ensure_ascii=False))

        output_path.write_text(html_rendered, encoding="utf-8")
        return output_path


def _load(set_name: str) -> list[dict]:
    target_path = _EVAL_DIR / f"{set_name}.jsonl"
    if not target_path.exists():
        # Fallback to local golden.jsonl in core/eval/ for backward compatibility if data/eval/ is empty
        target_path = Path(__file__).parent / "golden.jsonl"
    return [json.loads(line) for line in target_path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
    import time
    start_time = time.time()

    st = {"query": item["query"], "role": item.get("role", "agent")}
    st.update(retrieve(st))
    st.update(assistant(st))
    st.update(gate_node(st))

    latency = time.time() - start_time
    
    # Estimate tokens: prompt template is approx 300 chars, selection dict is completion.
    prompt_chars = 300 + len(item["query"])
    completion_chars = len(str(st.get("selection", "")))
    est_tokens = int((prompt_chars + completion_chars) * 0.8)  # Korean/English average token ratio

    sel = st.get("selection") or {}
    tool = sel.get("tool")
    decision = st["gate"]["decision"]

    ret_ok = None
    if "expected_section" in item:
        secs = [r["section"] for r in st.get("retrieved", [])]
        ret_ok = any(item["expected_section"] in s for s in secs)

    faith_ok = None
    if with_faith and decision == "ALLOW" and tool in ("search_policy", "issue_refund"):
        from src.core.graph import respond, execute
        st.update(execute(st))
        st.update(respond(st))
        faith_ok = _judge_faithfulness(st.get("answer", ""), st.get("retrieved", []))

    return {
        "id": item["id"],
        "category": item["category"],
        "query": item["query"],
        "tool": tool,
        "tool_ok": tool == item["expected_tool"],
        "expected_tool": item["expected_tool"],
        "decision": decision,
        "gate_ok": decision == item["expected_gate"],
        "expected_gate": item["expected_gate"],
        "gate_reason": st["gate"].get("reason", ""),
        "ret_ok": ret_ok,
        "faith_ok": faith_ok,
        "latency": latency,
        "est_tokens": est_tokens,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="validation", choices=["validation", "test"], help="평가 대상 데이터셋 (validation 또는 test)")
    ap.add_argument("--faith", action="store_true", help="faithfulness LLM judge 포함(추가 호출)")
    args = ap.parse_args()

    print(f"=== 평가 시작: '{args.set}' 데이터셋 ===")
    items = _load(args.set)
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

    avg_latency = sum(r["latency"] for r in results) / len(results) if results else 0.0
    total_tokens = sum(r["est_tokens"] for r in results)
    avg_tokens = total_tokens / len(results) if results else 0.0

    metrics_dict = {
        "total": len(results),
        "tool_acc": tool_acc,
        "gate_acc": gate_acc,
        "ret_prec": ret_prec if ret else 0.0,
        "avg_latency": avg_latency,
        "total_tokens": total_tokens,
        "avg_tokens": avg_tokens,
    }

    print("\n=== 지표 ===")
    print(f"  데이터셋 개수            : {metrics_dict['total']}건")
    print(f"  tool_selection_accuracy : {metrics_dict['tool_acc']:.1%}  ({sum(r['tool_ok'] for r in results)}/{len(results)})")
    print(f"  gate_judgment_accuracy  : {metrics_dict['gate_acc']:.1%}  ({sum(r['gate_ok'] for r in results)}/{len(results)})")
    if ret:
        print(f"  retrieval_precision@3   : {metrics_dict['ret_prec']:.1%}  ({sum(ret)}/{len(ret)})")
    if faith:
        print(f"  faithfulness            : {_mean(faith):.1%}  ({sum(faith)}/{len(faith)})")
    elif args.faith:
        print(f"  faithfulness            : 측정할 수 있는 데이터가 없습니다.")

    # HTML Report Generation
    report_file = ReportBuilder.generate_report(args.set, results, metrics_dict)
    print(f"\n  ✓ 대시보드 리포트 생성 완료: {report_file}")


if __name__ == "__main__":
    main()
