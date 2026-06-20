"""risk_gate (코어 엔진) — LLM이 고른 툴 호출을 실행 전 결정론적으로 판정.

설계 thesis: LLM의 툴 선택과 실제 실행 사이의 게이트. **LLM 없음, 순수 규칙.**
출력은 ALLOW/REVIEW/BLOCK 명시 스키마 → eval(gate-judgment accuracy)이 채점.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field

class RiskGateConfig(BaseModel):
    safe_tools: set[str] = Field(default_factory=lambda: {"get_transaction", "calc_fee", "search_policy"})
    sensitive_tools: set[str] = Field(default_factory=lambda: {"issue_refund"})
    review_threshold: int = 1_000_000
    block_threshold: int = 1_500_000
    role_limits: dict[str, Optional[int]] = Field(default_factory=lambda: {"agent": 1_000_000, "manager": None})

    @classmethod
    def from_file(cls, path: Path | str) -> RiskGateConfig:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**data)
        except Exception:
            return cls()

# Default config loading path
_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "data" / "gate_config.json"
_DEFAULT_CONFIG = RiskGateConfig.from_file(_DEFAULT_CONFIG_PATH)

# For backward compatibility
SAFE_TOOLS = _DEFAULT_CONFIG.safe_tools
SENSITIVE_TOOLS = _DEFAULT_CONFIG.sensitive_tools
REVIEW_THRESHOLD = _DEFAULT_CONFIG.review_threshold
BLOCK_THRESHOLD = _DEFAULT_CONFIG.block_threshold
ROLE_LIMITS = _DEFAULT_CONFIG.role_limits

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


def evaluate(
    tool_name: str,
    args: dict[str, Any],
    role: str = "agent",
    config: Optional[RiskGateConfig] = None
) -> GateDecision:
    """툴 호출 1건을 판정. role 기본 = 일반 상담원."""
    cfg = config or _DEFAULT_CONFIG

    # 0) JIT RBAC Security Check: 비인가자(user)는 어떠한 툴 호출도 불가능하며 무조건 차단/검토
    if role == "user":
        return GateDecision(
            "REVIEW",
            "비인가 사용자(user)의 직접적인 도구 호출 시도 감지 - 보안 심사 필요",
            requires_human=True
        )

    # 1) safe 툴 → 통과
    if tool_name in cfg.safe_tools:
        return GateDecision("ALLOW", f"safe tool '{tool_name}' — 조회/계산은 통제 대상 아님")

    if tool_name not in cfg.sensitive_tools:
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
    if amount > cfg.block_threshold:
        return GateDecision(
            "BLOCK",
            f"{amount:,}원 > {cfg.block_threshold:,}원 — 환불 심사 위원회 별도 승인 필요",
            [f"{_POLICY} · 3. 금액 기준 승인 단계"],
            requires_human=True,
        )

    if amount >= cfg.review_threshold:
        return GateDecision(
            "REVIEW",
            f"{amount:,}원 ≥ {cfg.review_threshold:,}원 — 매니저 검토 후 승인 필요",
            [f"{_POLICY} · 3. 금액 기준 승인 단계"],
            requires_human=True,
        )

    # 3) 100만원 미만 → RBAC 확인
    limit = cfg.role_limits.get(role, 0)
    if limit is not None and amount >= limit:
        return GateDecision(
            "REVIEW",
            f"권한 초과 — '{role}'는 {limit:,}원 미만만 직접 실행 가능, 상위자 에스컬레이션",
            [f"{_POLICY} · 6. 권한 (RBAC)"],
            requires_human=True,
        )

    return GateDecision(
        "ALLOW",
        f"{amount:,}원 < {cfg.review_threshold:,}원 — '{role}' 권한 내 자동 승인",
        [f"{_POLICY} · 3. 금액 기준 승인 단계"],
    )
