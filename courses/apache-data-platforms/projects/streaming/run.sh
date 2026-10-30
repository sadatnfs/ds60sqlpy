#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
cd "$project_dir"
action=${1:-start}
if [[ $# -gt 0 ]]; then shift; fi
requested_route=
if [[ $# == 1 && $1 == --binary && ($action == prepare || $action == start) ]]; then
  requested_route=binary
  shift
fi
case "$action" in
  prepare | start | resume | stop | down | status | logs | check | check-transactions | check-consumers | check-retention | check-schema)
    [[ $# == 0 ]] || {
      echo 'Unexpected arguments; no action taken.' >&2
      exit 2
    }
    ;;
  destroy)
    [[ $# == 1 && $1 == --confirm-owned-data-loss ]] || {
      echo 'Use destroy --confirm-owned-data-loss to delete this workshop data.' >&2
      exit 2
    }
    ;;
  help | --help | -h)
    echo 'Use prepare [--binary], start [--binary], resume, stop, down, status, logs, check, check-transactions, check-consumers, check-retention, check-schema, or destroy --confirm-owned-data-loss.'
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
  echo 'Use a local Unix-socket Docker context for this workshop.' >&2
  exit 2
}
upstream_image=apache/kafka:4.4.0@sha256:833b867a9585a141da455dc2b57431c65cbccb27f11c91f694444cca9f777e0f
binary_image=ds60-apache-kafka-binary:4.4.0
route=${requested_route:-upstream}
image=$upstream_image
if [[ $route == binary ]]; then image=$binary_image; fi
engine=$("$docker_cmd" info --format '{{.OSType}}|{{.Architecture}}')
case "$engine" in
  'linux|amd64' | 'linux|x86_64') architecture=amd64 ;;
  'linux|arm64' | 'linux|aarch64') architecture=arm64 ;;
  *)
    echo 'This pinned workshop supports native Linux AMD64 and ARM64 only. Use a supported native host; automatic emulation is disabled.' >&2
    exit 2
    ;;
esac
verify_image() {
  local actual
  actual=$("$docker_cmd" image inspect --format '{{.Os}}|{{.Architecture}}' "$image") || {
    echo 'Run prepare explicitly to obtain the pinned native image.' >&2
    return 2
  }
  [[ $actual == "linux|$architecture" ]] || {
    echo 'Image and native engine architectures differ; automatic emulation is disabled.' >&2
    return 2
  }
}
if [[ $action == prepare ]]; then
  if [[ $route == binary ]]; then
    base=${DS60_JAVA_IMAGE:-ds60sqlpy-worker-java21:1.3.0}
    [[ $base =~ ^ds60sqlpy-worker-java21:[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
      echo 'Use an existing versioned local Java21 classroom image.' >&2
      exit 2
    }
    base_platform=$("$docker_cmd" image inspect --format '{{.Os}}|{{.Architecture}}' "$base") || {
      echo 'Prepare the native Java21 classroom image before the binary alternative.' >&2
      exit 2
    }
    [[ $base_platform == "linux|$architecture" ]] || {
      echo 'Java base image is not native; automatic emulation is disabled.' >&2
      exit 2
    }
    "$docker_cmd" build --pull=false --progress=plain --build-arg "BASE_IMAGE=$base" \
      --tag "$binary_image" "$project_dir/binary-image"
  else
    "$docker_cmd" pull --platform "linux/$architecture" "$image"
  fi
  verify_image
  exit 0
fi
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
if [[ ! -e .env && ! -L .env ]]; then
  [[ $action == start ]] || {
    echo 'Use start to initialize this owned workshop.' >&2
    exit 2
  }
  verify_image
  owner=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
  cluster=$(dd if=/dev/urandom bs=16 count=1 2>/dev/null | base64 | tr '+/' '-_' | tr -d '=\n')
  [[ $owner =~ ^[a-f0-9]{32}$ && $cluster =~ ^[A-Za-z0-9_-]{22}$ ]] || exit 2
  (
    umask 077
    printf '%s\n' "DS60_WORKSHOP_OWNER=$owner" "DS60_WORKSHOP_PROJECT=ds60-apache-stream-${owner:0:12}" \
      "DS60_KAFKA_CLUSTER_ID=$cluster" "DS60_KAFKA_ROUTE=$route" >.env
  )
fi
[[ -f .env && ! -L .env ]] || {
  echo 'Environment must be a regular file.' >&2
  exit 2
}
owner='' project='' cluster='' route=''
while IFS='=' read -r key value; do
  case "$key" in
    DS60_WORKSHOP_OWNER)
      [[ -z $owner && $value =~ ^[a-f0-9]{32}$ ]] || exit 2
      owner=$value
      ;;
    DS60_WORKSHOP_PROJECT)
      [[ -z $project && $value =~ ^ds60-apache-stream-[a-f0-9]{12}$ ]] || exit 2
      project=$value
      ;;
    DS60_KAFKA_ROUTE)
      [[ -z $route && ($value == upstream || $value == binary) ]] || exit 2
      route=$value
      ;;
    DS60_KAFKA_CLUSTER_ID)
      [[ -z $cluster && $value =~ ^[A-Za-z0-9_-]{22}$ ]] || exit 2
      cluster=$value
      ;;
    *)
      echo 'Unknown environment field; no resource mutation taken.' >&2
      exit 2
      ;;
  esac
