#!/usr/bin/env bash
set -euo pipefail
cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")"
action=${1:-help}
if [[ $# -gt 0 ]]; then shift; fi
if [[ $action == help || $action == --help ]]; then
  cat <<'HELP'
Owned data-product workshop (Docker only; Windows uses WSL 2)
  ./run.sh start             Initialize/start from an existing native image
  ./run.sh stop              Stop this API, retaining all local state
  ./run.sh resume            Start the exact existing API container
  ./run.sh replace           Replace the API from its saved image; retain state
  ./run.sh down              Remove these containers/networks; retain state
  ./run.sh status            Show this project's containers
  ./run.sh logs              Follow this API's logs
  ./run.sh ingest FILE.json  Send fixtures/FILE.json through real local HTTP
  ./run.sh snapshots         List accepted raw snapshot receipts
  ./run.sh snapshot ID       Read the retained raw snapshot and receipt
  ./run.sh product           Read and verify the active product through HTTP
  ./run.sh publish ID        Validate, prepare and activate an analytical product
  ./run.sh publish ID --failpoint before-pointer|after-pointer
  ./run.sh recover           Reconcile observations; never auto-activate candidates
  ./run.sh history           Read retained publication observations
  ./run.sh rollback VERSION --reason TEXT
  ./run.sh configure-port PORT  Change the saved port only after down
Initial options: DS60_PRODUCT_PORT=8894
  DS60_PRODUCT_IMAGE=ds60sqlpy-worker-data-engineering:1.2.0
Images are never built or pulled here. State stays in this copy's .workshop/.
HELP
  exit 0
fi
case $action in start | stop | resume | replace | down | status | logs | ingest | snapshots | snapshot | product | publish | recover | history | rollback | configure-port) ;; *)
  echo 'Unknown action. Use ./run.sh help.' >&2
  exit 2
  ;;
esac
case $action in
  start | stop | resume | replace | down | status | logs | snapshots | product | recover | history)
    [[ $# == 0 ]] || {
      echo 'This action takes no additional arguments.' >&2
      exit 2
    }
    ;;
  ingest | snapshot | configure-port)
    [[ $# == 1 ]] || {
      echo 'This action requires exactly one value.' >&2
      exit 2
    }
    ;;
  publish)
    [[ $# == 1 || ($# == 3 && $2 == --failpoint && ($3 == before-pointer || $3 == after-pointer)) ]] || {
      echo 'Use publish ID [--failpoint before-pointer|after-pointer].' >&2
      exit 2
    }
    ;;
  rollback)
    [[ $# == 3 && $2 == --reason && -n $3 ]] || {
      echo 'Use rollback VERSION --reason TEXT.' >&2
      exit 2
    }
    ;;
esac
docker_cmd=$(command -v docker || true)
if [[ -z $docker_cmd && -x ${HOME}/.rd/bin/docker ]]; then docker_cmd=${HOME}/.rd/bin/docker; fi
[[ -n $docker_cmd ]] || {
  echo 'Install/start a Linux-container Docker engine first.' >&2
  exit 2
}
endpoint=${DOCKER_HOST:-}
if [[ -n ${DOCKER_CONTEXT:-} ]]; then
  endpoint=$("$docker_cmd" context inspect --format '{{(index .Endpoints "docker").Host}}' -- "$DOCKER_CONTEXT")
elif [[ -z $endpoint ]]; then
  endpoint=$("$docker_cmd" context inspect --format '{{(index .Endpoints "docker").Host}}')
fi
[[ $endpoint == unix://* ]] || {
  echo 'Use a local Unix Docker socket; run Windows commands from WSL 2.' >&2
  exit 2
}
engine=$("$docker_cmd" info --format '{{.OSType}}|{{.Architecture}}')
case $engine in linux\|aarch64 | linux\|arm64) architecture=arm64 ;; linux\|x86_64 | linux\|amd64) architecture=amd64 ;; *)
  echo 'Use a supported native Linux ARM64 or AMD64 engine; no automatic emulation.' >&2
  exit 2
  ;;
