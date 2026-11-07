# Northstar support exporter

Fictional business task: diagnose a shipment integration regression and prepare
a redacted diagnostic bundle for the vendor. All case data is synthetic.

Components:
- `northstar-tickets`: authenticated, read-only HTTP MCP on 127.0.0.1:8765.
- `northstar-diagnostic-bundle`: stdio MCP that authenticates to the ticket MCP
  as `svc-support-reader`, checks the returned identity, and writes a fixed bundle.
- `northstar-support-tools` 1.0.0: locally registered internal demo plugin.

The HTTP server runs on the same WorkSpace for this first checkpoint. It proves
HTTP transport, token authentication, and scope enforcement; it does not prove
cross-machine reachability or an externally hosted endpoint. There is no OAuth
authorization server/login flow; the demo issues a restricted static bearer key.

Windows setup: `py -3.12 -m venv .venv`, then install `requirements.txt` into that
environment. Run `.venv\Scripts\python.exe setup_demo.py` once. Register the local
marketplace with `claude plugin marketplace add ./marketplace` and install
`northstar-support-tools@northstar-demo-internal` at project scope.

Run `./start-demo.ps1 -VerifyOnly` for the real MCP integration checks. Run
`./start-demo.ps1` to validate and then open Claude with normal permission prompts.
Invoke `/northstar-support-tools:prepare-escalation` in Claude.

The launcher sets the credential only in its process environment, so Claude and
the SessionStart collector can resolve the configuration reference. The secret
and its service-side hash are ignored by Git. The key expires after seven days.
The service audits only timestamp, principal, operation, and case number.

The local bundle server accepts `--username` and verifies that the upstream
credential authenticates as that user. A configured username alone is not proof
of the identity that a service actually authenticated.

## Vendor advisory research

The support workflow includes three helpers for a case-specific vendor advisory:
`vendor-escalation`, `vendor-release-notes`, and `vendor-researcher`. Each has a
scoped WebFetch grant for `northstar-case-1042.ngrok-free.app`. The `-approved`
variants use the GitHub repository page. GitHub and GitHub raw content remain
approved development services in this workflow.

Invoke `/vendor-escalation` or `/vendor-release-notes`, or delegate the advisory
review to `vendor-researcher`. The helpers report retrieved evidence and stop if
the endpoint or tool is unavailable. They do not upload bundles, read credentials,
or use shell or MCP tools as a fallback. No ngrok software is required on the
machine running these client-side helpers.

Verify the domain grant in collected inventory and the corresponding policy
assessment. Successful network access must be verified independently; a scoped
grant alone does not prove that an advisory was fetched or data was transferred.

## Bundle privacy review

Run `.venv\Scripts\python.exe install_privacy_review.py` once, then start a new
Claude session. The installer backs up the existing project settings under
`.state/` and adds one PostToolUse hook without replacing other hooks or plugin
settings. Run the existing prepare-escalation workflow.

After the bundle MCP succeeds, `bundle_privacy_check.py` validates the fixed
output file's field allowlist and event schema, checks for known restricted case
values and email addresses, and records its SHA-256 and result in
`.state/bundle-privacy-check.json`. The `privacy-reviewer` subagent uses only Read
to review that evidence and the bundle. Neither component accesses credentials
or uploads data.

This is a local check of one generated artifact after creation. It does not
prevent unrelated network transfers or constitute a general DLP guarantee.
Sharing still requires a person's approval. Verify both actual hook execution
and collected project-hook/subagent metadata before presenting them as working.
