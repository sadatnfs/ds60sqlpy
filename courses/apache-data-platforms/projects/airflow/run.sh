#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
cd "$project_dir"
action=${1:-start}
if [[ $# -gt 0 ]]; then shift; fi
reuse_core=false
if [[ $# == 1 && $1 == --reuse-core && ($action == prepare || $action == start) ]]; then
  reuse_core=true
  shift
fi
case "$action" in
  prepare | start | resume | stop | down | status | logs | health | readback | run-intervals | retry-check | backfill-check | asset-check | connection-check)
    [[ $# == 0 ]] || {
      echo 'Unexpected arguments; no action taken.' >&2
      exit 2
    }
    ;;
  destroy)
    [[ $# == 1 && $1 == --confirm-owned-data-loss ]] || {
      echo 'To delete this workshop data, use destroy --confirm-owned-data-loss.' >&2
      exit 2
    }
    ;;
  help | --help | -h)
    echo 'Use prepare [--reuse-core], start [--reuse-core], resume, stop, down, status, logs, health, readback, run-intervals, retry-check, backfill-check, asset-check, connection-check, or destroy --confirm-owned-data-loss.'
    exit 0
    ;;
  *)
    echo 'Unknown action; no action taken.' >&2
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
  echo 'Start a local Docker engine and make its CLI available.' >&2
  exit 2
fi
if [[ -n ${DOCKER_CONTEXT:-} ]]; then
  endpoint=$("$docker_cmd" context inspect "$DOCKER_CONTEXT" --format '{{.Endpoints.docker.Host}}')
elif [[ -n ${DOCKER_HOST:-} ]]; then
  endpoint=$DOCKER_HOST
else
  endpoint=$("$docker_cmd" context inspect --format '{{.Endpoints.docker.Host}}')
fi
[[ $endpoint == unix://* ]] || {
  echo 'This workshop requires a local Unix-socket Docker context.' >&2
  exit 2
}
verify_native_image() {
  local engine platform
  engine=$("$docker_cmd" info --format '{{.OSType}}|{{.Architecture}}')
  case "$engine" in
    'linux|aarch64' | 'linux|arm64') engine='linux|arm64' ;;
    'linux|x86_64' | 'linux|amd64') engine='linux|amd64' ;;
    *)
      echo 'Use a native Linux AMD64 or ARM64 Docker engine.' >&2
      return 2
      ;;
  esac
  platform=$("$docker_cmd" image inspect --format '{{.Os}}|{{.Architecture}}' "$image") || {
    echo 'Prepare this separate native Airflow image first.' >&2
    return 2
  }
  [[ $platform == "$engine" ]] || {
    echo 'The local image does not match the native Docker engine architecture.' >&2
    echo 'Prepare the supported native image or use an explicitly selected native host. Automatic emulation is disabled.' >&2
    return 2
  }
}
prepare_image() {
  engine=$("$docker_cmd" info --format '{{.OSType}}|{{.Architecture}}')
  case "$engine" in
    'linux|aarch64' | 'linux|arm64')
      native='linux|arm64'
      architecture=arm64
      ;;
    'linux|x86_64' | 'linux|amd64')
      native='linux|amd64'
      architecture=amd64
      ;;
    *)
      echo 'Use native Linux AMD64/ARM64; automatic emulation is disabled.' >&2
      exit 2
      ;;
  esac
  if [[ $image == ds60-apache-airflow-core:3.3.2 ]]; then
    base=ds60sqlpy-worker-python-core:1.1.0
    [[ $("$docker_cmd" image inspect --format '{{.Os}}|{{.Architecture}}' "$base") == "$native" ]] || {
      echo 'Prepare the matching native Core classroom image first.' >&2
      exit 2
    }
    "$docker_cmd" build --pull=false --progress=plain --build-arg "BASE_IMAGE=$base" -f Dockerfile.core -t "$image" .
  else
    "$docker_cmd" pull --platform "linux/$architecture" "$image"
  fi
  prepared_now=true
}
prepared_now=false
[[ ! -L .workshop-lock ]] || {
  echo 'Refusing a symlink lock path.' >&2
  exit 2
}
mkdir .workshop-lock 2>/dev/null || {
  echo 'Another workshop action owns .workshop-lock; inspect it before retrying.' >&2
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
if [[ ! -e .env && ! -L .env ]]; then
  [[ $action == start || $action == prepare ]] || {
    echo 'No initialized workshop. Use start first.' >&2
    exit 2
  }
  image=apache/airflow:3.3.2-python3.12@sha256:9df9c8be4096b9cc626bd7cb1f2b8c712eef66c59c615f8c7e6200871ca10bd1
  if [[ $reuse_core == true ]]; then image=ds60-apache-airflow-core:3.3.2; fi
  [[ $image =~ ^(ds60-apache-airflow-core:3\.3\.2|apache/airflow:3\.3\.2-python3\.12@sha256:9df9c8be4096b9cc626bd7cb1f2b8c712eef66c59c615f8c7e6200871ca10bd1)$ ]] || {
    echo 'Use the pinned Airflow upstream image or explicit Core fallback.' >&2
    exit 2
  }
  port=${AIRFLOW_WORKSHOP_PORT:-18880}
  [[ $port =~ ^[0-9]{4,5}$ && $port -ge 1024 && $port -le 65535 ]] || {
    echo 'Use a loopback host port from 1024 through 65535.' >&2
    exit 2
  }
  if [[ $action == prepare ]]; then prepare_image; fi
  verify_native_image
  owner=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
  [[ $owner =~ ^[a-f0-9]{32}$ ]] || {
    echo 'Could not create an ownership marker.' >&2
    exit 2
  }
  (
    umask 077
    printf '%s\n' "DS60_WORKSHOP_OWNER=$owner" "DS60_WORKSHOP_PROJECT=ds60-apache-airflow-${owner:0:12}" \
      "DS60_AIRFLOW_IMAGE=$image" "DS60_AIRFLOW_PORT=$port" >.env
  )
fi
[[ -f .env && ! -L .env ]] || {
  echo 'The environment must be a regular owned file.' >&2
  exit 2
}
owner='' project='' image='' port=''
while IFS='=' read -r key value; do
  case "$key" in
    DS60_WORKSHOP_OWNER)
      [[ -z $owner && $value =~ ^[a-f0-9]{32}$ ]] || exit 2
      owner=$value
      ;;
    DS60_WORKSHOP_PROJECT)
      [[ -z $project && $value =~ ^ds60-apache-airflow-[a-f0-9]{12}$ ]] || exit 2
      project=$value
      ;;
    DS60_AIRFLOW_IMAGE)
      [[ -z $image && $value =~ ^(ds60-apache-airflow-core:3\.3\.2|apache/airflow:3\.3\.2-python3\.12@sha256:9df9c8be4096b9cc626bd7cb1f2b8c712eef66c59c615f8c7e6200871ca10bd1)$ ]] || exit 2
      image=$value
      ;;
    DS60_AIRFLOW_PORT)
      [[ -z $port && $value =~ ^[0-9]{4,5}$ && $value -ge 1024 && $value -le 65535 ]] || exit 2
      port=$value
      ;;
    *)
      echo 'Unknown environment field; no Docker mutation taken.' >&2
      exit 2
      ;;
  esac
