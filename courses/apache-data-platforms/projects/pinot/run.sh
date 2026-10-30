#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
cd "$project_dir"
action=${1:-start}
if [[ $# -gt 0 ]]; then shift; fi
requested_binary=false
if [[ $# == 1 && $1 == --binary && ($action == prepare || $action == start) ]]; then
  requested_binary=true
  shift
fi
case "$action" in
  prepare | start | resume | stop | down | status | logs | check | initialize | identity)
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
    echo 'Use prepare [--binary], start [--binary], initialize, check, identity, stop, resume, down, status, logs, or destroy --confirm-owned-data-loss.'
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
    echo 'Prepare the native Pinot workshop image first.' >&2
    return 2
  }
  [[ $platform == "$engine" ]] || {
    echo 'The local image does not match the native Docker engine architecture.' >&2
    echo 'Prepare the supported native image or use an explicitly selected native host. Automatic emulation is disabled.' >&2
    return 2
  }
}
verify_selected_image() {
  local image=$1
  verify_native_image
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
if [[ $action == prepare ]]; then
  engine=$("$docker_cmd" info --format '{{.OSType}}|{{.Architecture}}')
  case "$engine" in
    'linux|aarch64' | 'linux|arm64') engine='linux|arm64' ;;
    'linux|x86_64' | 'linux|amd64') engine='linux|amd64' ;;
    *)
      echo 'Use native Linux AMD64 or ARM64; automatic emulation is disabled.' >&2
      exit 2
      ;;
  esac
  if [[ $requested_binary == true ]]; then
    image=ds60-apache-pinot-binary:1.5.1
    base=${DS60_PINOT_BASE:-ds60sqlpy-worker-scala-jvm:1.3.0}
    [[ $base =~ ^ds60sqlpy-worker-scala-jvm:[0-9]+\.[0-9]+\.[0-9]+$ ]] || exit 2
    verify_selected_image "$base"
    "$docker_cmd" build --pull=false --progress=plain --build-arg "BASE_IMAGE=$base" --tag "$image" "$project_dir/binary-image"
  else
    image=ds60-apache-pinot-upstream:1.5.1
    upstream=apachepinot/pinot@sha256:dbb65d3732eea6edf2619b0b734f13466bf1c6fd73ab9abdfa98e08a807499b2
    "$docker_cmd" pull "$upstream"
    "$docker_cmd" tag "$upstream" "$image"
  fi
  verify_native_image
  [[ ! -L .workshop && ! -L .workshop/prepared-image ]] || exit 2
  (
    umask 077
    mkdir -p .workshop
    printf '%s\n' "$image" >.workshop/prepared-image.tmp
    mv .workshop/prepared-image.tmp .workshop/prepared-image
  )
  exit 0
fi
if [[ ! -e .env && ! -L .env ]]; then
  [[ $action == start ]] || {
    echo 'No initialized workshop. Use start first.' >&2
    exit 2
  }
  image=${DS60_PINOT_IMAGE:-ds60-apache-pinot-upstream:1.5.1}
  if [[ $requested_binary == true ]]; then
    image=ds60-apache-pinot-binary:1.5.1
  elif [[ -f .workshop/prepared-image && ! -L .workshop && ! -L .workshop/prepared-image ]]; then
    [[ $(wc -c <.workshop/prepared-image) -le 128 ]] || exit 2
    image=$(cat .workshop/prepared-image)
  fi
  [[ $image == ds60-apache-pinot-upstream:1.5.1 || $image == ds60-apache-pinot-binary:1.5.1 ]] || {
    echo 'Use a local versioned Pinot workshop image.' >&2
    exit 2
  }
  verify_native_image
  saved_image=$image
  image=ds60sqlpy-worker-data-platforms-python:1.3.0
  verify_native_image
  image=$saved_image
  owner=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
  [[ $owner =~ ^[a-f0-9]{32}$ ]] || {
    echo 'Could not create an ownership marker.' >&2
    exit 2
  }
  (
    umask 077
    printf '%s\n' "DS60_WORKSHOP_OWNER=$owner" "DS60_WORKSHOP_PROJECT=ds60-apache-pinot-${owner:0:12}" \
      "DS60_PINOT_IMAGE=$image" "DS60_PLATFORM_IMAGE=ds60sqlpy-worker-data-platforms-python:1.3.0" >.env
  )
