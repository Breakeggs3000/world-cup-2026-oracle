# Start backend (uvicorn) and frontend (Vite) in separate windows.
# Usage: .\tools\scripts\start-dev.ps1

$Root = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$Backend = Join-Path $Root "src\backend"
$Frontend = Join-Path $Root "src\frontend"
$UvBin = Join-Path $env:USERPROFILE ".local\bin"
$FnmExe = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages\Schniz.fnm_Microsoft.Winget.Source_8wekyb3d8bbwe\fnm.exe"

if (-not (Test-Path (Join-Path $Backend ".venv"))) {
    Write-Error "Backend venv missing. Run: cd src/backend; uv venv; uv pip install -r requirements.txt"
    exit 1
}

$backendCmd = @"
`$env:Path = '$UvBin;' + `$env:Path
Set-Location '$Backend'
Write-Host 'Backend: http://localhost:8000/docs' -ForegroundColor Green
uv run uvicorn app.main:app --reload --port 8000
"@

$frontendCmd = @"
if (Test-Path '$FnmExe') { Invoke-Expression (& '$FnmExe' env --use-on-cd | Out-String) }
Set-Location '$Frontend'
if (Get-Command fnm -ErrorAction SilentlyContinue) { fnm use 2>`$null }
Write-Host 'Frontend: http://localhost:5173' -ForegroundColor Green
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "Started backend and frontend in new windows."
Write-Host "  UI:  http://localhost:5173"
Write-Host "  API: http://localhost:8000/docs"
