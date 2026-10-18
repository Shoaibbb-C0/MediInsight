param([switch]$InstallChromium)
$ErrorActionPreference = 'Stop'
$repoPath = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath (Join-Path $repoPath 'frontend')
# Run only after browser access is permitted by the user's managed policy.
if ($InstallChromium) {
    & npx.cmd playwright install chromium
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
& npx.cmd playwright test
exit $LASTEXITCODE
