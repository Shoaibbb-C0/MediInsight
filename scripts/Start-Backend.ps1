param([ValidateRange(1024,65535)][int]$Port = 8001, [ValidateSet('local','supabase')][string]$AuthMode = 'local')
$ErrorActionPreference = 'Stop'
$repoPath = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $repoPath
$pythonPath = Join-Path $repoPath 'backend/.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Create backend/.venv and install backend/requirements.lock first. See FINAL_MANUAL_SETUP.md.' }
$env:ENVIRONMENT = 'development'
$env:AUTH_MODE = $AuthMode
Write-Host "Starting local backend on 127.0.0.1:$Port (authentication: $AuthMode). No cloud resources are created."
& $pythonPath -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port $Port --reload
exit $LASTEXITCODE
