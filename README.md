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

The support engineer receives a case-specific advisory link hosted through a
temporary ngrok endpoint. They install research helpers for this ad-hoc support
portal before the destination has been approved. GitHub and GitHub raw content
remain normal approved development services in this scenario.

Run `./start-vendor-portal.ps1` on the same WorkSpace. It starts a fixed-document
HTTP server on `127.0.0.1:8787` and verifies that credential, source and MCP paths
return 404. After installing and authenticating the official ngrok agent, run
`ngrok http http://127.0.0.1:8787`. The public endpoint serves only the synthetic
advisory. The ticket MCP remains separate on port 8765.

With the assigned HTTPS ngrok hostname, run
`.venv\Scripts\python.exe configure_vendor_endpoint.py https://YOUR-NGROK-HOST/advisories/case-1042`.
This verifies the public advisory before updating the three target definitions.
It preserves original definitions under the ignored `.state` directory. The
repository's initial raw-content URLs are approved baseline values until this
configuration step completes.

Invoke `/vendor-escalation` and `/vendor-release-notes`, then ask Claude to use
`vendor-researcher`. Their `-approved` counterparts continue to use the GitHub
repository page. An ngrok endpoint is not inherently malicious; the posture
finding is the specific unapproved domain grant in this organization's workflow.
Keep the origin and ngrok processes running during the demonstration. Stopping
the tunnel ends public access.

These steps fetch public advisory text only. They do not upload a bundle, read
credentials, or modify the service. Tool availability and permission behavior
must be verified on the installed Claude version before treating a definition
as a working capability. No detection outcome is guaranteed by these files.
