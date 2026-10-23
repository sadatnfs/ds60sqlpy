#!/usr/bin/env bash
# Optional module workers. Preparation stays on the host, outside the browser.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACTION="${1:-status}"
if (($#)); then shift; fi
PROFILES="${DS60_MODULE_PROFILES:-python-core}"
NO_BROWSER=0
K8S_SESSION=""
HOST_PYTHON="${DS60_HOST_PYTHON:-python3}"
K8S=0
while (($#)); do
  case "$1" in
    --profiles) PROFILES="${2:?Supply comma-separated module profiles}"; shift 2 ;;
    --no-browser) NO_BROWSER=1; shift ;;
    --k8s-session) K8S_SESSION="${2:?Supply the private prepared session path}"; shift 2 ;;
    --python) HOST_PYTHON="${2:?Supply the host Python executable}"; shift 2 ;;
    *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done
case "$ACTION" in build|start|stop|status) ;; *) printf 'Use build, start, stop, or status.\n' >&2; exit 2 ;; esac
PROJECT="${DS60_MODULE_PROJECT:-ds60-learning}"
[[ "$PROJECT" =~ ^[a-z0-9][a-z0-9_-]{0,48}$ ]] || { printf 'Invalid Compose project name.\n' >&2; exit 2; }
IFS=',' read -r -a SELECTED <<< "$PROFILES"
SERVICES=()
ENDPOINTS='{'
for profile in "${SELECTED[@]}"; do
  case "$profile" in
    python-core) service=python-core-worker ;;
    cpp20) service=cpp-worker ;;
    java21) service=java-worker ;;
    javascript-node) service=javascript-worker ;;
    typescript-node) service=typescript-worker ;;
    tensorflow-cpu) service=tensorflow-worker ;;
    llm-torch-cpu) service=llm-worker ;;
    scala-jvm) service=scala-worker ;;
    spark-local-scala) service=spark-scala-worker ;;
    spark-local-python) service=spark-python-worker ;;
    k8s-kind) service=kubernetes-worker; K8S=1 ;;
    *) printf 'Unknown profile: %s.\n' "$profile" >&2; exit 2 ;;
  esac
  SERVICES+=("$service")
  [[ "$ENDPOINTS" == '{' ]] || ENDPOINTS+=','
  ENDPOINTS+="\"$profile\":\"http://$service:8081\""
done
ENDPOINTS+='}'
command -v docker >/dev/null || { printf 'Install/start a Docker-compatible Linux-container engine first.\n' >&2; exit 1; }
endpoint="${DOCKER_HOST:-}"
if [[ -n "$endpoint" ]]; then unset DOCKER_CONTEXT; fi
if [[ -z "$endpoint" ]]; then endpoint="$(docker context inspect --format '{{.Endpoints.docker.Host}}')"; fi
case "$endpoint" in
  unix:///*|npipe:////./pipe/*|npipe://./pipe/*) ;;
  tcp://*) [[ "$endpoint" =~ ^tcp://(127[.]0[.]0[.]1|localhost):[0-9]{1,5}$ ]] || { printf 'Choose an exact local Docker endpoint.\n' >&2; exit 2; } ;;
  *) printf 'Choose a local Docker context before preparing host-saved modules.\n' >&2; exit 2 ;;
esac
export DOCKER_HOST="$endpoint"
unset DOCKER_CONTEXT
docker compose version >/dev/null
docker info >/dev/null
[[ "$(docker info --format '{{.OSType}}')" == linux ]] || { printf 'Switch the engine to Linux containers.\n' >&2; exit 1; }
security="$(docker info --format '{{json .SecurityOptions}}')"
case "$security" in
  *rootless*) export DS60_UID=0 DS60_GID=0 DS60_ROOTLESS=1 ;;
  *) current_uid="$(id -u)"; current_gid="$(id -g)"
     [[ "$current_uid" != 0 ]] || current_uid=1000
     [[ "$current_gid" != 0 ]] || current_gid=1000
     export DS60_UID="${DS60_UID:-$current_uid}" DS60_GID="${DS60_GID:-$current_gid}" DS60_ROOTLESS=0 ;;
