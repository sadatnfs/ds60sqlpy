#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker info >/dev/null
if ! docker image inspect postgres:17 >/dev/null 2>&1; then
    docker compose -f compose.classroom.yaml pull postgres
fi
export BUILDKIT_PROGRESS=plain COMPOSE_PROGRESS=plain
docker compose -f compose.classroom.yaml build lab
docker compose -f compose.classroom.yaml --profile python-core build python-core-worker
docker compose -f compose.classroom.yaml --profile python-core up -d --no-build --pull never --wait lab python-core-worker
address="$(docker compose -f compose.classroom.yaml port postgres "${DS60_LAB_PORT:-8765}")"
url="http://$address/journeys"
printf 'Classroom: %s\nProgress stays in the local classroom-learning Docker volume.\n' "$url"
if command -v open >/dev/null; then open "$url"; elif command -v xdg-open >/dev/null; then xdg-open "$url"; fi
