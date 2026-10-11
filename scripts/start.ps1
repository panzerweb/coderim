$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if (!(Test-Path -LiteralPath (Join-Path $projectRoot '.venv/Scripts/python.exe')) -or !(Test-Path -LiteralPath (Join-Path $projectRoot 'frontend/dist/index.html'))) {
    throw 'Run .\scripts\setup.ps1 first.'
}
Push-Location -LiteralPath $projectRoot
try {
    Write-Host 'Code Relay: http://127.0.0.1:8000 — Ctrl+C to stop'
    & '.\.venv\Scripts\python.exe' -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
} finally { Pop-Location }