done <.env
[[ -n $owner && $project == ds60-apache-stream-${owner:0:12} && -n $cluster && -n $route ]] || {
  echo 'Incomplete or inconsistent workshop identity.' >&2
  exit 2
}
[[ -z $requested_route || $requested_route == "$route" ]] || {
  echo 'The requested image route differs from this saved workshop. No automatic switch performed.' >&2
  exit 2
}
image=$upstream_image
if [[ $route == binary ]]; then image=$binary_image; fi
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
    [[ $actual == "$owner|apache-streaming" ]] || {
      echo 'Ownership mismatch; no action taken.' >&2
      exit 2
    }
  done
done
# Pin reviewed saved values; ambient shell exports must not override ownership.
export "DS60_WORKSHOP_OWNER=$owner" "DS60_WORKSHOP_PROJECT=$project" "DS60_KAFKA_CLUSTER_ID=$cluster" "DS60_KAFKA_ROUTE=$route"
compose=("$docker_cmd" compose --env-file .env -p "$project" -f compose.yaml)
if [[ $route == binary ]]; then compose+=(-f compose.binary.yaml); fi
case "$action" in
  start)
    verify_image
    "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 180 kafka
    ;;
  resume)
    existing=$("${compose[@]}" ps -aq kafka)
    [[ $existing =~ ^[a-f0-9]{12,64}$ ]] || {
      echo 'No single retained container; use start with retained data.' >&2
      exit 2
    }
    "${compose[@]}" start kafka
    healthy=false
    for ((attempt = 0; attempt < 180; attempt++)); do
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
    [[ $healthy == true && $("${compose[@]}" ps -aq kafka) == "$existing" ]] || {
      echo 'Resume did not produce the same healthy container within its deadline.' >&2
      exit 2
    }
    ;;
  check) "${compose[@]}" exec -T kafka bash /project/check-kafka.sh ;;
  check-transactions | check-consumers)
    [[ $route == binary ]] || {
      echo 'The Java client compile step requires the explicit binary route with its prepared JDK.' >&2
      exit 2
    }
    "${compose[@]}" exec -T kafka bash "/project/${action}.sh"
    ;;
  check-retention)
    [[ $route == binary ]] || {
      echo 'The retention Java client requires the explicit binary route with its prepared JDK.' >&2
      exit 2
    }
    "${compose[@]}" exec -T kafka bash /project/check-retention.sh
    ;;
  check-schema)
    [[ $route == binary ]] || {
      echo 'The local validator needs the explicit prepared binary route.' >&2
      exit 2
    }
    "${compose[@]}" exec -T kafka python3 /project/schema_fixture.py
    ;;
  stop) "${compose[@]}" stop kafka ;;
  down) "${compose[@]}" down ;;
  destroy) "${compose[@]}" down --volumes ;;
  status) "${compose[@]}" ps ;;
  logs) "${compose[@]}" logs --no-color --tail 100 kafka ;;
esac