esac
read -r SCOPE _ < <(printf '%s' "$ROOT" | cksum)
TEMP_BASE="$(cd "${TMPDIR:-/tmp}" && pwd -P)"
PARENT="$TEMP_BASE/ds60-modules-$UID"
SESSION="${DS60_MODULE_RUNTIME_DIR:-$PARENT/$SCOPE-$PROJECT}"
export DS60_MODULE_RUNTIME_DIR="$SESSION" DS60_MODULE_ENDPOINTS="$ENDPOINTS"
export DS60_LEARNING_DIR="${DS60_LEARNING_DIR:-$ROOT/.learning}"
if ((K8S)); then
  export DS60_K8S_SESSION_DIR="${K8S_SESSION:-$SESSION/not-prepared}"
  if [[ "$ACTION" == start ]]; then
    [[ "$K8S_SESSION" == /* ]] || { printf 'Use an absolute --k8s-session path from the preparation receipt.\n' >&2; exit 2; }
    [[ -n "$K8S_SESSION" ]] || { printf 'Kubernetes start requires --k8s-session from explicit host preparation.\n' >&2; exit 2; }
    command -v "$HOST_PYTHON" >/dev/null || { printf 'Kubernetes lease inspection needs host Python 3.12; use --python PATH.\n' >&2; exit 2; }
    "$HOST_PYTHON" "$ROOT/scripts/prepare_kubernetes.py" inspect --session "$K8S_SESSION" --docker-host "$endpoint"
  fi
fi
if [[ "$ACTION" == status || "$ACTION" == stop ]]; then
  QUERY=(docker compose --project-name "$PROJECT" -f "$ROOT/compose.yaml" -f "$ROOT/compose.modules.yaml" --profile lab)
  if ((K8S)); then QUERY+=(-f "$ROOT/compose.kubernetes.yaml"); fi
  for profile in "${SELECTED[@]}"; do QUERY+=(--profile "$profile"); done
  if [[ "$ACTION" == status ]]; then "${QUERY[@]}" ps; else "${QUERY[@]}" stop lab "${SERVICES[@]}"; fi
  exit $?
fi
# Credential directories may not follow links or enter portable learner backups.
private_path() {
  local part="$1"
  [[ "$part" == /* && "$part" != *'/../'* && "$part" != *'/./'* && "$part" != */.. && "$part" != */. ]] || return 1
  while [[ "$part" != / ]]; do
    [[ ! -L "$part" ]] || return 1
    case "${part##*/}" in .[lL][eE][aA][rR][nN][iI][nN][gG]) return 1 ;;
    esac
    part="${part%/*}"
    [[ -n "$part" ]] || part=/
  done
}
private_path "$SESSION" || { printf 'Use an absolute private runtime path outside .learning without linked ancestors.\n' >&2; exit 2; }
if [[ -e "$PARENT" || -L "$PARENT" ]]; then
  [[ -d "$PARENT" && ! -L "$PARENT" && -O "$PARENT" ]] || { printf 'Unsafe module session directory.\n' >&2; exit 1; }
fi
umask 077
mkdir -p "$PARENT"
chmod 700 "$PARENT"
SESSION="${DS60_MODULE_RUNTIME_DIR:-$PARENT/$SCOPE-$PROJECT}"
if [[ -e "$SESSION" || -L "$SESSION" ]]; then
  [[ -d "$SESSION" && ! -L "$SESSION" && -O "$SESSION" ]] || { printf 'Unsafe private runtime session.\n' >&2; exit 1; }
