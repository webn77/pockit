import pytest
from src.core.gate.risk_gate import evaluate, GateDecision, RiskGateConfig

def test_default_config_evaluation():
    # 기본 임계값: REVIEW 1,000,000 이상, BLOCK 1,500,000 초과
    # manager는 한도 제한 없음.
    res_allow = evaluate("issue_refund", {"amount": 500_000}, role="agent")
    assert res_allow.decision == "ALLOW"

    res_review = evaluate("issue_refund", {"amount": 1_200_000}, role="agent")
    assert res_review.decision == "REVIEW"

    res_block = evaluate("issue_refund", {"amount": 1_600_000}, role="agent")
    assert res_block.decision == "BLOCK"

    # agent는 1,000,000원 이상 시 금액 임계(100만원 이상 REVIEW)에 먼저 걸림
    res_rbac_review = evaluate("issue_refund", {"amount": 1_000_000}, role="agent")
    assert res_rbac_review.decision == "REVIEW"
    assert "매니저 검토" in res_rbac_review.reason


def test_custom_config_evaluation():
    # 커스텀 설정: 한도를 대폭 낮춘 경우
    custom_cfg = RiskGateConfig(
        safe_tools={"get_transaction", "calc_fee"},
        sensitive_tools={"issue_refund"},
        review_threshold=100_000,   # 10만원 이상 REVIEW
        block_threshold=300_000,    # 30만원 초과 BLOCK
        role_limits={"agent": 50_000, "manager": None}  # agent는 5만원 이상 시 권한 초과
    )

    # 1. safe_tools로 지정되지 않은 툴 검증
    res_policy = evaluate("search_policy", {"query": "test"}, role="manager", config=custom_cfg)
    assert res_policy.decision == "BLOCK"  # 커스텀 설정에서 safe_tools에서 제거됨 -> unknown tool

    # 2. agent 5만원 이상 환불 시도 -> 권한 초과 REVIEW
    res_agent = evaluate("issue_refund", {"amount": 80_000}, role="agent", config=custom_cfg)
    assert res_agent.decision == "REVIEW"
    assert "권한 초과" in res_agent.reason

    # 3. 30만원 초과 환불 시도 -> BLOCK
    res_block = evaluate("issue_refund", {"amount": 350_000}, role="manager", config=custom_cfg)
    assert res_block.decision == "BLOCK"
    assert "환불 심사 위원회" in res_block.reason
