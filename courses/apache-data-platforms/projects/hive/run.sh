#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
cd "$project_dir"
action=${1:-start}
if [[ $# -gt 0 ]]; then shift; fi
requested_mirror=false
if [[ $action == prepare && $# == 1 && $1 == --mirror ]]; then
  requested_mirror=true
  shift
fi
case "$action" in
  prepare | start-db | initialize-schema | verify-schema | metadata | explain | start | resume | stop | down | status | logs | check | initialize | identity)
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
    echo 'Use prepare [--mirror], start-db, initialize-schema, verify-schema, start, initialize, check, metadata, explain, identity, stop, resume, down, status, logs, or destroy --confirm-owned-data-loss.'
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
    echo 'Prepare the native Hive workshop image first.' >&2
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
  image=ds60-apache-hive-upstream:4.2.1
  engine=$("$docker_cmd" info --format '{{.OSType}}|{{.Architecture}}')
  case "$engine" in
    'linux|aarch64' | 'linux|arm64' | 'linux|x86_64' | 'linux|amd64') ;;
    *)
      echo 'Use native Linux AMD64 or ARM64; automatic emulation is disabled.' >&2
      exit 2
      ;;
  esac
  requested_image=$image
  for image in ds60sqlpy-worker-java21:1.3.0 ds60sqlpy-worker-data-platforms-python:1.3.0; do verify_native_image; done
  image=$requested_image
  upstream=apache/hive@sha256:b19bb5bd01f233a3f99d941ebf08acaff68c55911dd5fa42ea03928e51860b91
  postgres_upstream=postgres@sha256:00bc86618629af00d2937fdc5a5d63db3ff8450acf52f0636ec813c7f4902929
  if [[ $requested_mirror == true ]]; then
    # The mirror may retain native images without all index attestations.
    # These are the already reviewed children of the same pinned indexes.
    case "$engine" in
      'linux|aarch64' | 'linux|arm64')
        upstream=mirror.gcr.io/apache/hive@sha256:feda444e4e2a873ee08e9d9a5c3ad507ea72e5242d47ef0cf530298e9d6bff13
        postgres_upstream=mirror.gcr.io/library/postgres@sha256:ac74e8c63c516b1f81fbaaede0663981399f80e42369431136b2455557f8547b
        ;;
      'linux|x86_64' | 'linux|amd64')
        upstream=mirror.gcr.io/apache/hive@sha256:ec5d9c344d2b1d020fcf2d8a84408b6bd38be8eea0713b1df31243830d3535ee
        postgres_upstream=mirror.gcr.io/library/postgres@sha256:b86568d3e0fe1dfaeff52714f9da36f206a30e4c49131b82bf96982d78627409
        ;;
    esac
  fi
  "$docker_cmd" pull "$upstream"
  "$docker_cmd" tag "$upstream" "$image"
  "$docker_cmd" pull "$postgres_upstream"
  "$docker_cmd" tag "$postgres_upstream" ds60-apache-hive-postgres:17.6
  verify_native_image
  [[ ! -L .workshop ]] || exit 2
  mkdir -p .workshop
  "$docker_cmd" run --rm --pull never --network bridge --memory 256m --cpus 0.5 --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
    --mount "type=bind,source=$project_dir/prepare_jdbc.py,target=/project/prepare_jdbc.py,readonly" \
    --mount "type=bind,source=$project_dir/.workshop,target=/project/.workshop" \
    --entrypoint python3 ds60sqlpy-worker-data-platforms-python:1.3.0 /project/prepare_jdbc.py
  bash prepare-metadata.sh "$image" ds60sqlpy-worker-java21:1.3.0
  exit 0
fi
if [[ ! -e .env && ! -L .env ]]; then
  [[ $action == start || $action == start-db ]] || {
    echo 'No initialized workshop. Use start first.' >&2
    exit 2
  }
  image=${DS60_HIVE_IMAGE:-ds60-apache-hive-upstream:4.2.1}
  [[ $image =~ ^ds60-apache-hive-upstream:4\.2\.1$ ]] || {
    echo 'Use a local versioned Hive workshop image.' >&2
    exit 2
  }
  verify_native_image
  saved_image=$image
  image=ds60sqlpy-worker-data-platforms-python:1.3.0
  verify_native_image
  image=$saved_image
  verify_selected_image ds60-apache-hive-postgres:17.6
  owner=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
  [[ $owner =~ ^[a-f0-9]{32}$ ]] || {
    echo 'Could not create an ownership marker.' >&2
    exit 2
  }
  (
    umask 077
    printf '%s\n' "DS60_WORKSHOP_OWNER=$owner" "DS60_WORKSHOP_PROJECT=ds60-apache-hive-${owner:0:12}" \
      "DS60_HIVE_IMAGE=$image" "DS60_PLATFORM_IMAGE=ds60sqlpy-worker-data-platforms-python:1.3.0" "DS60_POSTGRES_IMAGE=ds60-apache-hive-postgres:17.6" >.env
  )
