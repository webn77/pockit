"""MCP 서버 검증 — stdio 클라이언트로 tool list + 호출 1회씩."""

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command="python", args=["-m", "src.mcp_server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("tools:", [t.name for t in tools.tools])

            for name, args in [
                ("get_transaction", {"transaction_id": "TX1001"}),
                ("calc_fee", {"amount": 12000, "method": "card"}),
                ("search_policy", {"query": "환불 가능 기간", "k": 1}),
                ("issue_refund", {"transaction_id": "TX1003", "amount": 8000}),
            ]:
                res = await session.call_tool(name, args)
                text = res.content[0].text if res.content else ""
                print(f"  {name}({args}) -> {text[:120]}")


if __name__ == "__main__":
    asyncio.run(main())
