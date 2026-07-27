# Stop processes occupying port 8000 (incl. uvicorn reload leftovers)
$port = 8000

$pids = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique

if (-not $pids) {
  Write-Host "Port $port is free."
  exit 0
}

foreach ($procId in $pids) {
  try {
    $proc = Get-Process -Id $procId -ErrorAction Stop
    Stop-Process -Id $procId -Force
    Write-Host "Stopped $($proc.ProcessName) (PID=$procId)"
  } catch {
    Write-Host "Failed to stop PID=$procId : $_"
  }
}
