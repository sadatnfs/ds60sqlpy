#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
action=${1:-help}
[[ $# -le 1 ]] || {
  echo 'Unexpected arguments; no action taken.' >&2
  exit 2
}
case "$action" in
  plan | apply | check | prepare) ;;
  start | resume | down | destroy)
    echo 'No local Atlas server is admitted. Prepare a separately owned supported native Atlas2.5.0/Java8 graph/index host; see PREPARATION.md. No emulation or substitute server was started.' >&2
    exit 2
    ;;
  help | --help | -h)
    echo 'Use prepare, plan, apply, or check. Server lifecycle is separately prepared on the explicitly owned native host.'
    exit 0
    ;;
  *)
    echo 'Unknown action; no action taken.' >&2
    exit 2
    ;;
esac
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
    echo 'Use a native Linux Docker engine.' >&2
    exit 2
    ;;
esac
image=ds60sqlpy-worker-data-platforms-python:1.1.0
actual=$("$docker_cmd" image inspect --format '{{.Os}}|{{.Architecture}}' "$image")
[[ $actual == "$engine" ]] || {
  echo 'Prepare the native data-platforms-python image. Automatic emulation is disabled.' >&2
  exit 2
}
if [[ $action == prepare ]]; then
  echo 'Native portable client is prepared. No Atlas server build or contact occurred.'
  exit 0
fi
[[ ! -L .workshop && ! -L .workshop/owner && ! -L .workshop/lock ]] || exit 2
(
  umask 077
  mkdir -p .workshop
)
mkdir .workshop/lock 2>/dev/null || {
  echo 'Another owned action holds the workshop lock.' >&2
  exit 2
}
printf '%s\n' "$$" >.workshop/lock/pid
release_lock() {
  if [[ -f .workshop/lock/pid && ! -L .workshop/lock/pid && $(cat .workshop/lock/pid) == "$$" ]]; then
    rm .workshop/lock/pid
    rmdir .workshop/lock
  fi
}
trap release_lock EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
if [[ ! -e .workshop/owner ]]; then
  [[ $action == plan ]] || {
    echo 'Use plan first to establish an owned namespace.' >&2
    exit 2
  }
  (
    umask 077
    od -An -N16 -tx1 /dev/urandom | tr -d ' \n' >.workshop/owner
  )
fi
owner=$(cat .workshop/owner)
[[ $owner =~ ^[a-f0-9]{32}$ ]] || exit 2
args=()
if [[ $action != plan ]]; then
  [[ -f .workshop/atlas.env && ! -L .workshop/atlas.env ]] || {
    echo 'Provide the untracked fixture credential environment file described in README.' >&2
    exit 2
  }
  seen='|'
  while IFS='=' read -r key value || [[ -n $key ]]; do
    case "$key" in
      DS60_ATLAS_ENDPOINT | DS60_ATLAS_USERNAME | DS60_ATLAS_PASSWORD)
        [[ $seen != *"|$key|"* && -n $value && $value != *$'\r'* ]] || {
          echo 'Duplicate or malformed private environment field.' >&2
          exit 2
        }
        seen+="$key|"
        ;;
      *)
        echo 'Unexpected private environment field; no server contact occurred.' >&2
        exit 2
        ;;
    esac
  done <.workshop/atlas.env
  args+=(--env-file "$PWD/.workshop/atlas.env")
fi
"$docker_cmd" run --rm --pull never --network bridge --memory 256m --cpus 0.5 \
  --pids-limit 128 --label "org.ds60.workshop.owner=$owner" --label "org.ds60.workshop.kind=apache-atlas-client" \
  "${args[@]}" --env "DS60_ATLAS_OWNER=$owner" --mount "type=bind,source=$PWD/client.py,target=/project/client.py,readonly" \
  --entrypoint python3 "$image" /project/client.py "$action"
