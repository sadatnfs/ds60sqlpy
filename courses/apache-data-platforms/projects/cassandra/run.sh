#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
cd "$project_dir"
action=${1:-start}
if [[ $# -gt 0 ]]; then shift; fi
requested_topology=
probe_stopped=false
if [[ $# == 1 && $1 == --replicated && $action == start ]]; then
  requested_topology=three
  shift
fi
case "$action" in
  prepare | start | resume | stop | down | status | logs | check | check-backup | check-replication | replica-identity | identity)
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
    echo 'Use prepare, start [--replicated], resume, stop, down, status, logs, check, check-backup, check-replication, replica-identity, identity, or destroy --confirm-owned-data-loss.'
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
    echo 'Prepare the native Cassandra workshop image first.' >&2
    return 2
  }
  [[ $platform == "$engine" ]] || {
    echo 'The local image does not match the native Docker engine architecture.' >&2
    echo 'Prepare the supported native image or use an explicitly selected native host. Automatic emulation is disabled.' >&2
    return 2
  }
}
replica_capacity() {
  local memory
  memory=$("$docker_cmd" info --format '{{.MemTotal}}')
  [[ $memory =~ ^[0-9]+$ && $memory -ge 8589934592 ]] || {
    echo 'The explicit three-node workshop needs at least 8 GiB allocated to the Docker engine. Use the single-node path or increase the engine allocation; other workloads also need capacity.' >&2
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
  if [[ $probe_stopped == true ]]; then
    "${compose[@]}" start cassandra-two cassandra-three >/dev/null || {
      echo 'The interrupted owned outage could not restore its nodes. Inspect status and use resume; no test was replayed.' >&2
    }
  fi
  if [[ -f .workshop-lock/pid && ! -L .workshop-lock/pid && $(cat .workshop-lock/pid) == "$$" ]]; then
    rm .workshop-lock/pid
    rmdir .workshop-lock
  fi
}
trap release_lock EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
if [[ $action == prepare ]]; then
  image=ds60-apache-cassandra-binary:5.0.9
  base=${DS60_CASSANDRA_BASE:-ds60sqlpy-worker-scala-jvm:1.3.0}
  [[ $base =~ ^ds60sqlpy-worker-scala-jvm:[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
    echo 'Use a prepared local versioned Scala/JVM image with Java 17.' >&2
    exit 2
  }
  engine=$("$docker_cmd" info --format '{{.OSType}}|{{.Architecture}}')
  case "$engine" in
    'linux|aarch64' | 'linux|arm64') engine='linux|arm64' ;;
    'linux|x86_64' | 'linux|amd64') engine='linux|amd64' ;;
    *)
      echo 'Use native Linux AMD64 or ARM64; automatic emulation is disabled.' >&2
      exit 2
      ;;
  esac
  actual=$("$docker_cmd" image inspect --format '{{.Os}}|{{.Architecture}}' "$base")
  [[ $actual == "$engine" ]] || {
    echo 'Prepare the native Java 17 base; automatic emulation is disabled.' >&2
    exit 2
  }
  "$docker_cmd" build --pull=false --progress=plain --build-arg "BASE_IMAGE=$base" \
    --tag "$image" "$project_dir/binary-image"
  verify_native_image
  exit 0
fi
if [[ ! -e .env && ! -L .env ]]; then
  [[ $action == start ]] || {
    echo 'No initialized workshop. Use start first.' >&2
    exit 2
  }
  image=${DS60_CASSANDRA_IMAGE:-ds60-apache-cassandra-binary:5.0.9}
  [[ $image =~ ^ds60-apache-cassandra-binary:[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
    echo 'Use a local versioned Cassandra workshop image.' >&2
    exit 2
  }
  verify_native_image
  [[ $requested_topology != three ]] || replica_capacity
  owner=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
  [[ $owner =~ ^[a-f0-9]{32}$ ]] || {
    echo 'Could not create an ownership marker.' >&2
    exit 2
  }
  (
    umask 077
    printf '%s\n' "DS60_WORKSHOP_OWNER=$owner" "DS60_WORKSHOP_PROJECT=ds60-apache-cassandra-${owner:0:12}" \
      "DS60_CASSANDRA_IMAGE=$image" "DS60_CASSANDRA_TOPOLOGY=${requested_topology:-single}" >.env
  )
fi
[[ -f .env && ! -L .env ]] || {
  echo 'The environment must be a regular owned file.' >&2
  exit 2
}
owner='' project='' image=''
topology=single
seen_topology=false
while IFS='=' read -r key value; do
  case "$key" in
    DS60_WORKSHOP_OWNER)
      [[ -z $owner && $value =~ ^[a-f0-9]{32}$ ]] || exit 2
      owner=$value
      ;;
    DS60_WORKSHOP_PROJECT)
      [[ -z $project && $value =~ ^ds60-apache-cassandra-[a-f0-9]{12}$ ]] || exit 2
      project=$value
      ;;
    DS60_CASSANDRA_IMAGE)
      [[ -z $image && $value =~ ^ds60-apache-cassandra-binary:[0-9]+\.[0-9]+\.[0-9]+$ ]] || exit 2
      image=$value
      ;;
    DS60_CASSANDRA_TOPOLOGY)
      [[ $seen_topology == false && ($value == single || $value == three) ]] || exit 2
      topology=$value
      seen_topology=true
      ;;
    *)
      echo 'Unknown environment field; no Docker mutation taken.' >&2
      exit 2
      ;;
  esac
