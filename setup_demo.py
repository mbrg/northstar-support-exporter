"""Issue a credential for this synthetic service only; never display it."""
import hashlib
import json
import secrets
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
secret_dir = ROOT / ".secrets"
secret_dir.mkdir(mode=0o700, exist_ok=True)
auth_file = secret_dir / "ticket-auth.json"
env_file = ROOT / ".env"
config_file = ROOT / ".mcp.json"
if any(path.exists() for path in (auth_file, env_file, config_file)):
    raise SystemExit("Setup already exists or is partial; inspect it before changing credentials/configuration")
token = secrets.token_urlsafe(32)
principal = "svc-support-reader"
auth_file.write_text(json.dumps({"principal": principal,
    "token_sha256": hashlib.sha256(token.encode()).hexdigest(),
    "expires_at": int(time.time()) + 7 * 86400, "scopes": ["case:1042:read"]}, indent=2))
env_file.write_text("NORTHSTAR_TICKET_API_TOKEN=" + token + "\n")
config_file.write_text(json.dumps({"mcpServers": {
    "northstar-tickets": {"type": "http", "url": "http://127.0.0.1:8765/mcp",
                          "headers": {"Authorization": "Bearer ${NORTHSTAR_TICKET_API_TOKEN}"}},
    "northstar-diagnostic-bundle": {"type": "stdio", "command": sys.executable,
        "args": [str(ROOT / "bundle_server.py"), "--username", principal],
        "env": {"NORTHSTAR_TICKET_API_TOKEN": "${NORTHSTAR_TICKET_API_TOKEN}"}}
}}, indent=2))
for path in (auth_file, env_file):
    path.chmod(0o600)
print("Created svc-support-reader, scoped to reading synthetic case 1042 for seven days.")
print("Created two project MCP configurations. Credential value was not printed.")
