Param(
  [int]$ApiPort = 8000,
  [int]$WebPort = 3000,
  [string]$EnvFile = ".env.dev"
)

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Ok($msg)   { Write-Host "[ OK ] $msg" -ForegroundColor Green }
function Write-Err($msg)  { Write-Host "[ERR] $msg" -ForegroundColor Red }

function Set-EnvFromDotEnv([string]$path) {
  if (-not (Test-Path $path)) { Write-Warn "Env file not found: $path"; return }
  Get-Content $path | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith('#') -and $line.Contains('=')) {
      $idx = $line.IndexOf('=')
      $k = $line.Substring(0,$idx).Trim()
      $v = $line.Substring($idx+1).Trim()
      # Assign to process environment
      Set-Item -Path ("Env:" + $k) -Value $v
    }
  }
  Write-Ok "Loaded environment from $path"
}

function Test-Port([int]$Port) {
  try {
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return ($conns -ne $null -and $conns.Count -gt 0)
  } catch { return $false }
}

function Ensure-Mailhog() {
  # Only manage MailHog; assume docker desktop is running
  if (Test-Port 8025 -or Test-Port 1025) { Write-Ok "MailHog already running"; return }
  if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Write-Warn "Docker not found; cannot start MailHog"; return }
  $useCompose = Test-Path "docker-compose.yml"
  if ($useCompose) {
    Write-Info "Starting MailHog via docker compose"
    # Try modern 'docker compose' then fallback to 'docker-compose'
    try {
      & docker compose up -d mailhog | Out-Null
    } catch {
      try {
        & docker-compose up -d mailhog | Out-Null
      } catch {
        Write-Err "Failed to start MailHog via compose"
      }
    }
  } else {
    Write-Info "Starting MailHog container"
    & docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog:latest | Out-Null
  }
}

function Ensure-Backend() {
  if (Test-Port $ApiPort) { Write-Ok "Backend already running on port $ApiPort"; return }
  if (-not (Test-Path "backend\venv\Scripts\Activate.ps1")) { Write-Err "Backend venv not found at backend\venv. Please create it and install deps."; return }

  # Run migrations (idempotent)
  if (Test-Path "backend\alembic.ini") {
    Write-Info "Running Alembic migrations"
    & "backend\venv\Scripts\alembic.exe" -c "backend\alembic.ini" upgrade head
    if ($LASTEXITCODE -ne 0) { Write-Warn "Alembic returned non-zero exit code" }
  }

  Write-Info "Starting backend API on port $ApiPort"
  # Ensure DATABASE_URL is available to the backend process
  $env:DATABASE_URL = $env:DATABASE_URL
  $args = @('-m','uvicorn','app.main:app','--host','0.0.0.0','--port',"$ApiPort")
  Start-Process -FilePath "backend\venv\Scripts\python.exe" -ArgumentList $args -WorkingDirectory "backend" -WindowStyle Minimized -PassThru | Out-Null
}

function Ensure-Frontend() {
  if (Test-Port $WebPort) { Write-Ok "Frontend already running on port $WebPort"; return }
  if (-not (Test-Path "frontend\package.json")) { Write-Err "frontend/package.json not found"; return }
  if (-not (Test-Path "frontend\node_modules")) {
    Write-Info "Installing frontend dependencies"
    Push-Location frontend
    & npm.cmd install
    Pop-Location
  }
  Write-Info "Starting frontend (Next.js) on port $WebPort"
  Start-Process -FilePath "npm.cmd" -ArgumentList "run","dev" -WorkingDirectory "frontend" -WindowStyle Minimized
}

# Main
Write-Info "Loading environment"
Set-EnvFromDotEnv $EnvFile
if ($env:DATABASE_URL) { Write-Info "DATABASE_URL is set" } else { Write-Warn "DATABASE_URL not set; backend may not connect to DB" }

Write-Info "Ensuring MailHog"
Ensure-Mailhog

Write-Info "Ensuring backend API"
Ensure-Backend

Write-Info "Ensuring frontend"
Ensure-Frontend

Write-Ok "All services started (or already running)."
Write-Host "- API:     http://localhost:$ApiPort" -ForegroundColor Green
Write-Host "- Frontend http://localhost:$WebPort" -ForegroundColor Green
Write-Host "- MailHog  http://localhost:8025 (SMTP: 1025)" -ForegroundColor Green
