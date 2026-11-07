param([switch]$VerifyOnly)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Create the virtual environment and install requirements.txt first' }
$envLine = Get-Content -LiteralPath (Join-Path $PSScriptRoot '.env') | Where-Object { $_.StartsWith('NORTHSTAR_TICKET_API_TOKEN=') }
if (@($envLine).Count -ne 1) { throw 'Expected one demo credential in .env' }
$env:NORTHSTAR_TICKET_API_TOKEN = $envLine.Substring($envLine.IndexOf('=') + 1)
$state = Join-Path $PSScriptRoot '.state'
New-Item -ItemType Directory -Force -Path $state | Out-Null
$listener = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue
if (-not $listener) {
    $serverPath = Join-Path $PSScriptRoot 'ticket_server.py'
    $server = Start-Process -FilePath $python -ArgumentList @('"' + $serverPath + '"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $state 'ticket.stdout.log') -RedirectStandardError (Join-Path $state 'ticket.stderr.log')
    $server.Id | Set-Content (Join-Path $state 'ticket-server.pid')
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        if ($server.HasExited) { throw 'Ticket server exited; inspect .state/ticket.stderr.log' }
        if (Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue) { break }
        Start-Sleep -Milliseconds 250
    }
} else {
    $owner = Get-CimInstance Win32_Process -Filter "ProcessId = $($listener[0].OwningProcess)"
    if ($owner.CommandLine -notlike ('*' + (Join-Path $PSScriptRoot 'ticket_server.py') + '*')) {
        throw 'Port 8765 belongs to another service; leave it running and select another demo port'
    }
}
& $python (Join-Path $PSScriptRoot 'verify_demo.py')
if ($LASTEXITCODE -ne 0) { throw 'Verification failed; do not proceed to Claude' }
if (-not $VerifyOnly) { & claude --permission-mode default }
