import pytest
import sys
from pathlib import Path
from src.core.client.manager import ConnectionManager, MCPServerConfig, UserContext

@pytest.mark.asyncio
async def test_mcp_security_flow():
    # 1. 커넥션 매니저 초기화 및 Mock HR MCP 서버 등록
    manager = ConnectionManager()
    
    manager.register_server(MCPServerConfig(
        name="mock-hr-system",
        transport="stdio",
        command=sys.executable,
        args=["-m", "src.core.client.mock_servers"]
    ))

    # 2. 정상 호출 사용자 시나리오 (본인의 사번 45601 조회)
    user_self = UserContext(
        user_id=45601,
        email="dongwon@enterprise.com",
        role="agent",
        jwt_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy_user_payload"
    )
    
    try:
        res1 = await manager.call_tool_securely(
            server_name="mock-hr-system",
            tool_name="get_payroll_details",
            arguments={"target_employee_id": 45601},
            user_context=user_self
        )
        assert "보안 거부" not in res1.content[0].text, "정상 조회가 거부되었습니다."

        # 3. 우회 권한 공격 시나리오 (일반 agent가 김영희 사번 45602 조회 시도)
        res2 = await manager.call_tool_securely(
            server_name="mock-hr-system",
            tool_name="get_payroll_details",
            arguments={"target_employee_id": 45602},
            user_context=user_self
        )
        assert "보안 거부" in res2.content[0].text, "우회 조회가 허용되는 보안 리스크가 발생했습니다!"
    finally:
        await manager.shutdown()