fi
[[ -f .env && ! -L .env && $(wc -c <.env) -le 4096 ]] || {
  echo 'The environment must be a regular owned file.' >&2
  exit 2
}
owner='' project='' image='' postgres_image=''
platform_image=
while IFS='=' read -r key value; do
  case "$key" in
    DS60_WORKSHOP_OWNER)
      [[ -z $owner && $value =~ ^[a-f0-9]{32}$ ]] || exit 2
      owner=$value
      ;;
    DS60_WORKSHOP_PROJECT)
      [[ -z $project && $value =~ ^ds60-apache-hive-[a-f0-9]{12}$ ]] || exit 2
      project=$value
      ;;
    DS60_HIVE_IMAGE)
      [[ -z $image && $value =~ ^ds60-apache-hive-upstream:4\.2\.1$ ]] || exit 2
      image=$value
      ;;
    DS60_POSTGRES_IMAGE)
      [[ -z $postgres_image && $value == ds60-apache-hive-postgres:17.6 ]] || exit 2
      postgres_image=$value
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
[[ -n $owner && $project == ds60-apache-hive-${owner:0:12} && -n $image && -n $platform_image && -n $postgres_image ]] || {
  echo 'Incomplete or mismatched workshop identity.' >&2
  exit 2
}
case "$action" in
  start | start-db)
    verify_selected_image "$image"
    verify_selected_image ds60-apache-hive-postgres:17.6
    ;;
  initialize)
    verify_selected_image "$image"
    verify_selected_image "$platform_image"
    ;;
  check | identity | metadata | explain | initialize-schema | verify-schema)
    verify_selected_image "$image"
    ;;
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
    [[ $actual == "$owner|apache-hive" ]] || {
      echo 'Ownership mismatch; no action taken.' >&2
      exit 2
    }
  done
done
export DS60_WORKSHOP_OWNER="$owner" DS60_WORKSHOP_PROJECT="$project" DS60_HIVE_IMAGE="$image" DS60_PLATFORM_IMAGE="$platform_image" DS60_POSTGRES_IMAGE=ds60-apache-hive-postgres:17.6
compose=("$docker_cmd" compose --env-file .env -p "$project" -f compose.yaml)
services=(postgres metastore hiveserver2)
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
  start | initialize-schema | verify-schema | metadata | explain | initialize | check | identity)
    [[ ! -L .workshop && -f .workshop/postgresql.jar && ! -L .workshop/postgresql.jar && $(wc -c <.workshop/postgresql.jar) -le 2000000 ]] || {
      echo 'Prepare the pinned regular JDBC artifact explicitly; no service was started.' >&2
      exit 2
    }
    ;;
esac
case "$action" in
  start)
    verify_native_image
    # Start the dependency graph in explicit role order.
    for service in "${services[@]}"; do
      "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 180 "$service"
    done
    echo 'Hive Metastore and HiveServer2 are healthy on private endpoints. Use run.sh check.'
    ;;
  resume)
    retained_ids
    "${compose[@]}" start "${services[@]}"
    wait_retained
    echo 'The exact saved Hive containers are healthy.'
    ;;
  start-db) "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 120 postgres ;;
  initialize-schema) "${compose[@]}" run --rm --pull never --no-deps -T admin init-schema ;;
  verify-schema) "${compose[@]}" run --rm --pull never --no-deps -T admin verify-schema ;;
  metadata)
    [[ -f .workshop/metadata-client/identity.tsv && ! -L .workshop && ! -L .workshop/metadata-client && ! -e .workshop/preparation.owner ]] || {
      echo 'Prepare or reconcile the native metadata client explicitly first.' >&2
      exit 2
    }
    runtime_id=$("$docker_cmd" image inspect --format '{{.Id}}' "$image")
    [[ $runtime_id =~ ^sha256:[a-f0-9]{64}$ ]] || exit 2
    "${compose[@]}" run --rm --pull never --no-deps -T --env "DS60_HIVE_RUNTIME_IMAGE_ID=$runtime_id" admin metadata
    ;;
  explain) "${compose[@]}" run --rm --pull never --no-deps --no-tty=false --interactive=false admin explain ;;
  initialize)
    "${compose[@]}" run --rm --pull never --no-deps -T fixture
    "${compose[@]}" run --rm --pull never --no-deps --no-tty=false --interactive=false admin initialize
    ;;
  check | identity)
    if ! raw_output=$("${compose[@]}" run --rm --pull never --no-deps --no-tty=false --interactive=false admin query 2>&1); then
      printf '%s\n' "$raw_output" >&2
      echo 'Actual Hive SQL query failed; no source was replayed.' >&2
      exit 2
    fi
    output=$(printf '%s\n' "$raw_output" | tr -d '\r' | awk -F '\t' 'NF == 3')
    [[ $output == $'1\teast\t4\n2\twest\t9\n3\teast\t7' ]] || {
      echo 'Retained Hive rows differ; no initialization occurred.' >&2
      exit 2
    }
    if invalid=$("${compose[@]}" run --rm --pull never --no-deps --no-tty=false --interactive=false admin negative 2>&1); then
      echo 'Invalid column unexpectedly succeeded.' >&2
      exit 2
    elif [[ $invalid != *10004* || $invalid != *absent_field* ]]; then
      echo 'The negative request failed for a different reason; expected Hive10004 for absent_field.' >&2
      exit 2
    fi
    printf '{"passed":true,"actual_hive_sql":true,"exact_rows":3,"invalid_column_rejected":true,"read_only_no_initialization":true}\n'
    ;;
  stop) "${compose[@]}" stop "${services[@]}" ;;
  down) "${compose[@]}" down ;;
  destroy) "${compose[@]}" down --volumes ;;
  status) "${compose[@]}" ps ;;
  logs) "${compose[@]}" logs --no-color --tail 100 "${services[@]}" ;;
esac
