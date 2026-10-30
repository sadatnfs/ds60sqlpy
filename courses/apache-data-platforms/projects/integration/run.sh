#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
[[ $# == 2 && $1 == batch && $2 =~ ^batch-[a-z0-9-]{1,32}$ ]] || {
  echo 'Use run.sh batch batch-N with one new owned output name.' >&2
  exit 2
}
output=$2
[[ ! -L .workshop && ! -e .workshop/$output && ! -L .workshop/$output ]] || {
  echo 'Refusing existing or symbolic output state; no overwrite occurred.' >&2
  exit 2
}
if command -v docker >/dev/null 2>&1; then docker_cmd=$(command -v docker); else docker_cmd=${HOME}/.rd/bin/docker; fi
if [[ -n ${DOCKER_CONTEXT:-} ]]; then
  endpoint=$("$docker_cmd" context inspect "$DOCKER_CONTEXT" --format '{{.Endpoints.docker.Host}}')
elif [[ -n ${DOCKER_HOST:-} ]]; then
  endpoint=$DOCKER_HOST
else endpoint=$("$docker_cmd" context inspect --format '{{.Endpoints.docker.Host}}'); fi
[[ $endpoint == unix://* ]] || {
  echo 'Use a local Unix-socket Docker context.' >&2
  exit 2
}
engine=$("$docker_cmd" info --format '{{.OSType}}|{{.Architecture}}')
case "$engine" in
  'linux|aarch64' | 'linux|arm64') engine='linux|arm64' ;;
  'linux|x86_64' | 'linux|amd64') engine='linux|amd64' ;;
  *)
    echo 'Use a native Linux engine.' >&2
    exit 2
    ;;
esac
image=ds60sqlpy-worker-data-platforms-python:1.2.0
actual=$("$docker_cmd" image inspect --format '{{.Os}}|{{.Architecture}}' "$image")
[[ $actual == "$engine" ]] || {
  echo 'Prepare the native data-platforms-python image. Automatic emulation is disabled.' >&2
  exit 2
}
mkdir -p .workshop
"$docker_cmd" run --rm --pull never --network none --user "$(id -u):$(id -g)" --memory 512m --cpus 1 \
  --pids-limit 256 --cap-drop ALL --security-opt no-new-privileges \
  --read-only --tmpfs /tmp:size=64m \
  --mount "type=bind,source=$PWD,target=/project,readonly" \
  --mount "type=bind,source=$PWD/.workshop,target=/output" \
  --entrypoint python3 "$image" /project/batch_snapshot.py "/output/$output"