esac
[[ ! -L .workshop ]] || {
  echo '.workshop cannot be a symbolic link.' >&2
  exit 2
}
lock=.workshop/action.lock
lock_held=false
release_lock() {
  if [[ -d $lock && ! -L $lock && -f $lock/pid && ! -L $lock/pid && $(cat "$lock/pid") == "$$" ]]; then
    rm -f "$lock/pid"
    rmdir "$lock"
  fi
}
take_lock() {
  mkdir "$lock" 2>/dev/null || {
    echo 'Another workshop action holds the local lock; inspect its saved PID before recovery.' >&2
    exit 2
  }
  printf '%s\n' "$$" >"$lock/pid"
  lock_held=true
  trap release_lock EXIT
}
if [[ ! -e .workshop/settings.env ]]; then
  [[ $action == start ]] || {
    echo 'This copy has no saved workshop. Run ./run.sh start first.' >&2
    exit 2
  }
  image_ref=${DS60_PRODUCT_IMAGE:-ds60sqlpy-worker-data-engineering:1.2.0}
  port=${DS60_PRODUCT_PORT:-8894}
  [[ $image_ref =~ ^[A-Za-z0-9][A-Za-z0-9._/:@-]+$ ]] || exit 2
  [[ $port =~ ^[1-9][0-9]{3,4}$ && $port -ge 1024 && $port -le 65535 ]] || {
    echo 'Choose a port from 1024 through 65535.' >&2
    exit 2
  }
  selected=$("$docker_cmd" image inspect --format '{{.Id}}|{{.Os}}|{{.Architecture}}' "$image_ref") || {
    echo 'Prepare the data-engineering classroom image first, or select an already pulled Hub image.' >&2
    echo 'From the classroom root: ./classroom build --profile data-engineering --local-build' >&2
    exit 2
  }
  IFS='|' read -r image_id image_os image_arch <<<"$selected"
  [[ $image_os == linux && $image_arch == "$architecture" ]] || {
    echo 'Image and native engine architectures differ.' >&2
    exit 2
  }
  umask 077
  mkdir -p .workshop/raw .workshop/published .workshop/control .workshop/private
  take_lock
  if [[ ! -e .workshop/settings.env ]]; then
    owner=$("$docker_cmd" run --rm --pull never --network none --read-only --cap-drop ALL --security-opt no-new-privileges --entrypoint python "$image_id" -c 'import secrets;print(secrets.token_hex(16))')
    ids=$("$docker_cmd" run --rm --pull never --network none --read-only --cap-drop ALL --security-opt no-new-privileges --mount "type=bind,src=$PWD/.workshop,dst=/prepared" --entrypoint python "$image_id" -c 'import os; s=os.stat("/prepared"); print(str(s.st_uid)+":"+str(s.st_gid))')
    IFS=':' read -r user_id group_id <<<"$ids"
    project=ds60-data-product-${owner:0:12}
    printf '%s\n' 'DS60_PRODUCT_CONFIG_VERSION=1' "DS60_PRODUCT_OWNER=$owner" "DS60_PRODUCT_PROJECT=$project" "DS60_PRODUCT_IMAGE_REF=$image_ref" "DS60_PRODUCT_IMAGE_ID=$image_id" "DS60_PRODUCT_ARCH=$architecture" "DS60_PRODUCT_PORT=$port" "DS60_PRODUCT_UID=$user_id" "DS60_PRODUCT_GID=$group_id" >.workshop/settings.env
  fi
fi
case $action in
  logs | status | snapshots | snapshot | product | history) ;;
  *) [[ $lock_held == true ]] || take_lock ;;
esac
[[ ! -L .workshop/settings.env && -f .workshop/settings.env ]] || exit 2
seen='|'
while IFS='=' read -r key value; do
  [[ $seen != *"|$key|"* ]] || {
    echo 'Duplicate saved setting.' >&2
    exit 2
  }
  seen="$seen$key|"
  case $key in
    DS60_PRODUCT_CONFIG_VERSION) config=$value ;; DS60_PRODUCT_OWNER) owner=$value ;;
    DS60_PRODUCT_PROJECT) project=$value ;; DS60_PRODUCT_IMAGE_REF) image_ref=$value ;;
    DS60_PRODUCT_IMAGE_ID) image_id=$value ;; DS60_PRODUCT_ARCH) saved_arch=$value ;;
    DS60_PRODUCT_PORT) port=$value ;; DS60_PRODUCT_UID) user_id=$value ;; DS60_PRODUCT_GID) group_id=$value ;;
    *)
      echo 'Unexpected saved setting; no action taken.' >&2
      exit 2
      ;;
  esac
done <.workshop/settings.env
[[ ${config:-} == 1 && ${owner:-} =~ ^[0-9a-f]{32}$ && ${project:-} == ds60-data-product-${owner:0:12} ]] || {
  echo 'Saved ownership is invalid.' >&2
  exit 2
}
[[ ${image_id:-} =~ ^sha256:[0-9a-f]{64}$ && ${image_ref:-} =~ ^[A-Za-z0-9][A-Za-z0-9._/:@-]+$ && ${saved_arch:-} == "$architecture" ]] || exit 2
[[ ${port:-} =~ ^[1-9][0-9]{3,4}$ && $port -ge 1024 && $port -le 65535 && ${user_id:-} =~ ^[0-9]+$ && ${group_id:-} =~ ^[0-9]+$ ]] || exit 2
for path in .workshop/raw .workshop/published .workshop/control .workshop/private; do
  [[ -d $path && ! -L $path ]] || {
    echo 'Owned state directory is absent or linked.' >&2
    exit 2
  }
