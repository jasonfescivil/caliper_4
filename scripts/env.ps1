param([string])
# Load .env into process if not already present
if (-not ) {
  # Assume repo root is parent of scripts dir
   = Split-Path  -Parent
   = Join-Path  ".env"
}
if (Test-Path ) {
  Get-Content  | Where-Object { /bin/bash -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object {
    , = /bin/bash -split '=',2
     = .Trim().Trim('"').Trim("'")
    if (-not (Test-Path "env:")) { Set-Item -Path "env:" -Value  }
  }
}
