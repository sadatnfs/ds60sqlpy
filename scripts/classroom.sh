#!/usr/bin/env bash
# Shared host entrypoint for macOS, Linux and Windows through WSL 2.
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_dir"
action=up
if [ "$#" -gt 0 ]; then
  case "$1" in up|start|build|stop|status|logs|doctor) action="$1"; shift ;; esac
fi
[ "$action" != start ] || action=up
registry=mirrors
no_browser=0
no_build=0
project_option=''
requested_port=''
requested_db_port=''
profiles=()
all_profiles=(python-core cpp20 java21 javascript-node typescript-node tensorflow-cpu llm-torch-cpu scala-jvm spark-local-scala spark-local-python)
all_services=(python-core-worker cpp-worker java-worker javascript-worker typescript-worker tensorflow-worker llm-worker scala-worker spark-scala-worker spark-python-worker)
usage() {
  cat <<'HELP'
Usage: ./classroom [up|build|stop|status|logs|doctor] [options]

With no arguments: build all ten ordinary workers locally, start them, wait for
readiness and open the browser. Progress stays in this project's Docker volumes.
The host needs Bash and a local Linux-container Docker engine with Compose 2.28.0+.
Windows: use Ubuntu in WSL 2 with your Docker engine's integration enabled.

  --starter                 Prepare only the app, PostgreSQL and Python Core
  --profile PROFILE         Add a selected profile (repeatable; includes Core)
  --no-build                Resume already built images without network preparation
  --no-browser              Print the ready URL without opening it
  --port PORT               Browser host port; 0 lets Docker select a free port
  --database-port PORT      PostgreSQL host port; 0 selects a free port
  --project NAME            Separate Compose project and learning volumes
  --registry mirrors|upstream  Shipped TLS-verified mirrors are the default
  -h, --help                Show this help without contacting Docker

Examples:
  ./classroom
  ./classroom --starter
  ./classroom --profile cpp20 --profile java21
  ./classroom --no-build
  ./classroom stop

Kubernetes owned-cluster preparation and optional pretrained-model downloads
remain explicit workflows in the course guides. Nothing is pushed or pruned.
HELP
}
fail() { printf '\n%s\n' "$*" >&2; exit 2; }
while [ "$#" -gt 0 ]; do
  case "$1" in
    --starter) profiles=(python-core); shift ;;
    --no-build) no_build=1; shift ;;
    --no-browser) no_browser=1; shift ;;
    --profile|--port|--database-port|--project|--registry)
      [ "$#" -ge 2 ] || fail "Missing value after $1. Use ./classroom --help."
      case "$1" in
        --profile) profiles+=("$2") ;;
        --port) requested_port="$2" ;;
        --database-port) requested_db_port="$2" ;;
        --project) project_option="$2" ;;
        --registry) registry="$2" ;;
      esac
      shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) fail "Unknown option: $1. Use ./classroom --help." ;;
  esac
done
case "$registry" in mirrors|upstream) ;; *) fail 'Registry must be mirrors or upstream.' ;; esac
valid_port() { [[ "$1" =~ ^[0-9]{1,5}$ ]] && [ "$((10#$1))" -le 65535 ]; }
for port in "$requested_port" "$requested_db_port"; do
  [ -z "$port" ] || valid_port "$port" || fail 'Ports must be integers from 0 through 65535.'
