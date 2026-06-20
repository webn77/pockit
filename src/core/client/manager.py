"""pockit MCP client manager — 다중 사내 MCP 서버 연동 및 JIT 토큰 전파."""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

# python-mcp SDK 임포트
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

logger = logging.getLogger("pockit.mcp_client")

@dataclass
class UserContext:
    """사용자 인증 컨텍스트 (JWT 토큰 및 역할 정보)"""
    user_id: int
    email: str
    role: str
    jwt_token: str  # Downstream MCP로 전달할 JWT 토큰

@dataclass
class MCPServerConfig:
    """MCP 서버 개별 접속 설정"""
    name: str
    transport: str  # "stdio" | "sse"
    command: Optional[str] = None
    args: Optional[list[str]] = None
    url: Optional[str] = None

class ConnectionManager:
    """다중 MCP 서버 접속 생명주기 및 JIT 보안 토큰 전파 관리 매니저"""
    
    def __init__(self):
        self.configs: Dict[str, MCPServerConfig] = {}
        self.active_sessions: Dict[str, ClientSession] = {}
        self._exit_stack: Dict[str, Tuple[Any, ClientSession]] = {}

    def register_server(self, config: MCPServerConfig):
        """MCP 서버 설정을 등록 (지연 로딩 적용)"""
        self.configs[config.name] = config
        logger.info(f"[pockit] 등록 완료: MCP Server '{config.name}' ({config.transport})")

    async def get_session(self, server_name: str) -> ClientSession:
        """등록된 서버 세션을 획득 (연결이 안 되어 있으면 지연 로딩으로 즉시 연결)"""
        if server_name in self.active_sessions:
            return self.active_sessions[server_name]

        if server_name not in self.configs:
            raise ValueError(f"등록되지 않은 MCP 서버입니다: '{server_name}'")

        config = self.configs[server_name]
        logger.info(f"[pockit] MCP 서버 연결 초기화 중: '{server_name}'...")

        if config.transport == "stdio":
            if not config.command:
                raise ValueError(f"stdio 수송에는 'command' 매개변수가 필수입니다: '{server_name}'")
            params = StdioServerParameters(command=config.command, args=config.args or [])
            
            # stdio 연결 생성
            ctx = stdio_client(params)
            read_stream, write_stream = await ctx.__aenter__()
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            await session.initialize()
            
            self._exit_stack[server_name] = (ctx, session)
            self.active_sessions[server_name] = session
            return session

        elif config.transport == "sse":
            if not config.url:
                raise ValueError(f"SSE 수송에는 'url' 매개변수가 필수입니다: '{server_name}'")
            
            # SSE 연결 생성
            ctx = sse_client(config.url)
            read_stream, write_stream = await ctx.__aenter__()
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            await session.initialize()
            
            self._exit_stack[server_name] = (ctx, session)
            self.active_sessions[server_name] = session
            return session

        else:
            raise NotImplementedError(f"지원하지 않는 transport 타입입니다: '{config.transport}'")

    async def call_tool_securely(
        self, 
        server_name: str, 
        tool_name: str, 
        arguments: Dict[str, Any], 
        user_context: UserContext
    ) -> Any:
        """
        [보안 핵심] downstream MCP 툴을 호출하기 전, 
        인자에 JIT _auth_context(JWT 포함)를 강제 주입하여 검증 가능하도록 전파.
        """
        session = await self.get_session(server_name)
        
        # JIT auth block 주입
        secure_arguments = {
            **arguments,
            "auth_context": {
                "user_id": user_context.user_id,
                "email": user_context.email,
                "role": user_context.role,
                "jwt": user_context.jwt_token
            }
        }
        
        logger.info(f"[pockit] 보안 호출 진행: {server_name}.{tool_name} on behalf of User {user_context.user_id}")
        return await session.call_tool(tool_name, secure_arguments)

    async def shutdown(self):
        """가동 중인 모든 서브프로세스 및 네트워크 연결 리소스 정리"""
        for name, (ctx, session) in list(self._exit_stack.items()):
            logger.info(f"[pockit] MCP 서버 연결 정리 중: '{name}'")
            try:
                await session.__aexit__(None, None, None)
                await ctx.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"[pockit] MCP 서버 {name} 종료 중 에러 발생: {e}")
        self.active_sessions.clear()
        self._exit_stack.clear()
