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
    Write-Host 'Setup complete. Run .\scripts\start.ps1 and open http://127.0.0.1:8000'
} finally { Pop-Location }
