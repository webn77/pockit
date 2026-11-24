"""견고한 평가 러너 — run_eval의 채점 로직을 재사용하되 항목별 예외 격리 + 재시도.

run_eval.main()은 항목 1건이라도 LLM이 빈/비정상 응답을 내면 전체가 중단된다.
본 러너는 항목별 try/except + 재시도(기본 3회)로 끝까지 완주하고, 실패 항목은
tool_ok=False / decision="ERROR" / gate_ok=False 로 정직하게 오답 집계한다.

실행: python data/eval/run_eval_robust.py --set validation [--retries 3]
"""
from __future__ import annotations
import argparse, sys, time
from src.core.eval.run_eval import _load, _mean, evaluate_item, ReportBuilder


def run_item(item, retries):
    last = None
    for attempt in range(retries):
        try:
            return evaluate_item(item)
        except Exception as e:  # noqa: BLE001 — 어떤 LLM 응답 오류든 격리
            last = e
            time.sleep(1.5 * (attempt + 1))
    return {
        "id": item["id"], "category": item["category"], "query": item["query"],
        "tool": None, "tool_ok": False, "expected_tool": item["expected_tool"],
        "decision": "ERROR", "gate_ok": False, "expected_gate": item["expected_gate"],
        "gate_reason": f"eval error: {last}", "ret_ok": None, "faith_ok": None,
        "latency": 0.0, "est_tokens": 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="validation", choices=["validation", "test"])
    ap.add_argument("--retries", type=int, default=3)
    args = ap.parse_args()

    items = _load(args.set)
    print(f"=== 평가 시작(robust): '{args.set}' {len(items)}건, retries={args.retries} ===")
    results, errors = [], 0
    for n, it in enumerate(items, 1):
        r = run_item(it, args.retries)
        if r["decision"] == "ERROR":
            errors += 1
        mark = "✓" if (r["tool_ok"] and r["gate_ok"]) else "✗"
        print(f"  [{mark}] #{r['id']:>3} {r['category']:<16} tool={r['tool']}({'o' if r['tool_ok'] else 'x'}) "
              f"gate={r['decision']}({'o' if r['gate_ok'] else 'x'})  ({n}/{len(items)})", flush=True)
        results.append(r)

    tool_acc = _mean([r["tool_ok"] for r in results])
    gate_acc = _mean([r["gate_ok"] for r in results])
    ret = [r["ret_ok"] for r in results if r["ret_ok"] is not None]
    ret_prec = _mean(ret) if ret else 0.0
    avg_latency = sum(r["latency"] for r in results) / len(results) if results else 0.0
    total_tokens = sum(r["est_tokens"] for r in results)
    metrics = {
        "total": len(results), "tool_acc": tool_acc, "gate_acc": gate_acc,
        "ret_prec": ret_prec, "avg_latency": avg_latency,
        "total_tokens": total_tokens, "avg_tokens": total_tokens / len(results) if results else 0.0,
    }
    print("\n=== 지표 ===")
    print(f"  데이터셋 개수            : {metrics['total']}건  (eval 오류 {errors}건)")
    print(f"  tool_selection_accuracy : {tool_acc:.1%}  ({sum(r['tool_ok'] for r in results)}/{len(results)})")
    print(f"  gate_judgment_accuracy  : {gate_acc:.1%}  ({sum(r['gate_ok'] for r in results)}/{len(results)})")
    if ret:
        print(f"  retrieval_precision@3   : {ret_prec:.1%}  ({sum(ret)}/{len(ret)})")
    report = ReportBuilder.generate_report(args.set, results, metrics)
    print(f"\n  ✓ 대시보드 리포트 생성 완료: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
