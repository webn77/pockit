"""Mock HR MCP Server — stdio 기반으로 Pockit의 JIT 토큰 전파를 검증하기 위한 가상 툴 서버."""
from __future__ import annotations

import sys
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP

# FastMCP 객체 생성
mcp = FastMCP("MockHRServer")

# 가상의 직원 급여 테이블 데이터
_PAYROLL_DB = {
    45601: {"name": "이동원", "salary": "7,000,000 KRW", "department": "AI 플랫폼"},
    45602: {"name": "김영희", "salary": "5,500,000 KRW", "department": "보안인프라"},
}

@mcp.tool()
def get_payroll_details(target_employee_id: int, auth_context: Dict[str, Any] = None) -> str:
    """
    [보안 검증 툴] 직원의 급여 정보를 조회합니다.
    Pockit의 JIT 권한 전파에 의해 주입된 auth_context를 검증합니다.
    """
    # 1. JIT Context 누락 여부 검사
    if not auth_context:
        return "보안 거부: JIT 권한 정보(auth_context)가 누락되었습니다."

    user_id = auth_context.get("user_id")
    role = auth_context.get("role")
    jwt = auth_context.get("jwt")

    # 2. JWT 토큰 무결성 검증 (Mock)
    if not jwt or "dummy_user_payload" not in jwt:
        return "보안 거부: 올바르지 않은 사용자 인증 서명(JWT)입니다."

    # 3. 권한 매핑 검증 (JIT RBAC)
    # 일반 'agent'는 본인의 사번 정보만 조회할 수 있으며, 타인의 정보 조회 시 차단
    if role == "agent" and user_id != target_employee_id:
        return f"보안 거부: 역할 '{role}'는 본인 사번({user_id}) 외 타인의 급여 정보를 조회할 수 없습니다."

    # 4. 데이터 쿼리 수행
    record = _PAYROLL_DB.get(target_employee_id)
    if not record:
        return f"정보 없음: 사번 {target_employee_id} 직원을 찾을 수 없습니다."

    return (
        f"[승인 완료] 사원명: {record['name']} | "
        f"부서: {record['department']} | "
        f"급여액: {record['salary']} (호출자: {user_id}/{role})"
    )

if __name__ == "__main__":
    # stdio 수송으로 동작하도록 mcp 구동
    mcp.run(transport="stdio")
