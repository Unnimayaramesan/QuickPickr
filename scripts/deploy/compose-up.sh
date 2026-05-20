#!/usr/bin/env bash
# Build and start QuickPickr via Docker Compose (API + web + Redis)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "WARN: No .env at repo root. Copy .env.example and set Vertex + GCP variables." >&2
fi

mkdir -p .secrets
docker compose up --build -d
echo ""
echo "Web:  http://localhost:3000"
echo "API:  http://127.0.0.1:8080/health"
echo "Logs: docker compose logs -f api web"