done
if [ -n "$project_option" ] && ! [[ "$project_option" =~ ^[a-z0-9][a-z0-9_-]{0,48}$ ]]; then fail 'Use a lowercase project name with letters, digits, hyphens or underscores.'; fi
if [ "${#profiles[@]}" -eq 0 ]; then profiles=("${all_profiles[@]}"); else profiles=(python-core "${profiles[@]}"); fi
services=()
selected_profiles=()
for profile in "${profiles[@]}"; do
  found=0
  for ((i=0;i<${#all_profiles[@]};i++)); do
    if [ "$profile" = "${all_profiles[$i]}" ]; then
      found=1
      duplicate=0
      for ((j=0;j<${#selected_profiles[@]};j++)); do [ "$profile" != "${selected_profiles[$j]}" ] || duplicate=1; done
      if [ "$duplicate" -eq 0 ]; then selected_profiles+=("$profile"); services+=("${all_services[$i]}"); fi
      break
    fi
  done
  [ "$found" -eq 1 ] || fail "Unknown ordinary profile: $profile. Use ./classroom --help."
done
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) fail 'Run ./classroom from a WSL 2 Linux terminal, or double-click START_DOCKER_CLASSROOM.cmd.' ;; esac
if command -v docker >/dev/null 2>&1; then docker_cli="$(command -v docker)"
elif [ -x "$HOME/.rd/bin/docker" ]; then docker_cli="$HOME/.rd/bin/docker"
else fail 'Docker CLI is unavailable. Start/install a local Docker-compatible engine. In WSL, enable the engine integration for this Linux distribution, then reopen the terminal.'; fi
endpoint="${DOCKER_HOST:-}"
if [ -n "$endpoint" ]; then unset DOCKER_CONTEXT; else endpoint="$("$docker_cli" context inspect --format '{{.Endpoints.docker.Host}}')"; fi
case "$endpoint" in unix:///*|npipe:////./pipe/*|npipe://./pipe/*) ;;
  tcp://*) [[ "$endpoint" =~ ^tcp://(127[.]0[.]0[.]1|localhost):[0-9]{1,5}$ ]] || fail 'Choose a local Docker context so learning volumes stay on this machine.' ;;
  *) fail 'Choose a local Docker context. Remote SSH/TCP engines are not the personal classroom route.' ;;
esac
version="$("$docker_cli" compose version --short)" || fail 'Docker Compose is unavailable. Install/update the Compose plugin supplied by your engine.'
if [[ "$version" =~ ^v?([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
  major=$((10#${BASH_REMATCH[1]})); minor=$((10#${BASH_REMATCH[2]})); patch=$((10#${BASH_REMATCH[3]}))
  [ "$major" -gt 2 ] || { [ "$major" -eq 2 ] && { [ "$minor" -gt 28 ] || { [ "$minor" -eq 28 ] && [ "$patch" -ge 0 ]; }; }; } || fail 'Update Docker Compose to 2.28.0 or newer.'
else fail 'Could not read the Compose version. Update the engine/Compose plugin.'; fi
engine_os="$("$docker_cli" info --format '{{.OSType}}')" || fail 'The Docker engine is not ready. Start it and rerun the same command.'
[ "$engine_os" = linux ] || fail 'Select Linux containers. Windows uses the WSL 2 backend.'
compose=("$docker_cli" compose --project-directory "$repo_dir" --progress plain --parallel 1)
if [ "$registry" = mirrors ]; then compose+=(--env-file "$repo_dir/docker/registry-mirrors.env.txt"); fi
# Keep explicit local settings; never source .env as shell code or print its contents.
if [ -f "$repo_dir/.env" ]; then compose+=(--env-file "$repo_dir/.env"); fi
[ -z "$project_option" ] || compose+=(--project-name "$project_option")
compose+=(-f "$repo_dir/compose.classroom.yaml")
for profile in "${selected_profiles[@]}"; do compose+=(--profile "$profile"); done
settings="$("${compose[@]}" config --environment | awk '/^(COMPOSE_PROJECT_NAME|DS60_LAB_PORT|DS60_CLASSROOM_PORT|DS60_POSTGRES_PORT|DS60_POSTGRES_IMAGE)=/')" || fail 'Compose could not read the course configuration. Check .env syntax and the Compose version.'
project_name=''; internal_port=8765; configured_port=''; configured_db_port=''; db_image=postgres:17
while IFS='=' read -r key value; do
  case "$key" in
    COMPOSE_PROJECT_NAME) project_name="$value" ;;
    DS60_LAB_PORT) internal_port="$value"; configured_port="$value" ;;
    DS60_CLASSROOM_PORT) requested_port="${requested_port:-$value}" ;;
    DS60_POSTGRES_PORT) configured_db_port="$value" ;;
    DS60_POSTGRES_IMAGE) db_image="${value:-postgres:17}" ;;
  esac
done <<< "$settings"
[[ "$project_name" =~ ^[a-z0-9][a-z0-9_-]{0,48}$ ]] || fail 'Compose resolved an invalid project name.'
valid_port "$internal_port" && [ "$((10#$internal_port))" -gt 0 ] || fail 'DS60_LAB_PORT must be a container port from 1 through 65535.'
[ "$((10#$internal_port))" -ne 5432 ] || fail 'DS60_LAB_PORT cannot be 5432 because the app shares the PostgreSQL network namespace.'
state_dir="$repo_dir/.classroom/$project_name"
[ ! -L "$repo_dir/.classroom" ] && [ ! -L "$state_dir" ] || fail 'The launcher state directory must not be a symbolic link.'
saved_port=''; saved_db_port=''
if [ -e "$state_dir/ports.env" ]; then
  [ -f "$state_dir/ports.env" ] && [ ! -L "$state_dir/ports.env" ] || fail 'The saved port settings must be a regular file.'
  while IFS='=' read -r key value; do
    case "$key" in DS60_CLASSROOM_PORT) saved_port="$value" ;; DS60_POSTGRES_PORT) saved_db_port="$value" ;; '') ;; *) fail 'Unexpected saved port setting. Inspect .classroom for this project.' ;; esac
  done < "$state_dir/ports.env"
fi
# Existing explicitly published ports are retained when adopting an older classroom.
existing="$("${compose[@]}" ps --all --quiet postgres)"
existing_port=''; existing_db_port=''
if [ -n "$existing" ] && [[ "$existing" != *$'\n'* ]]; then
  existing_port="$("$docker_cli" inspect --format "{{range (index .HostConfig.PortBindings \"${internal_port}/tcp\")}}{{.HostPort}}{{end}}" "$existing")"
  existing_db_port="$("$docker_cli" inspect --format '{{range (index .HostConfig.PortBindings "5432/tcp")}}{{.HostPort}}{{end}}' "$existing")"
fi
browser_port="${requested_port:-${configured_port:-${saved_port:-${existing_port:-0}}}}"
database_port="${requested_db_port:-${configured_db_port:-${saved_db_port:-${existing_db_port:-0}}}}"
valid_port "$browser_port" && valid_port "$database_port" || fail 'Configured/saved host ports must be integers from 0 through 65535.'
browser_port=$((10#$browser_port)); database_port=$((10#$database_port))
[ "$browser_port" = 0 ] || [ "$browser_port" != "$database_port" ] || fail 'The browser and database require different host ports.'
export DS60_CLASSROOM_PORT="$browser_port" DS60_POSTGRES_PORT="$database_port"
"${compose[@]}" config --quiet
published_url() {
  local address
  address="$("${compose[@]}" port postgres "$internal_port")" || return 1
  [[ "$address" =~ ^127[.]0[.]0[.]1:([0-9]+)$ ]] || return 1
  [ "${BASH_REMATCH[1]}" -gt 0 ] || return 1
  printf 'http://%s/classroom' "$address"
}
case "$action" in
  doctor) printf 'Local Linux Docker engine and Compose %s are ready.\nProject: %s\nProfiles: %s\n' "$version" "$project_name" "${selected_profiles[*]}"; exit 0 ;;
  status) "${compose[@]}" ps --all; if url="$(published_url)"; then printf 'Published classroom address: %s\n' "$url"; fi; exit 0 ;;
  logs) "${compose[@]}" logs --tail 100 lab postgres; exit 0 ;;
esac
umask 077
mkdir -p "$state_dir"
lock="$state_dir/launcher.lock"
[ ! -L "$lock" ] || fail 'The launcher lock must not be a symbolic link.'
# Serialize stale-lock recovery separately from ordinary lock acquisition.
# Re-read the PID under this mutex so a second reclaimer cannot delete a new owner.
reclaim_stale_lock() (
  recovery="$state_dir/launcher-recovery.lock"
  mkdir "$recovery" 2>/dev/null || fail 'Another launcher is recovering the lock. Retry after it finishes; inspect a leftover recovery lock after an interrupted recovery.'
  trap 'rmdir "$recovery" 2>/dev/null || true' EXIT
  [ ! -L "$lock" ] && [ -f "$lock/pid" ] && [ ! -L "$lock/pid" ] || fail 'Another launcher is starting, or its lock needs inspection. Retry after it finishes.'
  owner_pid="$(cat "$lock/pid")"
  [[ "$owner_pid" =~ ^[0-9]+$ ]] || fail 'The launcher lock is invalid. Inspect it before retrying.'
  if kill -0 "$owner_pid" 2>/dev/null; then fail "Another launcher is active for this project (PID $owner_pid). Wait or cancel that terminal first."; fi
  rm "$lock/pid"
  rmdir "$lock" || fail 'The old launcher lock contains unexpected files; they were preserved.'
  mkdir "$lock" || fail 'Another launcher acquired the project lock. Retry after it finishes.'
)
if ! mkdir "$lock" 2>/dev/null; then reclaim_stale_lock; fi
printf '%s\n' "$$" > "$lock/pid"
release_lock() {
  if [ -f "$lock/pid" ] && [ "$(cat "$lock/pid")" = "$$" ]; then rm "$lock/pid"; rmdir "$lock" 2>/dev/null || true; fi
}
trap release_lock EXIT
trap 'printf "\nInterrupted. Saved volumes are retained; rerun ./classroom when ready.\n" >&2; exit 130' INT TERM
trap 'code=$?; printf "\nClassroom command failed. Read the preceding error; rerun the same command after fixing it.\nSaved volumes are retained. For a busy explicit port, choose --port 0 --database-port 0.\n" >&2; exit "$code"' ERR
if [ "$action" = stop ]; then
  "$docker_cli" compose --project-directory "$repo_dir" -p "$project_name" -f "$repo_dir/compose.classroom.yaml" --profile '*' stop --timeout 20
  printf 'Classroom stopped. All project learning/database volumes were retained.\n'
  exit 0
fi
printf '\nDS60 Classroom | %s\nProfiles: %s\n' "$project_name" "${selected_profiles[*]}"
printf 'First preparation can download several GB. Builds are sequential and local.\n'
if [ "$no_build" -eq 0 ]; then
  if ! "$docker_cli" image inspect "$db_image" >/dev/null 2>&1; then "${compose[@]}" pull postgres; fi
  # Build each service explicitly: newer Compose Bake can schedule a multi-service
  # build concurrently despite the top-level Compose parallel limit.
  for service in lab "${services[@]}"; do
    printf '\nBuilding %s locally...\n' "$service"
    "${compose[@]}" build "$service"
  done
fi
if [ "$action" = build ]; then
  printf 'Local images are ready. Resume with:\n./classroom --no-build --project %s --registry %s --port %s --database-port %s' "$project_name" "$registry" "$browser_port" "$database_port"
  for profile in "${selected_profiles[@]}"; do printf ' --profile %s' "$profile"; done
  printf '\n'
  exit 0
fi
printf '\nStarting the database and selecting the published browser port...\n'
"${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 180 postgres
url="$(published_url)" || fail 'Docker did not report a loopback browser mapping for this project.'
public_port="${url#http://127.0.0.1:}"
public_port="${public_port%/classroom}"
export DS60_PUBLIC_PORT="$public_port"
printf '\nStarting the application with its exact public Host/Origin...\n'
"${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 180 lab
# Bound startup load so several JVM/framework readiness probes do not compete.
for service in "${services[@]}"; do
  printf '\nPreparing %s...\n' "$service"
  "${compose[@]}" up -d --no-deps --no-build --pull never --wait --wait-timeout 120 "$service"
done
"${compose[@]}" exec -T lab python /opt/course/docker/healthcheck.py
url="$(published_url)" || fail 'The containers are healthy, but their loopback browser address could not be determined. Use ./classroom status.'
# Verify the host-facing route too, including its exact Host header.
if command -v curl >/dev/null 2>&1; then
  curl --noproxy '*' --fail --silent --show-error --max-time 10 "$url" >/dev/null || fail 'The host browser URL is not reachable. Keep the error, check the engine port forwarding, and rerun without --no-build if images are outdated.'
else
  if ! (
    exec 3<>"/dev/tcp/127.0.0.1/$public_port" || exit 1
    host_header=127.0.0.1
    [ "$public_port" = 80 ] || host_header="127.0.0.1:$public_port"
    printf 'GET /classroom HTTP/1.0\r\nHost: %s\r\nConnection: close\r\n\r\n' "$host_header" >&3 || exit 1
    IFS= read -r -t 10 response <&3 || exit 1
    [[ "$response" =~ ^HTTP/1[.][01][[:space:]]200[[:space:]] ]] || exit 1
    exec 3>&-
  ); then
    fail 'The host browser URL did not return HTTP 200. Check the engine and rerun without --no-build if images are outdated.'
  fi
fi
settings_temp="$(mktemp "$state_dir/ports.XXXXXX")"
printf 'DS60_CLASSROOM_PORT=%s\nDS60_POSTGRES_PORT=%s\n' "$browser_port" "$database_port" > "$settings_temp"
mv -f "$settings_temp" "$state_dir/ports.env"
[ ! -d "$state_dir/classroom.url" ] || fail 'The classroom URL path is a directory; it was preserved.'
url_temp="$(mktemp "$state_dir/url.XXXXXX")"
printf '%s\n' "$url" > "$url_temp"
mv -f "$url_temp" "$state_dir/classroom.url"
printf '\nReady: %s\nSaved learning and database data remain in project %s Docker volumes.\nStop safely with: ./classroom stop --project %s\n' "$url" "$project_name" "$project_name"
if [ "$no_browser" -eq 0 ]; then
  if [ "$(uname -s)" = Darwin ] && command -v open >/dev/null 2>&1; then open "$url" || printf 'Open %s in your browser.\n' "$url"
  elif [ -n "${WSL_DISTRO_NAME:-}" ] || { [ -r /proc/sys/kernel/osrelease ] && grep -qi microsoft /proc/sys/kernel/osrelease; }; then
    if command -v wslview >/dev/null 2>&1; then wslview "$url" || printf 'Open %s in your Windows browser.\n' "$url"
    elif command -v cmd.exe >/dev/null 2>&1; then cmd.exe /c start '' "$url" || printf 'Open %s in your Windows browser.\n' "$url"
    else printf 'Open %s in your Windows browser.\n' "$url"; fi
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$url" >/dev/null 2>&1 || printf 'Open %s in your browser.\n' "$url"
  else printf 'Open %s in your browser.\n' "$url"; fi
fi
