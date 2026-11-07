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

The support engineer receives an ad-hoc vendor support URL and installs a
command, skill and subagent with a scoped WebFetch grant to that destination.
The three target definitions use the illustrative hostname
`northstar-case-1042.ngrok-free.app`; the `-approved` controls use GitHub.
GitHub and GitHub raw content remain approved development services.

This is a configuration-only posture demonstration. It does not require an
ngrok executable, account, running tunnel or live destination. The hostname is
not asserted to exist or be under the operator's control. Do not fetch it until
an operator supplies and verifies an owned endpoint. The grant is present in
real Claude configuration; successful network access is not demonstrated.

The public fictional advisory in `docs/vendor-advisory-1042.md` supplies the
case context. The rule condition is the configured WebFetch domain being
outside the organization's approved endpoint policy. No detection outcome is
guaranteed by these files; verify actual inventory and assessment findings.
