# Stop QuickPickr Docker Compose stack
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\..")
docker compose down
