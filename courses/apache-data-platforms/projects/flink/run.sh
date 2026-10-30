#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
cd "$project_dir"
action=${1:-start}
if [[ $# -gt 0 ]]; then shift; fi
binary=false
if [[ $# == 1 && $1 == --binary && ($action == prepare || $action == start) ]]; then
  binary=true
  shift
fi
case "$action" in
  prepare | start | resume | stop | down | status | logs | check | check-sql | event-time | state | checkpoint | savepoint | backpressure | readback | reconcile)
    [[ $# == 0 ]] || {
      echo 'Unexpected arguments; no action taken.' >&2
      exit 2
    }
    ;;
  destroy)
    [[ $# == 1 && $1 == --confirm-owned-data-loss ]] || {
      echo 'Use destroy --confirm-owned-data-loss.' >&2
      exit 2
    }
    ;;
  help | --help | -h)
    echo 'Use prepare --binary, start, resume, stop, down, status, logs, check, check-sql, event-time, state, checkpoint, savepoint, backpressure, readback, reconcile, or destroy --confirm-owned-data-loss.'
    exit 0
    ;;
  *)
    echo 'Unknown action; no mutation taken.' >&2
    exit 2
    ;;
esac
# Native-only preparation must not inherit an emulation platform override.
unset DOCKER_DEFAULT_PLATFORM
if command -v docker >/dev/null 2>&1; then
  docker_cmd=$(command -v docker)
elif [[ -x ${HOME}/.rd/bin/docker ]]; then
  docker_cmd=${HOME}/.rd/bin/docker
else
  echo 'Start a local Docker engine and expose its CLI.' >&2
  exit 2
fi
if [[ -n ${DOCKER_CONTEXT:-} ]]; then
  endpoint=$("$docker_cmd" context inspect "$DOCKER_CONTEXT" --format '{{.Endpoints.docker.Host}}')
elif [[ -n ${DOCKER_HOST:-} ]]; then
  endpoint=$DOCKER_HOST
else endpoint=$("$docker_cmd" context inspect --format '{{.Endpoints.docker.Host}}'); fi
[[ $endpoint == unix://* ]] || {
  echo 'Use a local Unix-socket Docker engine, including through WSL2.' >&2
  exit 2
}
engine=$("$docker_cmd" info --format '{{.OSType}}|{{.Architecture}}')
case "$engine" in
  'linux|aarch64' | 'linux|arm64') native='linux|arm64' ;;
  'linux|x86_64' | 'linux|amd64') native='linux|amd64' ;;
  *)
    echo 'Use native Linux AMD64/ARM64. Automatic emulation is disabled.' >&2
    exit 2
    ;;
esac
image=ds60-apache-flink-binary:2.3.0
verify_image() {
  [[ $("$docker_cmd" image inspect --format '{{.Os}}|{{.Architecture}}' "$1") == "$native" ]] || {
    echo 'Prepare the matching native reviewed image; automatic emulation is disabled.' >&2
    return 2
  }
}
[[ ! -L .workshop-lock ]] || {
  echo 'Refusing a symlink lock path.' >&2
  exit 2
}
mkdir .workshop-lock 2>/dev/null || {
  echo 'Another action owns .workshop-lock; inspect it before retrying.' >&2
  exit 2
}
printf '%s\n' "$$" >.workshop-lock/pid
release_lock() {
  if [[ -f .workshop-lock/pid && ! -L .workshop-lock/pid && $(cat .workshop-lock/pid) == "$$" ]]; then
    rm .workshop-lock/pid
    rmdir .workshop-lock
  fi
}
trap release_lock EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
if [[ -e .env || -L .env ]]; then
  [[ -f .env && ! -L .env && $(wc -c <.env) -le 4096 ]] || {
    echo 'Use a bounded regular ownership record.' >&2
    exit 2
  }
  owner='' project='' selected=''
  while IFS='=' read -r key value; do
    case "$key" in
      DS60_WORKSHOP_OWNER)
        [[ -z $owner && $value =~ ^[a-f0-9]{32}$ ]] || exit 2
        owner=$value
        ;;
      DS60_WORKSHOP_PROJECT)
        [[ -z $project && $value =~ ^ds60-apache-flink-[a-f0-9]{12}$ ]] || exit 2
        project=$value
        ;;
      DS60_FLINK_IMAGE)
        [[ -z $selected && $value == "$image" ]] || exit 2
        selected=$value
        ;;
      *)
        echo 'Unknown environment field; no mutation taken.' >&2
        exit 2
        ;;
    esac
  done <.env
  [[ -n $owner && $project == ds60-apache-flink-${owner:0:12} && $selected == "$image" ]] || {
    echo 'Ownership record differs.' >&2
    exit 2
  }
else
  [[ $action == prepare || $action == start ]] || {
    echo 'Initialize this owned workshop with prepare/start first.' >&2
    exit 2
  }
  owner='' project=''