fi
[[ -f .env && ! -L .env ]] || {
  echo 'The environment must be a regular owned file.' >&2
  exit 2
}
owner='' project='' image=''
platform_image=
while IFS='=' read -r key value; do
  case "$key" in
    DS60_WORKSHOP_OWNER)
      [[ -z $owner && $value =~ ^[a-f0-9]{32}$ ]] || exit 2
      owner=$value
      ;;
    DS60_WORKSHOP_PROJECT)
      [[ -z $project && $value =~ ^ds60-apache-pinot-[a-f0-9]{12}$ ]] || exit 2
      project=$value
      ;;
    DS60_PINOT_IMAGE)
      [[ -z $image && ($value == ds60-apache-pinot-upstream:1.5.1 || $value == ds60-apache-pinot-binary:1.5.1) ]] || exit 2
      image=$value
      ;;
    DS60_PLATFORM_IMAGE)
      [[ -z $platform_image && $value =~ ^ds60sqlpy-worker-data-platforms-python:[0-9]+\.[0-9]+\.[0-9]+$ ]] || exit 2
      platform_image=$value
      ;;
    *)
      echo 'Unknown environment field; no Docker mutation taken.' >&2
      exit 2
      ;;
  esac
done <.env
[[ -n $owner && $project == ds60-apache-pinot-${owner:0:12} && -n $image ]] || {
  echo 'Incomplete or mismatched workshop identity.' >&2
  exit 2
}
[[ $requested_binary == false || $image == ds60-apache-pinot-binary:1.5.1 ]] || {
  echo 'Saved route differs; use a fresh owned copy rather than switching it automatically.' >&2
  exit 2
}
case "$action" in
  start) verify_selected_image "$image" ;;
  initialize)
    verify_selected_image "$image"
    verify_selected_image "$platform_image"
    ;;
  check | identity) verify_selected_image "$platform_image" ;;
esac
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
    [[ $actual == "$owner|apache-pinot" ]] || {
      echo 'Ownership mismatch; no action taken.' >&2
      exit 2
    }
  done
done
export DS60_WORKSHOP_OWNER="$owner" DS60_WORKSHOP_PROJECT="$project" DS60_PINOT_IMAGE="$image" DS60_PLATFORM_IMAGE="$platform_image"
compose=("$docker_cmd" compose --env-file .env -p "$project" -f compose.yaml)
services=(zookeeper controller broker server)
wait_retained() {
  local deadline=$((SECONDS + 180)) complete state index
  while ((SECONDS < deadline)); do
    complete=true
    for index in "${!retained[@]}"; do
      state=$("$docker_cmd" inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "${retained[$index]}")
      if [[ $state != 'running|healthy' ]]; then complete=false; fi
      if [[ $state == exited\|* || $state == dead\|* || $state == running\|none ]]; then
        echo 'A retained node failed its health contract; inspect logs.' >&2
        return 2
      fi
    done
    if [[ $complete == true ]]; then
      for index in "${!retained[@]}"; do
        [[ $("${compose[@]}" ps -aq "${services[$index]}") == "${retained[$index]}" ]] || {
          echo 'A retained node identity changed; no automatic replay occurred.' >&2
          return 2
        }
      done
      return 0
    fi
    sleep 1
  done
  echo 'Retained nodes did not become healthy within their deadline.' >&2
  return 2
}
retained_ids() {
  local service current
  retained=()
  for service in "${services[@]}"; do
    current=$("${compose[@]}" ps -aq "$service")
    [[ $current =~ ^[a-f0-9]{64}$ ]] || {
      echo 'Expected one retained container per saved node. Use start over retained data if containers were removed.' >&2
      return 2
    }
    retained+=("$current")
  done
}

case "$action" in
  start)
    verify_native_image
    # Start the dependency graph in explicit role order.
    for service in "${services[@]}"; do
      "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 180 "$service"
    done
    echo 'Pinot is healthy on its private CQL endpoints. Use run.sh check.'
    ;;
  resume)
    retained_ids
    "${compose[@]}" start "${services[@]}"
    wait_retained
    echo 'The exact saved Pinot containers are healthy.'
    ;;
  check | identity) "${compose[@]}" run --rm --pull never --no-deps -T client check ;;
  initialize)
    plan=$("${compose[@]}" run --rm --pull never --no-deps -T client plan)
    if [[ $plan == absent ]]; then
      "${compose[@]}" run --rm --pull never --no-deps -T client create
      "${compose[@]}" run --rm --pull never --no-deps -T ingest
    elif [[ $plan != ready ]]; then
      echo 'Unexpected initialization state; no replay occurred.' >&2
      exit 2
    fi
    "${compose[@]}" run --rm --pull never --no-deps -T client check
    ;;
  stop) "${compose[@]}" stop "${services[@]}" ;;
  down) "${compose[@]}" down ;;
  destroy) "${compose[@]}" down --volumes ;;
  status) "${compose[@]}" ps ;;
  logs) "${compose[@]}" logs --no-color --tail 100 "${services[@]}" ;;
esac
