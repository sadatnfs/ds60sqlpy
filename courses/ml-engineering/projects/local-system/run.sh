#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
cd "$project_dir"
action=${1:-start}
if [[ $# -gt 0 ]]; then shift; fi
command -v docker >/dev/null || {
  echo 'Start a local Docker engine and make its CLI available.' >&2
  exit 2
}
if [[ -n ${DOCKER_CONTEXT:-} ]]; then
  endpoint=$(docker context inspect "$DOCKER_CONTEXT" --format '{{.Endpoints.docker.Host}}')
elif [[ -n ${DOCKER_HOST:-} ]]; then
  endpoint=$DOCKER_HOST
else
  endpoint=$(docker context inspect --format '{{.Endpoints.docker.Host}}')
fi
[[ $endpoint == unix://* ]] || {
  echo 'Use a local Unix-socket Docker context for this owned bind-mounted workshop.' >&2
  exit 2
}
if [[ ! -e .env ]]; then
  image=${DS60_DATA_IMAGE:-ds60sqlpy-worker-data-engineering:1.0.0}
  docker image inspect "$image" >/dev/null 2>&1 || {
    echo 'Prepare the data-engineering image from the main repository first; see README.md.' >&2
    exit 2
  }
  owner=$(docker run --rm --pull never --network none --read-only --entrypoint python3 "$image" -c 'import uuid; print(uuid.uuid4().hex)')
  [[ $owner =~ ^[a-f0-9]{32}$ ]] || {
    echo 'Could not obtain a valid ownership marker.' >&2
    exit 2
  }
  (
    umask 077
    printf '%s\n' "DS60_WORKSHOP_OWNER=$owner" "DS60_WORKSHOP_PROJECT=ds60-mle-workshop-${owner:0:8}" \
      "DS60_WORKSHOP_UID=$(id -u)" "DS60_WORKSHOP_GID=$(id -g)" "DS60_WORKSHOP_PORT=0" "DS60_DATA_IMAGE=$image" >.env
  )
fi
[[ -f .env && ! -L .env ]] || {
  echo 'The workshop environment file must be a regular owned file.' >&2
  exit 2
}
owner=$(awk -F= '$1=="DS60_WORKSHOP_OWNER" {print $2}' .env)
project=$(awk -F= '$1=="DS60_WORKSHOP_PROJECT" {print $2}' .env)
[[ $owner =~ ^[a-f0-9]{32}$ && $project =~ ^ds60-mle-[a-z0-9-]+$ ]] || {
  echo 'Invalid workshop identity; retain the state and inspect .env.' >&2
  exit 2
}
for id in $(docker ps -aq --filter "label=com.docker.compose.project=$project"); do
  actual=$(docker inspect --format '{{index .Config.Labels "org.ds60.workshop.owner"}}' "$id")
  [[ $actual == "$owner" ]] || {
    echo 'Project container ownership mismatch; no action taken.' >&2
    exit 2
  }
done
for id in $(docker network ls -q --filter "label=com.docker.compose.project=$project"); do
  actual=$(docker network inspect --format '{{index .Labels "org.ds60.workshop.owner"}}' "$id")
  [[ $actual == "$owner" ]] || {
    echo 'Project network ownership mismatch; no action taken.' >&2
    exit 2
  }
done
compose=(docker compose --env-file .env -p "$project" -f compose.yaml)
case "$action" in
  start | resume)
    mkdir -p state
    if [[ -f state/current.json ]]; then
      "${compose[@]}" up -d --no-deps --no-build --pull never --wait --wait-timeout 90 predictor
    elif [[ $action == resume ]]; then
      echo 'No trained model is present. Use start for a fresh owned training run.' >&2
      exit 2
    else
      "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 180 predictor
    fi
    address=$("${compose[@]}" port predictor 8080)
    [[ $address =~ ^127\.0\.0\.1:[0-9]+$ ]] || {
      echo 'Expected a loopback-only published address.' >&2
      exit 2
    }
    printf 'Local prediction service: http://%s\n' "$address"
    ;;
  stop) "${compose[@]}" stop predictor ;;
  down) "${compose[@]}" down ;;
  status) "${compose[@]}" ps ;;
  logs) "${compose[@]}" logs --no-color --tail 100 predictor ;;
  activate)
    [[ ${1:-} == v1 || ${1:-} == v2 ]] || {
      echo 'Use activate v1 or activate v2.' >&2
      exit 2
    }
    "${compose[@]}" run --rm --pull never --no-deps -T control activate --version "$1"
    ;;
  inject-stale | restore-features) "${compose[@]}" run --rm --pull never --no-deps -T control "$action" ;;
  *)
    echo 'Use start, resume, stop, down, status, logs, activate v1|v2, inject-stale or restore-features.' >&2
    exit 2
    ;;
esac