done
saved_platform=$("$docker_cmd" image inspect --format '{{.Os}}|{{.Architecture}}' "$image_id") || {
  echo 'The saved native image is absent; no build or pull attempted.' >&2
  exit 2
}
[[ $saved_platform == "linux|$architecture" ]] || exit 2
owned=$("$docker_cmd" ps -a --filter "label=com.docker.compose.project=$project" --format '{{.ID}}|{{.Label "ds60.workshop.kind"}}|{{.Label "ds60.workshop.owner"}}|{{.Label "com.docker.compose.project.working_dir"}}') || {
  echo 'Could not verify ownership; no action taken.' >&2
  exit 2
}
while IFS='|' read -r container kind stored_owner directory; do
  [[ -n $container ]] || continue
  [[ $kind == data-product && $stored_owner == "$owner" && $directory == "$PWD" ]] || {
    echo 'Project resources belong to a different owned copy.' >&2
    exit 2
  }
done <<<"$owned"
network_ids=$("$docker_cmd" network ls -q --filter "label=com.docker.compose.project=$project") || {
  echo 'Could not verify network ownership; no action taken.' >&2
  exit 2
}
for network_id in $network_ids; do
  labels=$("$docker_cmd" network inspect --format '{{index .Labels "ds60.workshop.kind"}}|{{index .Labels "ds60.workshop.owner"}}' "$network_id") || exit 2
  [[ $labels == "data-product|$owner" ]] || {
    echo 'A project network has different ownership; no action taken.' >&2
    exit 2
  }
done
if [[ $action == configure-port ]]; then
  [[ $# == 1 && $1 =~ ^[1-9][0-9]{3,4}$ && $1 -ge 1024 && $1 -le 65535 && -z $owned ]] || {
    echo 'Use configure-port PORT only after ./run.sh down.' >&2
    exit 2
  }
  port=$1
  printf '%s\n' 'DS60_PRODUCT_CONFIG_VERSION=1' "DS60_PRODUCT_OWNER=$owner" "DS60_PRODUCT_PROJECT=$project" "DS60_PRODUCT_IMAGE_REF=$image_ref" "DS60_PRODUCT_IMAGE_ID=$image_id" "DS60_PRODUCT_ARCH=$architecture" "DS60_PRODUCT_PORT=$port" "DS60_PRODUCT_UID=$user_id" "DS60_PRODUCT_GID=$group_id" >.workshop/settings.env
  echo 'Saved port updated; start will reuse the same image and state.'
  exit 0
fi
export DS60_PRODUCT_OWNER="$owner" DS60_PRODUCT_PROJECT="$project" DS60_PRODUCT_IMAGE_ID="$image_id" DS60_PRODUCT_PORT="$port" DS60_PRODUCT_UID="$user_id" DS60_PRODUCT_GID="$group_id"
compose=("$docker_cmd" compose --project-name "$project" --env-file .workshop/settings.env -f compose.yaml)
if [[ $action == start ]]; then
  "$docker_cmd" run --rm --pull never --network none --read-only --user "$user_id:$group_id" --cap-drop ALL --security-opt no-new-privileges --cpus 2 --memory 2g --pids-limit 128 --tmpfs /tmp:rw,mode=1777,size=128m --mount "type=bind,src=$PWD/product,dst=/opt/product,readonly" --mount "type=bind,src=$PWD/.workshop,dst=/state" --env PYTHONPATH=/opt:/opt/worker/src --env "DS60_PRODUCT_OWNER=$owner" --env "DS60_PRODUCT_IMAGE_ID=$image_id" --entrypoint python "$image_id" -m product.tool initialize
  "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 90 api
  echo "API ready at http://127.0.0.1:$port; use ./run.sh ingest baseline.json"
elif [[ $action == resume ]]; then
  original=$("${compose[@]}" ps -aq api)
  [[ $original =~ ^[0-9a-f]{64}$ ]] || {
    echo 'No single existing API container. Use start to create from the saved image.' >&2
    exit 2
  }
  "${compose[@]}" start api
  deadline=$((SECONDS + 90))
  while :; do
    state=$("$docker_cmd" inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}' "$original")
    [[ $state == running\|healthy ]] && break
    [[ $state != exited\|* && $state != dead\|* && $state != *\|unhealthy && $SECONDS -lt $deadline ]] || {
      echo 'The retained API did not become healthy; inspect logs.' >&2
      exit 2
    }
    sleep 1
  done
  [[ $("${compose[@]}" ps -aq api) == "$original" ]] || exit 2
  echo 'Exact API container resumed; saved image and state retained.'
elif [[ $action == replace ]]; then
  "${compose[@]}" up -d --force-recreate --no-build --pull never --wait --wait-timeout 90 api
elif [[ $action == stop ]]; then
  "${compose[@]}" stop api
elif [[ $action == down ]]; then
  "${compose[@]}" down
elif [[ $action == status ]]; then
  "${compose[@]}" ps -a
elif [[ $action == logs ]]; then
  "${compose[@]}" logs --follow api
elif [[ $action == ingest || $action == snapshots || $action == snapshot || $action == product ]]; then
  "${compose[@]}" --profile tools run --rm --no-deps --pull never client "$action" "$@"
else
  "${compose[@]}" --profile tools run --rm --no-deps --pull never publisher "$action" "$@"
fi
