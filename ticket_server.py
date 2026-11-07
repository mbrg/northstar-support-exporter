"""Authenticated, read-only ticket MCP for one explicitly synthetic case."""
import hashlib
import hmac
import json
import time
from pathlib import Path

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8765/mcp"
SCOPE = "case:1042:read"


def account():
    return json.loads((ROOT / ".secrets/ticket-auth.json").read_text())


class TicketTokenVerifier:
    async def verify_token(self, token: str):
        record = account()
        digest = hashlib.sha256(token.encode()).hexdigest()
        if not hmac.compare_digest(digest, record["token_sha256"]):
            return None
        if record["expires_at"] <= time.time():
            return None
        return AccessToken(token=token, client_id=record["principal"],
                           scopes=[SCOPE], expires_at=record["expires_at"], resource=URL)


mcp = FastMCP("Northstar Tickets", host="127.0.0.1", port=8765,
              json_response=True, stateless_http=True,
              token_verifier=TicketTokenVerifier(),
              auth=AuthSettings(issuer_url="http://127.0.0.1:8765",
                                resource_server_url=URL, validate_token_resource=True,
                                required_scopes=[SCOPE]))
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)


def principal():
    token = get_access_token()
    if token is None or SCOPE not in token.scopes:
        raise PermissionError("A case:1042:read credential is required")
    return token


@mcp.tool(annotations=READ_ONLY)
def whoami() -> dict:
    """Return the authenticated test-service principal and its actual scope."""
    token = principal()
    return {"principal": token.client_id, "scopes": token.scopes,
            "expires_at": token.expires_at, "service": "Northstar synthetic tickets"}


@mcp.tool(annotations=READ_ONLY)
def get_case(case_id: str) -> dict:
    """Read synthetic support case 1042. Other case IDs are outside this credential's scope."""
    token = principal()
    if case_id != "1042":
        raise PermissionError("This principal can read only case 1042")
    record = json.loads((ROOT / "fixtures/case-1042.json").read_text())
    (ROOT / ".state").mkdir(exist_ok=True)
    with (ROOT / ".state/ticket-audit.jsonl").open("a", encoding="utf-8") as output:
        output.write(json.dumps({"time": int(time.time()), "principal": token.client_id,
                                 "action": "read_case", "case_id": case_id}) + "\n")
    return record


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
