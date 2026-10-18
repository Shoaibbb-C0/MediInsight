param([ValidateRange(1024,65535)][int]$Port = 3000, [ValidateRange(1024,65535)][int]$BackendPort = 8001)
$ErrorActionPreference = 'Stop'
$repoPath = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath (Join-Path $repoPath 'frontend')
$env:BACKEND_PORT = [string]$BackendPort
$env:FRONTEND_PORT = [string]$Port
$env:BACKEND_URL = "http://127.0.0.1:$BackendPort"
& npm.cmd run dev
exit $LASTEXITCODE
