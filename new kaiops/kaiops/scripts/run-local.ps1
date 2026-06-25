param(
    [switch]$SkipFrontend,
    [switch]$InstallFrontendDeps
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
$apiDir = Join-Path $repoRoot 'apps\api'
$webDir = Join-Path $repoRoot 'apps\web'

if (-not (Test-Path $python)) {
    throw "Virtual environment not found at $python. Create it in the repo root first."
}

$apiProcess = Start-Process -FilePath $python -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000') -WorkingDirectory $apiDir -PassThru
Write-Host "KaiOps API started on http://localhost:8000 (PID $($apiProcess.Id))"

if (-not $SkipFrontend) {
    $nodeCommand = Get-Command node -ErrorAction SilentlyContinue
    $npmCommand = Get-Command npm -ErrorAction SilentlyContinue

    if (-not $nodeCommand -or -not $npmCommand) {
        Write-Warning 'Node.js/npm are not installed or not on PATH. Frontend will not start.'
    }
    else {
        if ($InstallFrontendDeps -or -not (Test-Path (Join-Path $webDir 'node_modules'))) {
            Push-Location $webDir
            try {
                & npm install
            }
            finally {
                Pop-Location
            }
        }

        $webProcess = Start-Process -FilePath $npmCommand.Source -ArgumentList @('run', 'dev', '--', '-H', '0.0.0.0', '-p', '3000') -WorkingDirectory $webDir -PassThru
        Write-Host "KaiOps web started on http://localhost:3000 (PID $($webProcess.Id))"
    }
}

Write-Host 'If you are using local PostgreSQL/Redis/Kafka without Docker, ensure those services are already running and the .env values point to them.'
