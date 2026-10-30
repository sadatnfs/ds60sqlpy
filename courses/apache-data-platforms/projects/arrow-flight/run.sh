#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
cd "$project_dir"
action=${1:-start}
if [[ $# -gt 0 ]]; then shift; fi
case "$action" in
  start | resume | stop | down | status | logs | check | network-check | ipc-check)
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
    echo 'Use start, resume, stop, down, status, logs, check, network-check, ipc-check, or destroy --confirm-owned-data-loss.'
    exit 0
    ;;
  *)
    echo 'Unknown action; no action taken.' >&2
    exit 2
    ;;
esac
if command -v docker >/dev/null 2>&1; then
  docker_cmd=$(command -v docker)
elif [[ -x ${HOME}/.rd/bin/docker ]]; then
  docker_cmd=${HOME}/.rd/bin/docker
else
  echo 'Start a local Docker engine and make its CLI available.' >&2
  exit 2
fi
unset DOCKER_DEFAULT_PLATFORM
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
    echo 'Prepare the native data-platforms-python classroom image first.' >&2
    return 2
  }
  [[ $platform == "$engine" ]] || {
    echo 'The local image does not match the native Docker engine architecture.' >&2
    echo 'Prepare the supported native image or use an explicitly selected native host. Automatic emulation is disabled.' >&2
    return 2
  }
}
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
  [[ $action == start ]] || {
    echo 'No initialized workshop. Use start first.' >&2
    exit 2
  }
  image=${DS60_PLATFORM_IMAGE:-ds60sqlpy-worker-data-platforms-python:1.2.0}
  [[ $image =~ ^ds60sqlpy-worker-data-platforms-python:[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
    echo 'Use a local versioned data-platforms-python image.' >&2
    exit 2
  }
  verify_native_image
  owner=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
  [[ $owner =~ ^[a-f0-9]{32}$ ]] || {
    echo 'Could not create an ownership marker.' >&2
    exit 2
  }
  (
    umask 077
    printf '%s\n' "DS60_WORKSHOP_OWNER=$owner" "DS60_WORKSHOP_PROJECT=ds60-apache-flight-${owner:0:12}" \
      "DS60_PLATFORM_IMAGE=$image" >.env
  )
fi
[[ -f .env && ! -L .env ]] || {
  echo 'The environment must be a regular owned file.' >&2
  exit 2
}
owner=''
project=''
image=''
while IFS='=' read -r key value; do
  case "$key" in
    DS60_WORKSHOP_OWNER)
      [[ -z $owner && $value =~ ^[a-f0-9]{32}$ ]] || exit 2
      owner=$value
      ;;
    DS60_WORKSHOP_PROJECT)
      [[ -z $project && $value =~ ^ds60-apache-flight-[a-f0-9]{12}$ ]] || exit 2
      project=$value
      ;;
    DS60_PLATFORM_IMAGE)
      [[ -z $image && $value =~ ^ds60sqlpy-worker-data-platforms-python:[0-9]+\.[0-9]+\.[0-9]+$ ]] || exit 2
      image=$value
      ;;
    *)
      echo 'Unknown environment field; no Docker mutation taken.' >&2
      exit 2
      ;;
  esac
done <.env
[[ -n $owner && $project == ds60-apache-flight-${owner:0:12} && -n $image ]] || {
  echo 'Incomplete or mismatched workshop identity.' >&2
  exit 2
}
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
    [[ $actual == "$owner|apache-arrow-flight" ]] || {
      echo 'Ownership mismatch; no action taken.' >&2
      exit 2
    }
  done
done
export DS60_WORKSHOP_OWNER="$owner" DS60_WORKSHOP_PROJECT="$project" DS60_PLATFORM_IMAGE="$image"
compose=("$docker_cmd" compose --env-file .env -p "$project" -f compose.yaml)
case "$action" in
  start)
    verify_native_image
    "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 90 server
    echo 'Flight is healthy on its private service endpoint. Use run.sh check for the client.'
    ;;
  resume)
    existing=$("${compose[@]}" ps -aq server)
    [[ $existing =~ ^[a-f0-9]{12,64}$ ]] || {
      echo 'No single retained container; use start with retained data.' >&2
      exit 2
    }
    "${compose[@]}" start server
    healthy=false
    for ((attempt = 0; attempt < 90; attempt++)); do
      state=$("$docker_cmd" inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$existing")
      if [[ $state == 'running|healthy' ]]; then
        healthy=true
        break
      fi
      if [[ $state == exited\|* || $state == dead\|* || $state == running\|none ]]; then
        echo 'Retained container failed its health contract; inspect logs.' >&2
        exit 2
      fi
      sleep 1
    done
    [[ $healthy == true && $("${compose[@]}" ps -aq server) == "$existing" ]] || {
      echo 'Resume did not produce the same healthy container within its deadline.' >&2
      exit 2
    }
    echo 'Flight is healthy on its private service endpoint. Use run.sh check for the client.'
    ;;
  check) "${compose[@]}" run --rm --pull never --no-deps -T client ;;
  network-check) "${compose[@]}" run --rm --pull never --no-deps -T client client.py --network ;;
  ipc-check) bash check-ipc.sh "$image" "$docker_cmd" ;;
  stop) "${compose[@]}" stop server ;;
  down) "${compose[@]}" down ;;
  destroy) "${compose[@]}" down --volumes ;;
  status) "${compose[@]}" ps ;;
  logs) "${compose[@]}" logs --no-color --tail 100 server ;;
esac
