param(
    [int]$ApiPort = 8001,
    [switch]$SkipDocker,
    [switch]$NoKillPort,
    [switch]$SkipFrontend,
    [switch]$InstallFrontendDeps
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$venvRoot = $null
$venvCandidates = @(
    (Join-Path $repoRoot '.venv'),
    (Join-Path (Split-Path -Parent $repoRoot) '.venv'),
    (Join-Path (Split-Path -Parent (Split-Path -Parent $repoRoot)) '.venv')
)

foreach ($candidate in $venvCandidates) {
    if (Test-Path (Join-Path $candidate 'Scripts\python.exe')) {
        $venvRoot = $candidate
        break
    }
}

$python = Join-Path $venvRoot 'Scripts\python.exe'
$venvScripts = Join-Path $venvRoot 'Scripts'
$apiDir = Join-Path $repoRoot 'apps\api'
$webDir = Join-Path $repoRoot 'apps\web'
$dockerDir = Join-Path $repoRoot 'infrastructure\docker'

if (-not $venvRoot -or -not (Test-Path $python)) {
    throw "Virtual environment not found. Checked: $($venvCandidates -join ', ')"
}

# Emulate venv activation for commands launched from this script.
$env:VIRTUAL_ENV = $venvRoot
if ($env:Path -notlike "$venvScripts*") {
    $env:Path = "$venvScripts;$env:Path"
}

if (-not $SkipDocker) {
    $dockerCommand = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCommand) {
        throw 'Docker CLI is not installed or not on PATH.'
    }

    Push-Location $dockerDir
    try {
        & docker compose up -d
    }
    finally {
        Pop-Location
    }
}

if (-not $NoKillPort) {
    $listeners = Get-NetTCPConnection -LocalPort $ApiPort -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique

    foreach ($processId in $listeners) {
        if ($processId) {
            try {
                Stop-Process -Id $processId -Force -ErrorAction Stop
                Write-Host "Stopped process $processId using port $ApiPort"
            }
            catch {
                Write-Warning "Could not stop process $processId on port ${ApiPort}: $($_.Exception.Message)"
            }
        }
    }
}

$apiProcess = Start-Process -FilePath $python -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', $ApiPort.ToString()) -WorkingDirectory $apiDir -PassThru
Write-Host "KaiOps API started on http://localhost:$ApiPort (PID $($apiProcess.Id))"

if (-not $SkipFrontend) {
    $frontendPort = 3000
    if (-not $NoKillPort) {
        $frontendListeners = Get-NetTCPConnection -LocalPort $frontendPort -State Listen -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty OwningProcess -Unique

        foreach ($processId in $frontendListeners) {
            if ($processId) {
                try {
                    Stop-Process -Id $processId -Force -ErrorAction Stop
                    Write-Host "Stopped process $processId using port $frontendPort"
                }
                catch {
                    Write-Warning "Could not stop process $processId on port ${frontendPort}: $($_.Exception.Message)"
                }
            }
        }
    }

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

        $webProcess = Start-Process -FilePath $npmCommand.Source -ArgumentList @('run', 'dev', '--', '-H', '0.0.0.0', '-p', $frontendPort.ToString()) -WorkingDirectory $webDir -PassThru
        Write-Host "KaiOps web started on http://localhost:$frontendPort (PID $($webProcess.Id))"
    }
}

if ($SkipDocker) {
    Write-Host 'Docker startup skipped. Ensure local Postgres/Redis/Kafka/Prometheus are already running.'
}