done <.env
[[ -n $owner && $project == ds60-apache-airflow-${owner:0:12} && -n $image && -n $port ]] || {
  echo 'Incomplete or mismatched workshop identity.' >&2
  exit 2
}
if [[ $reuse_core == true && $image != ds60-apache-airflow-core:3.3.2 ]]; then
  echo 'Saved workshop uses another preparation route; use a fresh owned copy.' >&2
  exit 2
fi
for kind in container network volume; do
  case "$kind" in
    container) ids=$("$docker_cmd" ps -aq --filter "label=com.docker.compose.project=$project") ;;
    network) ids=$("$docker_cmd" network ls -q --filter "label=com.docker.compose.project=$project") ;;
    volume) ids=$("$docker_cmd" volume ls -q --filter "label=com.docker.compose.project=$project") ;;
  esac
  for id in $ids; do
    if [[ $kind == container ]]; then
      actual=$("$docker_cmd" inspect --format '{{index .Config.Labels "org.ds60.workshop.owner"}}|{{index .Config.Labels "org.ds60.workshop.kind"}}' "$id")
    else
      actual=$("$docker_cmd" "$kind" inspect --format '{{index .Labels "org.ds60.workshop.owner"}}|{{index .Labels "org.ds60.workshop.kind"}}' "$id")
    fi
    [[ $actual == "$owner|apache-airflow" ]] || {
      echo 'Ownership mismatch; no action taken.' >&2
      exit 2
    }
  done
done
# Pin reviewed saved values; ambient shell exports must not override ownership.
export "DS60_WORKSHOP_OWNER=$owner" "DS60_WORKSHOP_PROJECT=$project" "DS60_AIRFLOW_IMAGE=$image" "DS60_AIRFLOW_PORT=$port"
compose=("$docker_cmd" compose --env-file .env -p "$project" -f compose.yaml)
case "$action" in
  prepare)
    if [[ $prepared_now == false ]]; then prepare_image; fi
    verify_native_image
    echo 'Prepared Airflow image and saved selection are ready.'
    ;;
  start)
    verify_native_image
    "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 240 airflow
    echo "Local Airflow UI: http://127.0.0.1:$port (fixture user learner, password learner)"
    ;;
  resume)
    existing=$("${compose[@]}" ps -aq airflow)
    [[ $existing =~ ^[a-f0-9]{12,64}$ ]] || {
      echo 'No retained container; use start with retained data.' >&2
      exit 2
    }
    "${compose[@]}" start airflow
    healthy=false
    for ((attempt = 0; attempt < 240; attempt++)); do
      state=$("$docker_cmd" inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$existing")
      if [[ $state == 'running|healthy' ]]; then
        healthy=true
        break
      fi
      if [[ $state == exited\|* || $state == dead\|* || $state == running\|none ]]; then
        echo 'Retained service failed readiness; inspect logs.' >&2
        exit 2
      fi
      sleep 1
    done
    [[ $healthy == true && $("${compose[@]}" ps -aq airflow) == "$existing" ]] || exit 2
    echo "Local Airflow UI: http://127.0.0.1:$port (fixture user learner, password learner)"
    ;;
  health | readback | run-intervals | retry-check | backfill-check | asset-check | connection-check)
    "${compose[@]}" exec -T airflow python3 /project/client.py "$action"
    ;;
  stop) "${compose[@]}" stop airflow ;;
  down) "${compose[@]}" down ;;
  destroy) "${compose[@]}" down --volumes ;;
  status) "${compose[@]}" ps ;;
  logs) "${compose[@]}" logs --no-color --tail 100 airflow ;;
esac
