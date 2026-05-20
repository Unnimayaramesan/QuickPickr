# Build and start QuickPickr via Docker Compose (API + web + Redis)
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\..")

if (-not (Test-Path ".env")) {
    Write-Warning "No .env at repo root. Copy .env.example and set VERTEX_SEARCH_SERVING_CONFIG + GCP credentials."
}

if (-not (Test-Path ".secrets")) {
    New-Item -ItemType Directory -Path ".secrets" | Out-Null
    Write-Host "Created .secrets/ — place SA JSON and set GCP_SA_MOUNT in .env if using compose volume mount."
}

docker compose up --build -d
Write-Host ""
Write-Host "Web:  http://localhost:3000"
Write-Host "API:  http://127.0.0.1:8080/health"
Write-Host "Logs: docker compose logs -f api web"
