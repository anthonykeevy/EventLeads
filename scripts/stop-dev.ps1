Param(
  [int]$ApiPort = 8000,
  [int]$WebPort = 3000
)

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Ok($msg)   { Write-Host "[ OK ] $msg" -ForegroundColor Green }
function Write-Err($msg)  { Write-Host "[ERR] $msg" -ForegroundColor Red }

function Stop-ByPort([int]$Port, [string]$Label) {
  try {
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  } catch { $conns = $null }
  if (-not $conns) { Write-Ok "$Label not listening on port $Port (nothing to stop)"; return }
  $pids = ($conns | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique) | Where-Object { $_ -gt 0 }
  if (-not $pids) { Write-Ok "$Label no owning process found"; return }
  
  # Stop parent processes and their children
  foreach($procId in $pids){
    try {
      $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
      if ($proc) {
        # Stop children first, then parent
        $children = Get-WmiObject Win32_Process | Where-Object { $_.ParentProcessId -eq $procId }
        foreach($child in $children) {
          try { Stop-Process -Id $child.ProcessId -Force -ErrorAction SilentlyContinue } catch {}
        }
        Stop-Process -Id $procId -Force -ErrorAction Stop
        Write-Ok "$($Label) process $($procId) and children stopped"
      }
    } catch {
      Write-Warn "Failed to stop $($Label) process $($procId): $($_.Exception.Message)"
    }
  }
}

function Stop-Mailhog() {
  if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Write-Warn "Docker not found; cannot stop MailHog"; return }
  # Try compose stop first
  $stopped = $false
  if (Test-Path "docker-compose.yml") {
    try { 
      & docker compose stop mailhog | Out-Null
      if ($LASTEXITCODE -eq 0) { $stopped = $true }
    } catch { 
      try { 
        & docker-compose stop mailhog | Out-Null
        if ($LASTEXITCODE -eq 0) { $stopped = $true }
      } catch {} 
    }
  }
  if (-not $stopped) {
    try { 
      & docker stop mailhog | Out-Null
      if ($LASTEXITCODE -eq 0) { $stopped = $true }
    } catch {}
  }
  if ($stopped) { Write-Ok "MailHog stopped" } else { Write-Warn "MailHog stop command did not succeed (it may not be running)" }
}

Write-Info "Stopping frontend (port $WebPort)"
Stop-ByPort -Port $WebPort -Label "Frontend"

Write-Info "Stopping backend API (port $ApiPort)"
Stop-ByPort -Port $ApiPort -Label "Backend"

Write-Info "Stopping MailHog"
Stop-Mailhog

Write-Ok "Stop sequence completed"
