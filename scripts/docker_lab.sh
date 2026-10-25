#!/usr/bin/env bash
# No host Python is needed. Docker/Compose and this host shell run the launcher.
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
action="start"
if [ "$#" -gt 0 ]; then
  case "$1" in start | build | stop | status | doctor)
    action="$1"
    shift
    ;;
  esac
fi
lab_port="${DS60_LAB_PORT:-8765}"
database_port="${DS60_POSTGRES_PORT:-55432}"
data_dir="${DS60_LEARNING_DIR:-$repo_dir/.learning}"
project_name="ds60-learning"
force_build=0
no_browser=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --build)
      force_build=1
      shift
      ;;
    --no-browser)
      no_browser=1
      shift
      ;;
    --port | --database-port | --data-dir | --project)
      if [ "$#" -lt 2 ]; then
        echo "Missing value after $1" >&2
        exit 2
      fi
      case "$1" in
        --port) lab_port="$2" ;; --database-port) database_port="$2" ;;
        --data-dir) data_dir="$2" ;; --project) project_name="$2" ;;
      esac
      shift 2
      ;;
    -h | --help)
      echo 'Usage: bash scripts/docker_lab.sh [start|build|stop|status|doctor] [--build] [--no-browser] [--port N] [--database-port N] [--data-dir PATH] [--project NAME]'
      exit 0
      ;;
    *)
      echo "Unknown option: $1. Use --help." >&2
      exit 2
      ;;
  esac
done
case "$lab_port:$database_port" in *[!0-9:]* | :* | *:)
  echo 'Ports must be numbers.' >&2
  exit 2
  ;;
esac
if [ "$lab_port" -lt 1 ] || [ "$lab_port" -gt 65535 ] || [ "$database_port" -lt 1 ] || [ "$database_port" -gt 65535 ] || [ "$lab_port" = "$database_port" ]; then
  echo 'Use different browser/database ports between 1 and 65535.' >&2
  exit 2
fi
if ! [[ "$project_name" =~ ^[a-z0-9][a-z0-9_-]{0,48}$ ]]; then
  echo 'Choose a lowercase project name.' >&2
  exit 2
fi
if command -v docker >/dev/null 2>&1; then
  docker_cli="$(command -v docker)"
elif [ -x "$HOME/.rd/bin/docker" ]; then
  docker_cli="$HOME/.rd/bin/docker"
else
  echo 'Docker CLI not found. Install/start your local Docker engine, then reopen Terminal.' >&2
  exit 2
fi
endpoint="${DOCKER_HOST:-}"
if [ -n "$endpoint" ]; then unset DOCKER_CONTEXT; fi
if [ -z "$endpoint" ]; then endpoint="$("$docker_cli" context inspect --format '{{.Endpoints.docker.Host}}')"; fi
case "$endpoint" in unix:///* | npipe:////./pipe/* | npipe://./pipe/*) ;;
tcp://*)
  if ! [[ "$endpoint" =~ ^tcp://(127[.]0[.]0[.]1|localhost):[0-9]{1,5}$ ]]; then
    echo 'Choose an exact local Docker TCP endpoint without credentials or path suffixes.' >&2
    exit 2
  fi
  ;;
*)
  echo 'Choose a local Docker context so host-saved progress stays on this machine.' >&2
  exit 2
  ;;
esac
"$docker_cli" compose version >/dev/null
engine_os="$("$docker_cli" info --format '{{.OSType}}')"
if [ "$engine_os" != linux ]; then
  echo 'Use Linux containers. Windows learners use the WSL 2 backend.' >&2
  exit 2
fi
security="$("$docker_cli" info --format '{{json .SecurityOptions}}')"
case "$security" in *rootless*) export DS60_UID=0 DS60_GID=0 DS60_ROOTLESS=1 ;;
*)
  current_uid="$(id -u)"
  current_gid="$(id -g)"
  if [ "$current_uid" = 0 ]; then current_uid=1000; fi
  if [ "$current_gid" = 0 ]; then current_gid=1000; fi
  export DS60_UID="$current_uid" DS60_GID="$current_gid" DS60_ROOTLESS=0
  ;;
esac
case "$data_dir" in /*) ;; *) data_dir="$PWD/$data_dir" ;; esac
export DS60_LEARNING_DIR="$data_dir" DS60_LAB_PORT="$lab_port" DS60_POSTGRES_PORT="$database_port"
compose=("$docker_cli" compose --project-directory "$repo_dir" --project-name "$project_name" --file "$repo_dir/compose.yaml" --profile lab)
url="http://127.0.0.1:$lab_port/classroom"
echo "Local lab: $url"
echo "Saved progress and pads: $data_dir"
case "$action" in
  doctor)
    echo 'Local Docker engine and Compose are ready. No data folder was created.'
    exit 0
    ;;
  status)
    "${compose[@]}" ps
    exit $?
    ;;
  stop)
    "${compose[@]}" stop
    exit $?
    ;;
esac
if [ "$action" = build ] || [ "$force_build" = 1 ] || ! "$docker_cli" image inspect ds60sqlpy-lab:0.4.0 >/dev/null 2>&1; then
  echo 'Building locally. The first build downloads public images/packages. Nothing is pushed.'
  build_args=(build)
  if [ -n "${DS60_BASE_IMAGE:-}" ]; then build_args+=(--build-arg "DS60_BASE_IMAGE=$DS60_BASE_IMAGE"); fi
  "${compose[@]}" "${build_args[@]}" lab
fi
if [ "$action" = build ]; then exit 0; fi
mkdir -p "$data_dir"
"${compose[@]}" up --wait --wait-timeout 120 --no-build
if ! command -v curl >/dev/null 2>&1; then
  echo "The container health checks passed. Open $url in your browser."
else
  ready=0
  for _ in $(seq 1 120); do
    if curl --noproxy '*' --fail --silent --max-time 2 "$url" >/dev/null; then
      ready=1
      break
    fi
    sleep 1
  done
  if [ "$ready" != 1 ]; then
    echo 'The lab is not ready. Use the status command, then inspect this project lab/postgres logs.' >&2
    "${compose[@]}" logs --tail 40 lab postgres
    exit 1
  fi
fi
echo "Ready: $url"
echo 'Stop keeps your host-saved progress and database volume.'
if [ "$no_browser" = 0 ]; then
  if [ "$(uname -s)" = Darwin ]; then
    open "$url" || echo "Open $url in your browser."
  elif [ -r /proc/sys/kernel/osrelease ] && [[ "$(cat /proc/sys/kernel/osrelease)" =~ [Mm]icrosoft ]]; then
    if command -v wslview >/dev/null 2>&1; then
      wslview "$url" || echo "Open $url in your Windows browser."
    elif command -v cmd.exe >/dev/null 2>&1; then
      cmd.exe /c start "" "$url" || echo "Open $url in your Windows browser."
    else echo "Open $url in your Windows browser."; fi
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1 || echo "Open $url in your browser."
  else echo "Open $url in your browser."; fi
fi
