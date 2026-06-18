"""결제 도메인 툴 — 순수 함수 1벌.

설계 결정(2): 로직은 여기 순수 함수로만 둔다.
LangGraph @tool 래퍼와 MCP 래퍼는 이 함수들을 호출만 한다(로직 중복 금지).
실행은 항상 결정론적 코드 — LLM은 어떤 함수를 어떤 인자로 부를지만 정한다.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# data/transactions.csv (합성 데이터만 — 실 거래 금지)
_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "transactions.csv"

# 결제수단별 수수료율 (결정론 규칙)
_FEE_RATES = {
    "card": 0.025,   # 카드 2.5%
    "point": 0.0,    # 포인트 0%
}

# 정책: 환불 가능 기간(일). 실제로는 search_policy(RAG)가 근거를 제공,
# 여기서는 결정론 검증용 상수로 둔다.
_REFUND_WINDOW_DAYS = 90


def _load_transactions() -> dict[str, dict[str, Any]]:
    """CSV를 transaction_id → row dict 로 적재."""
    rows: dict[str, dict[str, Any]] = {}
    with _DATA_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["amount"] = int(row["amount"])
            rows[row["transaction_id"]] = row
    return rows


def get_transaction(transaction_id: str) -> dict[str, Any]:
    """[safe] 거래 단건 조회. 없으면 found=False."""
    tx = _load_transactions().get(transaction_id)
    if tx is None:
        return {"found": False, "transaction_id": transaction_id}
    return {"found": True, **tx}


def calc_fee(amount: int, method: str = "card") -> dict[str, Any]:
    """[safe] 결제 수수료 계산. 결정론."""
    rate = _FEE_RATES.get(method)
    if rate is None:
        return {"ok": False, "reason": f"unknown method: {method}"}
    fee = int(round(amount * rate))
    return {"ok": True, "amount": amount, "method": method, "rate": rate, "fee": fee, "net": amount - fee}


def issue_refund(transaction_id: str, amount: int | None = None, *, now: datetime | None = None) -> dict[str, Any]:
    """[sensitive] 환불 실행. risk_gate 통과 후에만 호출되어야 한다.

    결정론 검증: 거래 존재 / 상태 completed / 환불기간 이내 / 금액 한도.
    PoC라 실제 부작용 없이 처리 결과를 반환(상태 시뮬레이션).
    """
    tx = get_transaction(transaction_id)
    if not tx["found"]:
        return {"ok": False, "reason": "transaction not found"}
    if tx["status"] != "completed":
        return {"ok": False, "reason": f"not refundable: status={tx['status']}"}

    now = now or datetime.now(timezone.utc)
    created = datetime.fromisoformat(tx["created_at"]).replace(tzinfo=timezone.utc)
    age_days = (now - created).days
    if age_days > _REFUND_WINDOW_DAYS:
        return {"ok": False, "reason": f"out of refund window: {age_days}d > {_REFUND_WINDOW_DAYS}d"}

    refund_amount = amount if amount is not None else tx["amount"]
    if refund_amount > tx["amount"]:
        return {"ok": False, "reason": "refund exceeds original amount"}

    return {
        "ok": True,
        "transaction_id": transaction_id,
        "refunded_amount": refund_amount,
        "original_amount": tx["amount"],
        "new_status": "refunded",
    }


# 4번째 툴 search_policy(RAG)는 src/rag/retriever.py 에서 정의한다(다음 단계).
SAFE_TOOLS = ["get_transaction", "calc_fee", "search_policy"]
SENSITIVE_TOOLS = ["issue_refund"]
