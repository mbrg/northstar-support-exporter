"""Add one project hook while preserving existing settings, plugins and hooks."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
settings = ROOT / ".claude/settings.json"
state = ROOT / ".state"
if settings.is_symlink() or state.is_symlink():
    raise SystemExit("Settings and state must not be symlinks")
original = settings.read_bytes()
config = json.loads(original)
hook = {
    "matcher": "mcp__northstar-diagnostic-bundle__build_redacted_bundle",
    "hooks": [{
        "type": "command",
        "command": str(Path(sys.executable)),
        "args": [str(ROOT / "bundle_privacy_check.py")],
        "timeout": 10,
        "statusMessage": "Checking the vendor bundle for restricted case data",
    }],
}
entries = config.setdefault("hooks", {}).setdefault("PostToolUse", [])
if hook in entries:
    print("Bundle privacy hook already installed; settings unchanged.")
else:
    entries.append(hook)
    state.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = state / ("settings-before-privacy-" + stamp + ".json")
    with backup.open("xb") as stream:
        stream.write(original)
    settings.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print("Installed one PostToolUse bundle check. Existing settings preserved.")
