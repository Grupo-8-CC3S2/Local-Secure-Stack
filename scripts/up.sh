#!/usr/bin/env bash
set -euo pipefail

# Este script levanta el stack local (API + DB) usando Docker Compose.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR%/scripts}"

cd "$REPO_ROOT"

echo "[up.sh] Levantando stack local con Docker Compose..."
docker compose --env-file compose/.env -f compose/docker-compose.yml up -d --build
echo "[up.sh] Stack levantado. Revisa 'docker compose ps' para ver el estado de los contenedores."
