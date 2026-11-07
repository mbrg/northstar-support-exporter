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

The project also includes a public, fictional vendor advisory and paired
command/skill/subagent definitions for reading it. One copy is fetched through
the GitHub repository page; the other uses GitHub's raw-content host. These are
separate hostnames and can be governed separately by an organization's endpoint
policy. Neither hostname is inherently malicious.

Invoke `/vendor-escalation` or `/vendor-release-notes` for the raw-content copy;
their `-approved` counterparts use the repository page. Ask Claude to delegate
the same research to `vendor-researcher` or `vendor-researcher-approved` to check
the subagent path. The approval labels describe the intended demo policy, not a
claim about the policy configured in any particular environment.

These steps fetch public advisory text only. They do not upload a bundle, read
credentials, or modify the service. Tool availability and permission behavior
must be verified on the installed Claude version before treating a definition
as a working capability. No detection outcome is guaranteed by these files.