fi
if [[ -n $project ]]; then
  for kind in container network volume; do
    case "$kind" in
      container) ids=$("$docker_cmd" ps -aq --filter "label=com.docker.compose.project=$project") ;;
      network) ids=$("$docker_cmd" network ls -q --filter "label=com.docker.compose.project=$project") ;;
      volume) ids=$("$docker_cmd" volume ls -q --filter "label=com.docker.compose.project=$project") ;;
    esac
    for id in $ids; do
      if [[ $kind == container ]]; then
        actual=$("$docker_cmd" inspect --format '{{index .Config.Labels "org.ds60.workshop.owner"}}|{{index .Config.Labels "org.ds60.workshop.kind"}}' "$id")
      else actual=$("$docker_cmd" "$kind" inspect --format '{{index .Labels "org.ds60.workshop.owner"}}|{{index .Labels "org.ds60.workshop.kind"}}' "$id"); fi
      [[ $actual == "$owner|apache-flink" ]] || {
        echo 'Resource ownership mismatch; no mutation taken.' >&2
        exit 2
      }
    done
  done
fi
if [[ $action == prepare ]]; then
  [[ $binary == true ]] || {
    echo 'Select the explicit checksum-verified prepare --binary route.' >&2
    exit 2
  }
  base=${DS60_FLINK_JAVA_IMAGE:-ds60sqlpy-worker-scala-jvm:1.3.0}
  [[ $base =~ ^ds60sqlpy-worker-scala-jvm:[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
    echo 'Use a reviewed local Java17 classroom base.' >&2
    exit 2
  }
  verify_image "$base"
  "$docker_cmd" build --pull=false --progress=plain --build-arg "BASE_IMAGE=$base" --tag "$image" "$project_dir/binary-image"
fi
if [[ -z $project ]]; then
  verify_image "$image"
  owner=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
  [[ $owner =~ ^[a-f0-9]{32}$ ]] || exit 2
  project=ds60-apache-flink-${owner:0:12}
  (
    umask 077
    printf '%s\n' "DS60_WORKSHOP_OWNER=$owner" "DS60_WORKSHOP_PROJECT=$project" "DS60_FLINK_IMAGE=$image" >.env
  )
fi
# Pin reviewed saved values; ambient shell exports must not override ownership.
export "DS60_WORKSHOP_OWNER=$owner" "DS60_WORKSHOP_PROJECT=$project" "DS60_FLINK_IMAGE=$image"
compose=("$docker_cmd" compose --env-file .env -p "$project" -f compose.yaml)
wait_service() {
  local service=$1 retained=${2:-} actual state
  actual=$("${compose[@]}" ps -aq "$service")
  [[ $actual =~ ^[a-f0-9]{12,64}$ && (-z $retained || $retained == "$actual") ]] || return 2
  for ((attempt = 0; attempt < 120; attempt++)); do
    state=$("$docker_cmd" inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$actual")
    [[ $state == 'running|healthy' ]] && return 0
    [[ $state != exited\|* && $state != dead\|* ]] || {
      echo 'Service failed readiness; inspect logs.' >&2
      return 2
    }
    sleep 1
  done
  echo 'Service did not become healthy within its deadline.' >&2
  return 2
}
client() { "${compose[@]}" exec -T jobmanager python3 /project/workshop.py "$1"; }
case "$action" in
  prepare)
    verify_image "$image"
    echo 'Verified native binary image prepared; no service started.'
    ;;
  start)
    verify_image "$image"
    "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 120 jobmanager taskmanager
    client ready
    ;;
  resume)
    for service in jobmanager taskmanager; do
      retained=$("${compose[@]}" ps -aq "$service")
      [[ $retained =~ ^[a-f0-9]{12,64}$ ]] || {
        echo 'Retained container absent; use start with retained data.' >&2
        exit 2
      }
      "${compose[@]}" start "$service"
      wait_service "$service" "$retained"
    done
    client ready
    ;;
  check | check-sql | event-time | state | savepoint | backpressure | readback | reconcile) client "$action" ;;
  checkpoint)
    client checkpoint-begin
    if client checkpoint-restart-needed; then
      retained=$("${compose[@]}" ps -aq taskmanager)
      "${compose[@]}" stop taskmanager
      "${compose[@]}" start taskmanager
      wait_service taskmanager "$retained"
    else
      code=$?
      [[ $code == 1 ]] || exit "$code"
    fi
    client checkpoint-finish
    ;;
  stop) "${compose[@]}" stop taskmanager jobmanager ;;
  down) "${compose[@]}" down ;;
  destroy) "${compose[@]}" down --volumes ;;
  status) "${compose[@]}" ps ;;
  logs) "${compose[@]}" logs --no-color --tail 100 jobmanager taskmanager ;;
esac
