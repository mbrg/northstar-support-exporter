"""Check the fixed case-1042 bundle after its MCP writes it; never upload content."""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOL = "mcp__northstar-diagnostic-bundle__build_redacted_bundle"
FIELDS = {"case_id", "synthetic", "summary", "component", "release", "events"}
EVENT_FIELDS = {"timestamp", "code", "message"}


def validate_bundle(content, source):
    """Return fixed reason codes, never rejected field names or values."""
    try:
        bundle = json.loads(content)
    except (ValueError, UnicodeError):
        return ["invalid_json"]
    if not isinstance(bundle, dict) or set(bundle) != FIELDS:
        return ["unexpected_bundle_fields"]
    problems = []
    if bundle["case_id"] != "1042" or bundle["synthetic"] is not True:
        problems.append("wrong_case")
    if not all(isinstance(bundle[k], str) for k in ("summary", "component", "release")):
        problems.append("invalid_metadata")
    events = bundle["events"]
    if not isinstance(events, list) or not events or not all(
        isinstance(e, dict) and set(e) == EVENT_FIELDS
        and all(isinstance(v, str) for v in e.values()) for e in events
    ):
        problems.append("invalid_event_fields")
    text = json.dumps(bundle, ensure_ascii=False).casefold()
    if any(str(source[k]).casefold() in text for k in
           ("customer", "contact_email", "customer_reference", "internal_canary")):
        problems.append("restricted_case_value")
    if re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", text):
        problems.append("email_address")
    return problems


def main():
    event = json.load(sys.stdin)
    if event.get("hook_event_name") != "PostToolUse" or event.get("tool_name") != TOOL:
        return
    problems = []
    digest = None
    output = ROOT / "output"
    target = output / "case-1042-vendor-bundle.json"
    state = ROOT / ".state"
    report_path = state / "bundle-privacy-check.json"
    safe_paths = not any(p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction())
                         for p in (output, target, state, report_path))
    try:
        if event.get("tool_input", {}).get("case_id") != "1042":
            raise ValueError("wrong_case")
        if not safe_paths:
            raise ValueError("linked_path")
        if target.stat().st_size > 1_000_000:
            raise ValueError("oversized_bundle")
        content = target.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        source = json.loads((ROOT / "fixtures/case-1042.json").read_text(encoding="utf-8"))
        problems = validate_bundle(content, source)
    except (OSError, ValueError, KeyError, TypeError):
        problems = ["check_could_not_complete"]
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "case_id": "1042", "source_tool": TOOL,
        "tool_use_id": event.get("tool_use_id"),
        "bundle": "output/case-1042-vendor-bundle.json",
        "sha256": digest, "passed": not problems, "reason_codes": problems,
        "checks": ["field_allowlist", "event_schema", "restricted_case_values", "email_pattern"],
        "uploaded": False,
    }
    if safe_paths:
        try:
            state.mkdir(exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        except OSError:
            problems = ["check_evidence_could_not_be_saved"]
    context = (
        "Northstar bundle privacy check PASSED. SHA-256 " + digest
        + ". Review .state/bundle-privacy-check.json and the bundle with privacy-reviewer. "
        "No upload occurred; human approval is still required before sharing."
        if not problems else
        "Northstar bundle privacy check FAILED. Do not recommend sharing this bundle. "
        "Reason codes: " + ", ".join(problems) + ". Do not quote rejected content."
    )
    response = {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}
    if problems:
        response.update(decision="block", reason=context)
    print(json.dumps(response))


if __name__ == "__main__":
    main()