done <.env
[[ -n $owner && $project == ds60-apache-cassandra-${owner:0:12} && -n $image ]] || {
  echo 'Incomplete or mismatched workshop identity.' >&2
  exit 2
}
[[ -z $requested_topology || $requested_topology == "$topology" ]] || {
  echo 'The requested topology differs from saved state. Use a fresh owned copy; no automatic topology change occurred.' >&2
  exit 2
}
if [[ $topology == three && ($action == start || $action == resume || $action == check-replication) ]]; then
  replica_capacity
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
    [[ $actual == "$owner|apache-cassandra" ]] || {
      echo 'Ownership mismatch; no action taken.' >&2
      exit 2
    }
  done
done
export DS60_WORKSHOP_OWNER="$owner" DS60_WORKSHOP_PROJECT="$project" DS60_CASSANDRA_IMAGE="$image" DS60_CASSANDRA_TOPOLOGY="$topology"
compose=("$docker_cmd" compose --env-file .env -p "$project" -f compose.yaml)
services=(cassandra)
if [[ $topology == three ]]; then
  compose+=(-f compose.replicated.yaml)
  services+=(cassandra-two cassandra-three)
fi
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
    # New replicas bootstrap sequentially; do not bypass range-movement safety.
    for service in "${services[@]}"; do
      "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 180 "$service"
    done
    echo 'Cassandra is healthy on its private CQL endpoints. Use run.sh check.'
    ;;
  resume)
    retained_ids
    "${compose[@]}" start "${services[@]}"
    wait_retained
    echo 'The exact saved Cassandra containers are healthy.'
    ;;
  check) "${compose[@]}" run --rm --pull never --no-deps -T client ;;
  check-backup)
    [[ $topology == single ]] || {
      echo 'This bounded SSTable restore checks the single-node topology only; it is not a whole-cluster backup.' >&2
      exit 2
    }
    "${compose[@]}" exec -T cassandra python3 /project/backup.py
    ;;
  identity) "${compose[@]}" run --rm --pull never --no-deps -T client /project/client.py --identity ;;
  replica-identity)
    [[ $topology == three ]] || {
      echo 'Replica identity belongs to the explicit three-node topology.' >&2
      exit 2
    }
    "${compose[@]}" run --rm --pull never --no-deps -T client /project/replication.py inspect
    ;;
  check-replication)
    [[ $topology == three ]] || {
      echo 'Use a fresh explicit start --replicated workshop for the real RF3 outage.' >&2
      exit 2
    }
    retained_ids
    prepared=$("${compose[@]}" run --rm --pull never --no-deps -T client /project/replication.py prepare)
    probe_stopped=true
    "${compose[@]}" stop cassandra-two cassandra-three
    outcome=0
    if ! outage=$("${compose[@]}" run --rm --pull never --no-deps -T client /project/replication.py outage); then
      outcome=1
    fi
    "${compose[@]}" start cassandra-two cassandra-three
    wait_retained
    probe_stopped=false
    [[ $outcome == 0 ]] || {
      echo 'The outage observation failed; original nodes were resumed and the test was not replayed.' >&2
      exit 2
    }
    recovered=$("${compose[@]}" run --rm --pull never --no-deps -T client /project/replication.py recovered)
    printf '{"passed":true,"prepare":%s,"outage":%s,"recovered":%s}\n' "$prepared" "$outage" "$recovered"
    ;;
  stop) "${compose[@]}" stop "${services[@]}" ;;
  down) "${compose[@]}" down ;;
  destroy) "${compose[@]}" down --volumes ;;
  status) "${compose[@]}" ps ;;
  logs) "${compose[@]}" logs --no-color --tail 100 "${services[@]}" ;;
esac
