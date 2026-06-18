"""risk_gate (코어 엔진) — LLM이 고른 툴 호출을 실행 전 결정론적으로 판정.

설계 thesis: LLM의 툴 선택과 실제 실행 사이의 게이트. **LLM 없음, 순수 규칙.**
출력은 ALLOW/REVIEW/BLOCK 명시 스키마 → eval(gate-judgment accuracy)이 채점.

Phase 1은 flat: 임계값·RBAC를 여기 상수로. (Phase 2에서 어댑터로 추출)
임계값은 data/policies/refund_policy.md "3. 금액 기준 승인 단계"와 1:1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# safe 툴은 게이트 무조건 통과. sensitive 툴만 판정.
SAFE_TOOLS = {"get_transaction", "calc_fee", "search_policy"}
SENSITIVE_TOOLS = {"issue_refund"}

# 금액 임계 (refund_policy.md §3)
REVIEW_THRESHOLD = 1_000_000   # 이상 → REVIEW
BLOCK_THRESHOLD = 1_500_000    # 초과 → BLOCK

# RBAC (refund_policy.md §6): 일반 상담원은 100만원 미만만 직접 실행
ROLE_LIMITS = {
    "agent": 1_000_000,   # 미만까지 직접 실행
    "manager": None,      # 제한 없음
}

_POLICY = "refund_policy.md"


@dataclass
class GateDecision:
    decision: str                     # ALLOW | REVIEW | BLOCK
    reason: str
    policy_refs: list[str] = field(default_factory=list)
    requires_human: bool = False      # REVIEW/BLOCK → interrupt 트리거

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "reason": self.reason,
            "policy_refs": self.policy_refs,
            "requires_human": self.requires_human,
        }


def evaluate(tool_name: str, args: dict[str, Any], role: str = "agent") -> GateDecision:
    """툴 호출 1건을 판정. role 기본 = 일반 상담원."""
    # 1) safe 툴 → 통과
    if tool_name in SAFE_TOOLS:
        return GateDecision("ALLOW", f"safe tool '{tool_name}' — 조회/계산은 통제 대상 아님")

    if tool_name not in SENSITIVE_TOOLS:
        return GateDecision("BLOCK", f"unknown tool '{tool_name}'", requires_human=True)

    # 2) sensitive 툴(issue_refund) → 금액 판정
    amount = args.get("amount")
    if amount is None:
        # 금액 미지정 = 원금 전액 환불. 보수적으로 REVIEW(금액 확인 필요).
        return GateDecision(
            "REVIEW",
            "환불 금액 미지정 — 원금 전액 여부 확인 필요",
            [f"{_POLICY} · 4. 부분 환불"],
            requires_human=True,
        )

    # 금액 임계
    if amount > BLOCK_THRESHOLD:
        return GateDecision(
            "BLOCK",
            f"{amount:,}원 > {BLOCK_THRESHOLD:,}원 — 환불 심사 위원회 별도 승인 필요",
            [f"{_POLICY} · 3. 금액 기준 승인 단계"],
            requires_human=True,
        )

    if amount >= REVIEW_THRESHOLD:
        return GateDecision(
            "REVIEW",
            f"{amount:,}원 ≥ {REVIEW_THRESHOLD:,}원 — 매니저 검토 후 승인 필요",
            [f"{_POLICY} · 3. 금액 기준 승인 단계"],
            requires_human=True,
        )

    # 3) 100만원 미만 → RBAC 확인
    limit = ROLE_LIMITS.get(role, 0)
    if limit is not None and amount >= limit:
        return GateDecision(
            "REVIEW",
            f"권한 초과 — '{role}'는 {limit:,}원 미만만 직접 실행 가능, 상위자 에스컬레이션",
            [f"{_POLICY} · 6. 권한 (RBAC)"],
            requires_human=True,
        )

    return GateDecision(
        "ALLOW",
        f"{amount:,}원 < {REVIEW_THRESHOLD:,}원 — '{role}' 권한 내 자동 승인",
        [f"{_POLICY} · 3. 금액 기준 승인 단계"],
    )
