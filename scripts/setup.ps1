param([switch]$Dev)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python environment creation failed.' }
    $requirements = if ($Dev) { 'backend/requirements-dev.txt' } else { 'backend/requirements.txt' }
    & '.\.venv\Scripts\python.exe' -m pip install -r $requirements
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
    Push-Location -LiteralPath (Join-Path $projectRoot 'frontend')
    try {
        npm.cmd ci
        if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
        npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
    } finally { Pop-Location }
    & '.\.venv\Scripts\python.exe' tools/validate_problems.py
    if ($LASTEXITCODE -ne 0) { throw 'Problem validation failed.' }
    Write-Host 'Setup complete. Use .\scripts\start-contest.ps1 for teams/organizers, or .\scripts\start.ps1 for practice.'
} finally { Pop-Location }