fi
mkdir -p "$SESSION"
chmod 700 "$SESSION"
[[ ! -L "$SESSION/worker-token" ]] || { printf 'Worker token must not be a symbolic link.\n' >&2; exit 1; }
if [[ ! -s "$SESSION/worker-token" ]]; then
  command -v openssl >/dev/null || { printf 'OpenSSL is needed to create this private session token.\n' >&2; exit 1; }
  openssl rand -hex 32 > "$SESSION/worker-token"
fi
chmod 600 "$SESSION/worker-token"
export DS60_MODULE_RUNTIME_DIR="$SESSION" DS60_MODULE_ENDPOINTS="$ENDPOINTS"
export DS60_UID="${DS60_UID:-$(id -u)}" DS60_GID="${DS60_GID:-$(id -g)}"
export DS60_LEARNING_DIR="${DS60_LEARNING_DIR:-$ROOT/.learning}"
[[ ! -L "$DS60_LEARNING_DIR" ]] || { printf 'Choose a real host learning directory.\n' >&2; exit 1; }
mkdir -p "$DS60_LEARNING_DIR"
COMPOSE=(docker compose --project-name "$PROJECT" -f "$ROOT/compose.yaml" -f "$ROOT/compose.modules.yaml" --profile lab)
if ((K8S)); then COMPOSE+=(-f "$ROOT/compose.kubernetes.yaml"); fi
for profile in "${SELECTED[@]}"; do COMPOSE+=(--profile "$profile"); done
case "$ACTION" in
  build)
    # Each image is built separately to bound simultaneous unpack/build space.
    BUILD_SERVICES=(lab "${SERVICES[@]}")
    if ((K8S)); then BUILD_SERVICES=(k8s-fixture "${BUILD_SERVICES[@]}"); fi
    for service in "${BUILD_SERVICES[@]}"; do
      available="$(df -Pk "$ROOT" | awk 'END {print $4}')"
      ((available >= 8 * 1024 * 1024)) || { printf 'Need at least 8 GiB free host disk before building. No cleanup was performed.\n' >&2; exit 1; }
      if docker image inspect postgres:17 >/dev/null 2>&1; then
        engine_available="$(docker run --rm --pull never --network none --entrypoint sh postgres:17 -c 'df -Pk /' | awk 'END {print $4}')"
        [[ "$engine_available" =~ ^[0-9]+$ ]] && ((engine_available >= 8 * 1024 * 1024)) || { printf 'Engine filesystem has less than 8 GiB free or its capacity is unknown. Preserve progress and free only resources you own.\n' >&2; exit 1; }
      else
        printf 'Engine filesystem capacity has not been measured yet; build the base course first.\n' >&2
        exit 1
      fi
      printf 'Building %s with foreground logs.\n' "$service"
      if [[ "$service" == k8s-fixture ]]; then
        COMPOSE_PROGRESS=plain BUILDKIT_PROGRESS=plain docker build --progress plain -f "$ROOT/docker/kubernetes/Dockerfile.fixture" --build-arg "DS60_PYTHON_IMAGE=${DS60_PYTHON_IMAGE:-python:3.12.12-slim-bookworm}" -t ds60sqlpy-k8s-fixture:0.1.0 "$ROOT"
      else
        COMPOSE_PROGRESS=plain BUILDKIT_PROGRESS=plain "${COMPOSE[@]}" build "$service"
      fi
    done ;;
  start)
    "${COMPOSE[@]}" up -d --no-build --pull never --wait --wait-timeout 180 lab "${SERVICES[@]}"
    URL="http://127.0.0.1:${DS60_LAB_PORT:-8765}/journeys"
    printf 'Module labs: %s\nSaved learner work: %s\n' "$URL" "$DS60_LEARNING_DIR"
    if ((NO_BROWSER == 0)); then
      if command -v open >/dev/null; then open "$URL"; elif command -v xdg-open >/dev/null; then xdg-open "$URL"; else printf 'Open the URL above in your browser.\n'; fi
    fi ;;
  stop) "${COMPOSE[@]}" stop lab "${SERVICES[@]}" ;;
  status) "${COMPOSE[@]}" ps ;;
esac
