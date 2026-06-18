"""MCP 서버 (코어 래퍼) — 순수 함수 4개를 표준 포트로 노출.

외부 노출 경로: 외부 Claude·다른 MCP 클라이언트가 같은 툴을 호출할 수 있다.
내부 그래프(graph.py)의 툴 디스패치와는 별개 경로 — 둘 다 같은 순수 함수를
호출만 한다(로직 중복 0, 설계 결정 2).

실행: python -m src.mcp_server   (stdio transport)
"""

from __future__ import annotations

from typing import Optional

from mcp.server.fastmcp import FastMCP

from src.tools import (
    get_transaction as _get_transaction,
    calc_fee as _calc_fee,
    issue_refund as _issue_refund,
)
from src.rag import search_policy as _search_policy

mcp = FastMCP("payment-guardrail")


@mcp.tool()
def get_transaction(transaction_id: str) -> dict:
    """[safe] 거래 단건 조회."""
    return _get_transaction(transaction_id)


@mcp.tool()
def calc_fee(amount: int, method: str = "card") -> dict:
    """[safe] 결제 수수료 계산(카드 2.5% / 포인트 0%)."""
    return _calc_fee(amount, method)


@mcp.tool()
def search_policy(query: str, k: int = 3) -> dict:
    """[safe] 결제 정책 문서 검색(RAG)."""
    return _search_policy(query, k)


@mcp.tool()
def issue_refund(transaction_id: str, amount: Optional[int] = None) -> dict:
    """[sensitive] 환불 실행. risk_gate 통과 후에만 호출해야 한다."""
    return _issue_refund(transaction_id, amount)


if __name__ == "__main__":
    mcp.run()
