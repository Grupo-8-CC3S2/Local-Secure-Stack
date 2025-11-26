#!/usr/bin/env bash
set -euo pipefail

# Este script apaga el stack local y elimina los volúmenes asociados.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR%/scripts}"

cd "$REPO_ROOT"

echo "[down.sh] Deteniendo stack local y eliminando volúmenes..."
docker compose --env-file compose/.env -f compose/docker-compose.yml down -v
echo "[down.sh] Stack detenido y volúmenes eliminados."
