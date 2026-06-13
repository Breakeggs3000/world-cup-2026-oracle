# Start backend (uvicorn) and frontend (Vite) in separate windows.
# Usage: .\tools\scripts\start-dev.ps1

$Root = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$Backend = Join-Path $Root "src\backend"
$Frontend = Join-Path $Root "src\frontend"
$UvBin = Join-Path $env:USERPROFILE ".local\bin"
$FnmExe = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages\Schniz.fnm_Microsoft.Winget.Source_8wekyb3d8bbwe\fnm.exe"

function Get-ListenersOnPort {
    param([int]$Port)
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) { return @() }
    $conns | Select-Object -ExpandProperty OwningProcess -Unique
}

function Confirm-StopPortListeners {
    param(
        [int]$Port,
        [string]$Label
    )
    $pids = Get-ListenersOnPort -Port $Port
    if ($pids.Count -eq 0) { return $true }

    Write-Host "Warning: port $Port ($Label) is already in use." -ForegroundColor Yellow
    foreach ($procId in $pids) {
        try {
            $proc = Get-Process -Id $procId -ErrorAction Stop
            Write-Host "  PID $procId : $($proc.ProcessName)" -ForegroundColor Yellow
        } catch {
            Write-Host "  PID $procId : (process not found)" -ForegroundColor Yellow
        }
    }

    $answer = Read-Host "Kill ONLY processes listening on port $Port? [y/N]"
    if ($answer -notmatch '^[yY]') {
        Write-Host "Skipping $Label start; port $Port still in use." -ForegroundColor Red
        return $false
    }

    foreach ($procId in $pids) {
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "Stopped PID $procId (port $Port)." -ForegroundColor Green
        } catch {
            Write-Warning "Could not stop PID $procId : $_"
        }
    }

    Start-Sleep -Milliseconds 500
    $remaining = Get-ListenersOnPort -Port $Port
    if ($remaining.Count -gt 0) {
        Write-Host "Port $Port is still in use; skipping $Label start." -ForegroundColor Red
        return $false
    }
    return $true
}

if (-not (Test-Path (Join-Path $Backend ".venv"))) {
    Write-Error "Backend venv missing. Run: cd src/backend; uv venv; uv pip install -r requirements.txt"
    exit 1
}

$startBackend = Confirm-StopPortListeners -Port 8000 -Label "backend"
$startFrontend = Confirm-StopPortListeners -Port 5173 -Label "frontend"

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

if ($startBackend) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
    Start-Sleep -Seconds 2
} else {
    Write-Host "Backend was not started." -ForegroundColor Red
}

if ($startFrontend) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd
} else {
    Write-Host "Frontend was not started." -ForegroundColor Red
}

if ($startBackend -or $startFrontend) {
    Write-Host "Started dev server(s) in new windows."
    if ($startFrontend) { Write-Host "  UI:  http://localhost:5173" }
    if ($startBackend) { Write-Host "  API: http://localhost:8000/docs" }
}

