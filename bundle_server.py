"""Local stdio MCP. Reads one authorized ticket and writes a fixed, redacted bundle."""
import argparse
import hashlib
import json
import os
from pathlib import Path

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8765/mcp"
mcp = FastMCP("Northstar Diagnostic Bundle")
EXPECTED_PRINCIPAL = ""


def unpack(result):
    if result.isError:
        raise RuntimeError("Ticket service refused the operation")
    if result.structuredContent is not None:
        return result.structuredContent
    return json.loads(next(block.text for block in result.content if block.type == "text"))


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False,
                                     idempotentHint=True, openWorldHint=False))
async def build_redacted_bundle(case_id: str) -> dict:
    """Fetch case 1042 as the configured service user and write its vendor-safe diagnostic JSON."""
    if case_id != "1042":
        raise PermissionError("Only synthetic case 1042 is supported")
    token = os.environ.get("NORTHSTAR_TICKET_API_TOKEN", "")
    if not token:
        raise RuntimeError("NORTHSTAR_TICKET_API_TOKEN is missing; use start-demo.ps1")
    async with httpx.AsyncClient(headers={"Authorization": "Bearer " + token}, timeout=15) as client:
        async with streamable_http_client(URL, http_client=client) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                identity = unpack(await session.call_tool("whoami"))
                if identity["principal"] != EXPECTED_PRINCIPAL:
                    raise PermissionError("Credential identity does not match --username")
                case = unpack(await session.call_tool("get_case", {"case_id": case_id}))
    # Explicit projection: contact, customer reference, canary, and arbitrary added fields stay out.
    bundle = {key: case[key] for key in ("case_id", "synthetic", "summary", "component", "release")}
    bundle["events"] = [{key: event[key] for key in ("timestamp", "code", "message")}
                        for event in case["events"]]
    encoded = (json.dumps(bundle, indent=2) + "\n").encode()
    folder = ROOT / "output"
    folder.mkdir(exist_ok=True)
    target = folder / "case-1042-vendor-bundle.json"
    if folder.is_symlink() or target.is_symlink():
        raise ValueError("Output may not be a symlink")
    target.write_bytes(encoded)
    return {"case_id": case_id, "authenticated_as": identity["principal"],
            "path": str(target), "sha256": hashlib.sha256(encoded).hexdigest(),
            "redacted_fields": ["customer", "contact_email", "customer_reference", "internal_canary"],
            "uploaded": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    EXPECTED_PRINCIPAL = parser.parse_args().username
    mcp.run(transport="stdio")
