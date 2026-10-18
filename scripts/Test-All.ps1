param([switch]$IncludeBrowser)
$ErrorActionPreference='Stop'
$repoPath=Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $repoPath
& ./backend/.venv/Scripts/python.exe -m pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& ./backend/.venv/Scripts/python.exe -m pip check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Push-Location -LiteralPath (Join-Path $repoPath 'frontend')
try {
    & npm.cmd run test
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & npm.cmd run build
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($IncludeBrowser) {
        & npx.cmd playwright test
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } else { Write-Host 'Browser execution was not requested; this is not an E2E pass. Use -IncludeBrowser after installing Chromium.' }
} finally { Pop-Location }
