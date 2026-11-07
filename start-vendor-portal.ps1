$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path $python)) { throw 'Run the Northstar environment setup first' }
$state = Join-Path $PSScriptRoot '.state'
New-Item -ItemType Directory -Force -Path $state | Out-Null
$listener = Get-NetTCPConnection -LocalPort 8787 -State Listen -ErrorAction SilentlyContinue
if ($listener) { throw 'Port 8787 is already in use; inspect its owner before restarting' }
$serverPath = Join-Path $PSScriptRoot 'vendor_portal.py'
$server = Start-Process -FilePath $python -ArgumentList @('"' + $serverPath + '"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $state 'vendor-portal.stdout.log') -RedirectStandardError (Join-Path $state 'vendor-portal.stderr.log')
$server.Id | Set-Content (Join-Path $state 'vendor-portal.pid')
$response = $null
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    if ($server.HasExited) { throw 'Advisory server exited; inspect .state/vendor-portal.stderr.log' }
    try {
        $response = Invoke-WebRequest 'http://127.0.0.1:8787/advisories/case-1042' -TimeoutSec 2
        if ($response.StatusCode -eq 200 -and $response.Content -match 'NORTHSTAR-VENDOR-ADVISORY-1042-V2') { break }
    } catch { Start-Sleep -Milliseconds 200 }
}
if (-not $response -or $response.Content -notmatch 'NORTHSTAR-VENDOR-ADVISORY-1042-V2') { throw 'Advisory readiness check failed' }
foreach ($path in @('/.env', '/.secrets/ticket-auth.json', '/ticket_server.py', '/mcp')) {
    try {
        $result = Invoke-WebRequest ('http://127.0.0.1:8787' + $path) -SkipHttpErrorCheck
        if ([int]$result.StatusCode -ne 404) { throw ('Unexpected response for ' + $path) }
    } catch { throw ('Public advisory boundary check failed for ' + $path) }
}
Write-Output 'PASS: advisory available; credential, project source and MCP paths return 404.'
Write-Output 'The ticket MCP remains separate on 127.0.0.1:8765.'
Write-Output 'Start the authenticated ngrok agent with: ngrok http http://127.0.0.1:8787'
