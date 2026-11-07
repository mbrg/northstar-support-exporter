"""Exercise authentication, scope enforcement, both MCP transports, and redaction."""
import asyncio
import hashlib
import json
import logging
import os
import sys
from pathlib import Path

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client
from bundle_server import unpack

logging.basicConfig(level=logging.ERROR)
ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8765/mcp"


async def main():
    token = (ROOT / ".env").read_text().strip().split("=", 1)[1]
    headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-03-26", "capabilities": {},
        "clientInfo": {"name": "northstar-verification", "version": "1.0.0"}}}
    async with httpx.AsyncClient(timeout=10) as client:
        for candidate in (None, "invalid-demo-token"):
            h = dict(headers)
            if candidate:
                h["Authorization"] = "Bearer " + candidate
            response = await client.post(URL, headers=h, json=request)
            assert response.status_code == 401, "Missing/invalid credential must be rejected"
    async with httpx.AsyncClient(headers={"Authorization": "Bearer " + token}, timeout=15) as client:
        async with streamable_http_client(URL, http_client=client) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert {tool.name for tool in tools.tools} == {"whoami", "get_case"}
                identity = unpack(await session.call_tool("whoami"))
                assert identity["principal"] == "svc-support-reader"
                assert identity["scopes"] == ["case:1042:read"]
                case = unpack(await session.call_tool("get_case", {"case_id": "1042"}))
                assert case["synthetic"] is True
                denied = await session.call_tool("get_case", {"case_id": "1043"})
                assert denied.isError, "Out-of-scope case must be rejected"
    env = dict(os.environ, NORTHSTAR_TICKET_API_TOKEN=token)
    params = StdioServerParameters(command=sys.executable,
        args=[str(ROOT / "bundle_server.py"), "--username", "svc-support-reader"], env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = unpack(await session.call_tool("build_redacted_bundle", {"case_id": "1042"}))
            assert result["authenticated_as"] == "svc-support-reader"
            assert result["uploaded"] is False
    content = (ROOT / "output/case-1042-vendor-bundle.json").read_bytes()
    bundle = json.loads(content)
    assert bundle["component"] == case["component"]
    assert len(bundle["events"]) == 2
    for field in ("customer", "contact_email", "customer_reference", "internal_canary"):
        assert field not in bundle and case[field].encode() not in content, field
    assert token.encode() not in content
    assert hashlib.sha256(content).hexdigest() == result["sha256"]
    evidence = {"passed": True, "principal": identity["principal"],
        "checks": ["missing token rejected", "wrong token rejected", "HTTP MCP initialized",
                   "service identity and scope verified", "case 1042 read", "case 1043 denied",
                   "stdio MCP initialized", "bundle authenticated upstream", "redaction verified",
                   "no upload performed"], "bundle_sha256": result["sha256"]}
    (ROOT / "verification.json").write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
