$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    if (!(Test-Path -LiteralPath '.venv/Scripts/python.exe') -or !(Test-Path -LiteralPath 'frontend/dist/index.html')) {
        throw 'Run .\scripts\setup.ps1 first.'
    }
    & '.\.venv\Scripts\python.exe' tools/local_contest.py
    if ($LASTEXITCODE -ne 0) { throw 'Contest startup failed. Read the message above.' }
} finally { Pop-Location }
