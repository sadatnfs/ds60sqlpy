#!/usr/bin/env bash
# Shared host entrypoint for macOS, Linux and Windows through WSL 2.
set -Eeuo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_dir"
action=up
if [ "$#" -gt 0 ]; then
  case "$1" in up | start | resume | build | pull | stop | status | logs | doctor | publish)
    action="$1"
    shift
    ;;
  esac
fi
[ "$action" != start ] || action=up
if [ "$action" = publish ]; then
  exec bash "$repo_dir/scripts/publish-images" "$@"
fi
registry=mirrors
registry_explicit=0
no_browser=0
no_build=0
rebuild=0
profiles_explicit=0
project_option=''
requested_port=''
requested_db_port=''
gpu_device=''
profiles=()
all_profiles=(python-core cpp20 java21 javascript-node typescript-node tensorflow-cpu llm-torch-cpu scala-jvm spark-local-scala spark-local-python c17 go csharp-dotnet rust-stable swift-linux php-cli jax-cpu bayesian-cpu r-statistics data-engineering data-platforms-python stan-cpu julia dbt-duckdb)
all_services=(python-core-worker cpp-worker java-worker javascript-worker typescript-worker tensorflow-worker llm-worker scala-worker spark-scala-worker spark-python-worker c-worker go-worker csharp-worker rust-worker swift-worker php-worker jax-worker bayesian-worker r-worker data-engineering-worker data-platforms-worker stan-worker julia-worker dbt-worker)
known_profiles=("${all_profiles[@]}" cuda-cpp cuda-python pytorch-cuda tensorflow-cuda)
known_services=("${all_services[@]}" cuda-cpp-worker cuda-python-worker pytorch-cuda-worker tensorflow-cuda-worker)
usage() {
  cat <<'HELP'
Usage: ./classroom [up|resume|build|pull|stop|status|logs|doctor|publish] [options]

With no arguments: resume this project's containers and saved profile selection.
A first launch prepares all ordinary workers, building only missing images.
Progress stays in this project's Docker volumes. Updates require --rebuild.
The host needs Bash and a local Linux-container Docker engine with Compose 2.28.0+.
Windows: use Ubuntu in WSL 2 with your Docker engine's integration enabled.

  --starter                 Select only the app, PostgreSQL and Python Core
  --all                     Select all ordinary workers
  --profile PROFILE         Add a selected profile (repeatable; includes Core)
  --no-build                Like resume: never build or pull missing images
  --rebuild                 Rebuild local images, or refresh Hub images; apply updates
  --from-hub USER            Pull native multi-platform images from USER/ds60sqlpy
  --tag VERSION             Select a release; Hub latest resolves to a saved version
  --architecture-tags       Use manual/legacy per-architecture Hub tags
  --local-build             Return this project to locally built images
  --gpu-device ID           Explicit NVIDIA device index/UUID for optional CUDA profiles
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
  ./classroom resume
  ./classroom --rebuild
  ./classroom stop
  ./classroom publish --to-hub YOUR_DOCKERHUB_USER
  ./classroom publish --to-hub YOUR_DOCKERHUB_USER --push

Publishing has its own options: ./classroom publish --help. It previews the
complete ordinary image set by default and requires --push for registry writes.

Kubernetes owned-cluster preparation and optional pretrained-model downloads
remain explicit workflows in the course guides. Startup never publishes or prunes.
HELP
}
fail() {
  printf '\n%s\n' "$*" >&2
  exit 2
}
# shellcheck source=scripts/classroom_images.sh
source "$repo_dir/scripts/classroom_images.sh"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --starter)
      profiles=(python-core)
      profiles_explicit=1
      shift
      ;;
    --all)
      profiles=("${all_profiles[@]}")
      profiles_explicit=1
      shift
      ;;
    --rebuild)
      rebuild=1
      shift
      ;;
    --no-build)
      no_build=1
      shift
      ;;
    --architecture-tags)
      image_layout=architecture
      image_layout_explicit=1
      shift
      ;;
    --no-browser)
      no_browser=1
      shift
      ;;
    --local-build)
      image_source=local
      image_namespace=''
      image_source_explicit=1
      shift
      ;;
    --profile | --port | --database-port | --project | --registry | --from-hub | --tag | --gpu-device)
      [ "$#" -ge 2 ] || fail "Missing value after $1. Use ./classroom --help."
      case "$1" in
        --profile)
          profiles+=("$2")
          profiles_explicit=1
          ;;
        --port) requested_port="$2" ;;
        --database-port) requested_db_port="$2" ;;
        --project) project_option="$2" ;;
        --gpu-device) gpu_device="$2" ;;
        --from-hub)
          image_source=hub
          image_namespace="$2"
          image_source_explicit=1
          ;;
        --tag)
          image_tag="$2"
          image_tag_explicit=1
          ;;
        --registry)
          registry="$2"
          registry_explicit=1
          ;;
      esac
      shift 2
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *) fail "Unknown option: $1. Use ./classroom --help." ;;
  esac
done
case "$registry" in mirrors | upstream) ;; *) fail 'Registry must be mirrors or upstream.' ;; esac
valid_port() { [[ "$1" =~ ^[0-9]{1,5}$ ]] && [ "$((10#$1))" -le 65535 ]; }
for port in "$requested_port" "$requested_db_port"; do
  [ -z "$port" ] || valid_port "$port" || fail 'Ports must be integers from 0 through 65535.'
done
if [ -n "$project_option" ] && ! [[ "$project_option" =~ ^[a-z0-9][a-z0-9_-]{0,48}$ ]]; then fail 'Use a lowercase project name with letters, digits, hyphens or underscores.'; fi
case "$action" in resume) no_build=1 ;; build | pull) rebuild=1 ;; esac
validate_image_selection pending
[ "$no_build" -eq 0 ] || [ "$rebuild" -eq 0 ] || fail 'Use resume/--no-build or --rebuild/build, not both.'
# Reject misspelled profiles before contacting the engine.
for profile in ${profiles[@]+"${profiles[@]}"}; do
  found=0
  for known in "${known_profiles[@]}"; do [ "$profile" != "$known" ] || found=1; done
  [ "$found" -eq 1 ] || fail "Unknown profile: $profile. Use ./classroom --help."
done
case "$(uname -s)" in MINGW* | MSYS* | CYGWIN*) fail 'Run ./classroom from a WSL 2 Linux terminal, or double-click START_DOCKER_CLASSROOM.cmd.' ;; esac
if command -v docker >/dev/null 2>&1; then
  docker_cli="$(command -v docker)"
elif [ -x "$HOME/.rd/bin/docker" ]; then
  docker_cli="$HOME/.rd/bin/docker"
else fail 'Docker CLI is unavailable. Start/install a local Docker-compatible engine. In WSL, enable the engine integration for this Linux distribution, then reopen the terminal.'; fi
endpoint="${DOCKER_HOST:-}"
if [ -n "$endpoint" ]; then unset DOCKER_CONTEXT; else endpoint="$("$docker_cli" context inspect --format '{{.Endpoints.docker.Host}}')"; fi
case "$endpoint" in unix:///* | npipe:////./pipe/* | npipe://./pipe/*) ;;
tcp://*) [[ "$endpoint" =~ ^tcp://(127[.]0[.]0[.]1|localhost):[0-9]{1,5}$ ]] || fail 'Choose a local Docker context so learning volumes stay on this machine.' ;;
*) fail 'Choose a local Docker context. Remote SSH/TCP engines are not the personal classroom route.' ;;
esac
version="$("$docker_cli" compose version --short)" || fail 'Docker Compose is unavailable. Install/update the Compose plugin supplied by your engine.'
if [[ "$version" =~ ^v?([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
  major=$((10#${BASH_REMATCH[1]}))
  minor=$((10#${BASH_REMATCH[2]}))
  patch=$((10#${BASH_REMATCH[3]}))
  [ "$major" -gt 2 ] || { [ "$major" -eq 2 ] && { [ "$minor" -gt 28 ] || { [ "$minor" -eq 28 ] && [ "$patch" -ge 0 ]; }; }; } || fail 'Update Docker Compose to 2.28.0 or newer.'
else fail 'Could not read the Compose version. Update the engine/Compose plugin.'; fi
engine_os="$("$docker_cli" info --format '{{.OSType}}')" || fail 'The Docker engine is not ready. Start it and rerun the same command.'
[ "$engine_os" = linux ] || fail 'Select Linux containers. Windows uses the WSL 2 backend.'
make_compose() {
  compose=("$docker_cli" compose --project-directory "$repo_dir" --progress plain --parallel 1)
  if [ "$registry" = mirrors ]; then compose+=(--env-file "$repo_dir/docker/registry-mirrors.env.txt"); fi
  # Never source local settings as shell code or print private environment values.
  if [ -f "$repo_dir/.env" ]; then compose+=(--env-file "$repo_dir/.env"); fi
  [ -z "$project_option" ] || compose+=(--project-name "$project_option")
  compose+=(-f "$repo_dir/compose.classroom.yaml")
  for profile in ${selected_profiles[@]+"${selected_profiles[@]}"}; do compose+=(--profile "$profile"); done
}
selected_profiles=()
make_compose
settings="$("${compose[@]}" config --environment | awk '/^(COMPOSE_PROJECT_NAME|DS60_LAB_PORT|DS60_CLASSROOM_PORT|DS60_POSTGRES_PORT|DS60_POSTGRES_IMAGE)=/')" || fail 'Compose could not read the course configuration. Check .env syntax and the Compose version.'
project_name=''
internal_port=8765
configured_port=''
configured_db_port=''
db_image=postgres:17
while IFS='=' read -r key value; do
  case "$key" in
    COMPOSE_PROJECT_NAME) project_name="$value" ;;
    DS60_LAB_PORT)
      internal_port="$value"
      configured_port="$value"
      ;;
    DS60_CLASSROOM_PORT) requested_port="${requested_port:-$value}" ;;
    DS60_POSTGRES_PORT) configured_db_port="$value" ;;
    DS60_POSTGRES_IMAGE) db_image="${value:-postgres:17}" ;;
  esac
done <<<"$settings"
[[ "$project_name" =~ ^[a-z0-9][a-z0-9_-]{0,48}$ ]] || fail 'Compose resolved an invalid project name.'
valid_port "$internal_port" && [ "$((10#$internal_port))" -gt 0 ] || fail 'DS60_LAB_PORT must be a container port from 1 through 65535.'
[ "$((10#$internal_port))" -ne 5432 ] || fail 'DS60_LAB_PORT cannot be 5432 because the app shares the PostgreSQL network namespace.'
state_dir="$repo_dir/.classroom/$project_name"
[ ! -L "$repo_dir/.classroom" ] && [ ! -L "$state_dir" ] || fail 'The launcher state directory must not be a symbolic link.'
load_image_selection
[ "$action" != pull ] || [ "$image_source" = hub ] || fail 'Use pull with --from-hub USER, or a project that has saved Hub settings.'
[ "$action" != build ] || [ "$image_source" = local ] || fail 'This project uses Hub images. Use pull to download them, or build --local-build to build locally.'
# Store declarative values only. No shell evaluation, paths or private environment data.
saved_profiles=''
saved_registry=''
if [ -e "$state_dir/selection.env" ] || [ -L "$state_dir/selection.env" ]; then
  [ -f "$state_dir/selection.env" ] && [ ! -L "$state_dir/selection.env" ] || fail 'The saved selection must be a regular file.'
  seen_profiles=0
  seen_registry=0
  while IFS='=' read -r key value || [ -n "$key$value" ]; do
    case "$key" in
      DS60_PROFILES)
        [ "$seen_profiles" -eq 0 ] || fail 'Duplicate saved profile setting.'
        saved_profiles="$value"
        seen_profiles=1
        ;;
      DS60_REGISTRY)
        [ "$seen_registry" -eq 0 ] || fail 'Duplicate saved registry setting.'
        saved_registry="$value"
        seen_registry=1
        ;;
      *) fail 'Unexpected saved selection setting. Inspect .classroom for this project.' ;;
    esac
  done <"$state_dir/selection.env"
  [ "$seen_profiles" -eq 1 ] && [ "$seen_registry" -eq 1 ] || fail 'The saved selection is incomplete.'
  case "$saved_registry" in mirrors | upstream) ;; *) fail 'The saved registry setting is invalid.' ;; esac
  [[ "$saved_profiles" =~ ^[a-z0-9-]+(,[a-z0-9-]+)*$ ]] || fail 'The saved profile setting is invalid.'
  IFS=',' read -r -a saved_profile_list <<<"$saved_profiles"
  for profile in "${saved_profile_list[@]}"; do
    found=0
    for known in "${known_profiles[@]}"; do [ "$profile" != "$known" ] || found=1; done
    [ "$found" -eq 1 ] || fail "Unknown saved profile: $profile. Inspect .classroom for this project."
  done
  [ "$registry_explicit" -eq 1 ] || registry="$saved_registry"
fi
make_compose
# Re-resolve only the selected database image after restoring the registry preference.
db_image="$("${compose[@]}" config --images postgres)"
[ -n "$db_image" ] && [[ "$db_image" != *$'\n'* ]] || fail 'Compose did not resolve one database image.'
if [ "$profiles_explicit" -eq 0 ]; then
  if [ -n "$saved_profiles" ]; then
    profiles=("${saved_profile_list[@]}")
  else
    # Adopt a previous launcher/Compose installation without expanding a starter
    # classroom into every optional SDK merely because selection.env is new.
    existing_services="$("${compose[@]}" --profile '*' ps --all --services)"
    while IFS= read -r service; do
      for ((i = 0; i < ${#known_services[@]}; i++)); do
        [ "$service" != "${known_services[$i]}" ] || profiles+=("${known_profiles[$i]}")
      done
    done <<<"$existing_services"
    if [ "${#profiles[@]}" -eq 0 ]; then
      if [[ $'\n'"$existing_services"$'\n' == *$'\nlab\n'* ]] || [[ $'\n'"$existing_services"$'\n' == *$'\npostgres\n'* ]] || [[ $'\n'"$existing_services"$'\n' == *$'\nclassroom-init\n'* ]]; then
        profiles=(python-core)
      else profiles=("${all_profiles[@]}"); fi
    fi
  fi
fi
profiles=(python-core ${profiles[@]+"${profiles[@]}"})
services=()
selected_profiles=()
for profile in ${profiles[@]+"${profiles[@]}"}; do
  duplicate=0
  for known in ${selected_profiles[@]+"${selected_profiles[@]}"}; do [ "$profile" != "$known" ] || duplicate=1; done
  if [ "$duplicate" -eq 0 ]; then
    for ((i = 0; i < ${#known_profiles[@]}; i++)); do
      if [ "$profile" = "${known_profiles[$i]}" ]; then
        selected_profiles+=("$profile")
        services+=("${known_services[$i]}")
        break
      fi
    done
  fi
done
if [ -e "$state_dir/gpu.env" ] || [ -L "$state_dir/gpu.env" ]; then
  [ -f "$state_dir/gpu.env" ] && [ ! -L "$state_dir/gpu.env" ] || fail 'GPU selection must be a regular file.'
  saved_gpu=''
  while IFS='=' read -r key value || [ -n "$key$value" ]; do
    [ "$key" = DS60_GPU_DEVICE ] && [ -z "$saved_gpu" ] || fail 'Invalid saved GPU selection.'
    saved_gpu="$value"
  done <"$state_dir/gpu.env"
  gpu_device="${gpu_device:-$saved_gpu}"
fi
if [ -n "$gpu_device" ]; then
  [[ "$gpu_device" =~ ^([0-9]{1,3}|GPU-[a-fA-F0-9-]{8,80}|MIG-[a-fA-F0-9-]{8,80})$ ]] || fail 'Choose one NVIDIA device index, GPU UUID or MIG UUID.'
  export DS60_GPU_DEVICE="$gpu_device"
fi
for profile in "${selected_profiles[@]}"; do
  case "$profile:$action" in
    cuda-*:up | cuda-*:resume | cuda-*:build | cuda-*:pull | pytorch-cuda:up | pytorch-cuda:resume | pytorch-cuda:build | pytorch-cuda:pull | tensorflow-cuda:up | tensorflow-cuda:resume | tensorflow-cuda:build | tensorflow-cuda:pull)
      gpu_arch="$("$docker_cli" info --format '{{.Architecture}}')"
      case "$gpu_arch" in
        amd64 | x86_64) ;;
        *) fail 'Optional CUDA images currently target Linux amd64 NVIDIA hosts. On ARM, use --starter or the llm-torch-cpu/tensorflow-cpu profiles and the CUDA CPU-model lessons. See docs/cuda-classroom.md for explicit native NVIDIA preparation. No CUDA image will be built or downloaded here.' ;;
      esac
      case "$action" in up | resume)
        [ -n "$gpu_device" ] || fail 'CUDA execution needs an explicitly chosen NVIDIA GPU. Add --gpu-device 0 or its GPU UUID. CPU/reading variants need no GPU.'
        ;;
      esac
      ;;
  esac
done
make_compose
saved_port=''
saved_db_port=''
if [ -e "$state_dir/ports.env" ] || [ -L "$state_dir/ports.env" ]; then
  [ -f "$state_dir/ports.env" ] && [ ! -L "$state_dir/ports.env" ] || fail 'The saved port settings must be a regular file.'
  while IFS='=' read -r key value; do
    case "$key" in DS60_CLASSROOM_PORT) saved_port="$value" ;; DS60_POSTGRES_PORT) saved_db_port="$value" ;; '') ;; *) fail 'Unexpected saved port setting. Inspect .classroom for this project.' ;; esac
  done <"$state_dir/ports.env"
fi
# Existing explicitly published ports are retained when adopting an older classroom.
existing="$("${compose[@]}" ps --all --quiet postgres)"
existing_port=''
existing_db_port=''
if [ -n "$existing" ] && [[ "$existing" != *$'\n'* ]]; then
  existing_port="$("$docker_cli" inspect --format "{{range (index .HostConfig.PortBindings \"${internal_port}/tcp\")}}{{.HostPort}}{{end}}" "$existing")"
  existing_db_port="$("$docker_cli" inspect --format '{{range (index .HostConfig.PortBindings "5432/tcp")}}{{.HostPort}}{{end}}' "$existing")"
fi
browser_port="${requested_port:-${configured_port:-${saved_port:-${existing_port:-0}}}}"
database_port="${requested_db_port:-${configured_db_port:-${saved_db_port:-${existing_db_port:-0}}}}"
valid_port "$browser_port" && valid_port "$database_port" || fail 'Configured/saved host ports must be integers from 0 through 65535.'
browser_port=$((10#$browser_port))
database_port=$((10#$database_port))
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
  doctor)
    printf 'Local Linux Docker engine and Compose %s are ready.\nProject: %s\nProfiles: %s\n' "$version" "$project_name" "${selected_profiles[*]}"
    exit 0
    ;;
  status)
    "${compose[@]}" ps --all
    if url="$(published_url)"; then printf 'Published classroom address: %s\n' "$url"; fi
    exit 0
    ;;
  logs)
    "${compose[@]}" logs --tail 100 lab postgres
    exit 0
    ;;
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
printf '%s\n' "$$" >"$lock/pid"
release_lock() {
  if [ -f "$lock/pid" ] && [ "$(cat "$lock/pid")" = "$$" ]; then
    rm "$lock/pid"
    rmdir "$lock" 2>/dev/null || true
  fi
}
trap release_lock EXIT
trap 'printf "\nInterrupted. Saved volumes are retained; rerun ./classroom when ready.\n" >&2; exit 130' INT TERM
handle_classroom_error() {
  local code=$?
  printf "\nClassroom command failed. Read the preceding error; rerun the same command after fixing it.\nSaved volumes are retained. For a busy explicit port, choose --port 0 --database-port 0.\n" >&2
  exit "$code"
}
trap handle_classroom_error ERR
if [ "$action" = stop ]; then
  "$docker_cli" compose --project-directory "$repo_dir" -p "$project_name" -f "$repo_dir/compose.classroom.yaml" --profile '*' stop --timeout 20
  printf 'Classroom stopped. All project learning/database volumes were retained.\n'
  exit 0
fi
save_profile_selection() {
  local selection_temp profile_csv
  selection_temp="$(mktemp "$state_dir/selection.XXXXXX")"
  profile_csv="$(
    IFS=,
    printf '%s' "${selected_profiles[*]}"
  )"
  printf 'DS60_PROFILES=%s\nDS60_REGISTRY=%s\n' "$profile_csv" "$registry" >"$selection_temp"
  mv -f "$selection_temp" "$state_dir/selection.env"
}
resolve_latest_hub_release
printf '\nDS60 Classroom | %s\nProfiles: %s\n' "$project_name" "${selected_profiles[*]}"
printf 'Images: %s (release %s)\n' "$image_source" "$image_tag"
# Persist the chosen intent before preparation so Ctrl+C or a failed download does
# not lose a small selection. Writes remain atomic and protected by the project lock.
save_profile_selection
save_image_selection
if [ -n "$gpu_device" ]; then
  gpu_temp="$(mktemp "$state_dir/gpu.XXXXXX")"
  printf 'DS60_GPU_DEVICE=%s\n' "$gpu_device" >"$gpu_temp"
  mv -f "$gpu_temp" "$state_dir/gpu.env"
fi
container_id() {
  local id
  id="$("${compose[@]}" ps --all --quiet "$1")" || return 1
  [[ "$id" != *$'\n'* ]] || fail "More than one $1 container exists; inspect this project before resuming."
  printf '%s' "$id"
}
image_for() {
  # Compose config includes dependencies. Read only this service's image from
  # its normalized YAML block, avoiding JSON/Python host prerequisites.
  local value
  value="$("${compose[@]}" config "$1" | awk -v service="$1" '
    $0 == "  " service ":" { active=1; next }
    active && /^  [^ ]/ { active=0 }
    active && /^    image: / { sub(/^    image: /, ""); print; exit }
  ')"
  [[ "$value" =~ ^[A-Za-z0-9_./:@+-]+$ ]] || fail "Compose did not resolve a usable image for $1."
  printf '%s' "$value"
}
container_setting() {
  "$docker_cli" inspect --format "{{range .Config.Env}}{{println .}}{{end}}" "$1" | awk -v key="$2" 'index($0,key "=")==1 {print substr($0,length(key)+2)}'
}
check_config() {
  local service="$1" id="$2" expected actual network desired_network
  [ -n "$id" ] || return 0
  if [ "$service" = lab ]; then
    # Compose resolves service:postgres to container:<id> before hashing a
    # created app. Normalize only that field to its existing runtime namespace,
    # then compare every remaining desired setting against the stored hash.
    # A stale namespace is repaired separately after PostgreSQL becomes healthy.
    desired_network="$("${compose[@]}" config lab | awk '
      $0 == "  lab:" { active=1; next }
      active && /^  [^ ]/ { active=0 }
      active && /^    network_mode: / { sub(/^    network_mode: /, ""); print; exit }
    ')"
    [ "$desired_network" = service:postgres ] || fail 'The desired app network mode changed. Use ./classroom --rebuild to apply the updated configuration.'
    network="$("$docker_cli" inspect --format '{{.HostConfig.NetworkMode}}' "$id")"
    [[ "$network" =~ ^container:[a-f0-9]{64}$ ]] || fail 'The existing app uses an unexpected network mode. Use ./classroom --rebuild to apply the classroom configuration.'
    expected="$(printf 'services:\n  lab:\n    network_mode: %s\n' "$network" | "${compose[@]}" -f - config --hash "$service")"
  else
    expected="$("${compose[@]}" config --hash "$service")"
  fi
  expected="${expected#* }"
  actual="$("$docker_cli" inspect --format '{{index .Config.Labels "com.docker.compose.config-hash"}}' "$id")"
  [ -n "$actual" ] && [ "$expected" = "$actual" ] || fail "The $service configuration changed. Resume retains existing containers. Use ./classroom --rebuild with the same project/options to apply updates while keeping saved volumes."
}
postgres_id="$(container_id postgres)"
lab_id="$(container_id lab)"
old_public_port=''
if [ -n "$lab_id" ]; then
  old_public_port="$(container_setting "$lab_id" DS60_PUBLIC_PORT)"
  if valid_port "$old_public_port" && [ "$old_public_port" -gt 0 ]; then
    export DS60_PUBLIC_PORT="$old_public_port"
  elif [ "$rebuild" -eq 0 ]; then
    fail 'The existing app has no valid public port setting. Use ./classroom --rebuild to update it.'
  fi
fi
# Compare config before starting anything. An explicit rebuild is the deliberate
# route for applying port, environment and runtime-setting changes.
if [ "$rebuild" -eq 0 ]; then
  check_config postgres "$postgres_id"
  check_config lab "$lab_id"
  for service in "${services[@]}"; do check_config "$service" "$(container_id "$service")"; done
fi
settings_temp="$(mktemp "$state_dir/ports.XXXXXX")"
printf 'DS60_CLASSROOM_PORT=%s\nDS60_POSTGRES_PORT=%s\n' "$browser_port" "$database_port" >"$settings_temp"
mv -f "$settings_temp" "$state_dir/ports.env"
app_image="$(image_for lab)"
restore_app_image_name() {
  local original_name image_id
  "$docker_cli" image inspect "$app_image" >/dev/null 2>&1 && return 0
  [ -n "$lab_id" ] || return 1
  original_name="$("$docker_cli" inspect --format '{{.Config.Image}}' "$lab_id")" || return 1
  [ "$original_name" = "$app_image" ] || return 1
  image_id="$("$docker_cli" inspect --format '{{.Image}}' "$lab_id")" || return 1
  [[ "$image_id" =~ ^sha256:[a-f0-9]{64}$ ]] || return 1
  "$docker_cli" image inspect "$image_id" >/dev/null 2>&1 || return 1
  # A stopped container still owns its immutable image even after its tag was
  # removed. Recover only its matching missing name; never replace an existing
  # tag or fetch/build anything to perform this local repair.
  "$docker_cli" image inspect "$app_image" >/dev/null 2>&1 && return 0
  printf '\nRestoring the missing app image name from its existing local image...\n'
  "$docker_cli" image tag "$image_id" "$app_image"
}
missing_services=()
build_services=()
if [ "$rebuild" -eq 1 ]; then
  build_services=(lab "${services[@]}")
else
  for service in lab "${services[@]}"; do
    if [ -z "$(container_id "$service")" ]; then
      image="$(image_for "$service")"
      if ! "$docker_cli" image inspect "$image" >/dev/null 2>&1; then missing_services+=("$service"); fi
    fi
  done
  build_services=(${missing_services[@]+"${missing_services[@]}"})
fi
need_database=0
if { [ -z "$postgres_id" ] || [ "$rebuild" -eq 1 ]; } && ! "$docker_cli" image inspect "$db_image" >/dev/null 2>&1; then need_database=1; fi
# New app/worker containers may require the shared initializer image even when
# an old lab exists and its tag was removed. Existing containers need no image tag.
need_initializer=0
[ -n "$lab_id" ] || need_initializer=1
# Building Core directly also needs the prepared app image as its base.
for service in ${build_services[@]+"${build_services[@]}"}; do [ "$service" != python-core-worker ] || need_initializer=1; done
if [ "$need_initializer" -eq 1 ] && ! restore_app_image_name; then
  have_lab_build=0
  for service in ${build_services[@]+"${build_services[@]}"}; do [ "$service" != lab ] || have_lab_build=1; done
  [ "$have_lab_build" -eq 1 ] || build_services=(lab ${build_services[@]+"${build_services[@]}"})
fi
if [ "$no_build" -eq 1 ] && { [ "$need_database" -eq 1 ] || [ "${#build_services[@]}" -gt 0 ]; }; then
  fail "Required local images are missing (database=$need_database; services: ${build_services[*]-}). Resume never builds or pulls. Run ./classroom with the same project/options to prepare only missing images."
fi
if [ "$need_database" -eq 1 ]; then "${compose[@]}" pull postgres; fi
for service in ${build_services[@]+"${build_services[@]}"}; do
  if [ "$image_source" = hub ]; then
    printf '\nPulling published %s for %s...\n' "$service" "$image_arch"
    "${compose[@]}" pull --policy always "$service"
    continue
  fi
  printf '\nBuilding missing/requested %s locally...\n' "$service"
  if [ "$service" = python-core-worker ]; then
    # The Compose service:lab additional context would rebuild the app as a
    # dependency. Use its already prepared image directly for this small worker.
    worker_image="$(image_for "$service")"
    "$docker_cli" build --progress plain --pull=false --build-arg "DS60_CORE_IMAGE=$app_image" --file "$repo_dir/docker/workers/Dockerfile.python-core" --tag "$worker_image" "$repo_dir"
  else
    "${compose[@]}" build "$service"
  fi
done
verify_hub_prepared_images
if [ "$action" = build ] || [ "$action" = pull ]; then
  printf 'Selected images are ready. Use ./classroom --rebuild to apply an update, or ./classroom resume to retain existing containers.\n'
  exit 0
fi
wait_for_container() {
  local service="$1" id="$2" timeout="$3" deadline status health extra state
  deadline=$((SECONDS + timeout))
  while :; do
    state="$("$docker_cli" inspect --format '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$id")" || fail "Could not inspect the resumed $service container. Saved volumes are retained; inspect ./classroom status with the same project."
    read -r status health extra <<<"$state"
    [ -z "${extra:-}" ] || fail "Docker returned an unexpected state for $service. Saved volumes are retained."
    case "$status:$health" in
      running:healthy | running:none) return 0 ;;
      *:unhealthy | exited:* | dead:* | paused:* | removing:*) fail "The resumed $service container is $status (health: $health). Saved volumes are retained; inspect its logs before retrying." ;;
      running:starting | created:* | restarting:*) ;;
      *) fail "Docker returned an unexpected state for $service. Saved volumes are retained." ;;
    esac
    [ "$SECONDS" -lt "$deadline" ] || fail "Timed out after ${timeout}s waiting for the resumed $service container to become healthy. Saved volumes are retained; inspect its logs before retrying."
    sleep 1
  done
}
start_existing() {
  local service="$1" id="$2" timeout="$3"
  # Compose 2.28 supports start but not start --wait. Poll the exact original
  # container through the stable Docker inspect API so resume stays portable.
  "${compose[@]}" start "$service"
  wait_for_container "$service" "$id" "$timeout"
}
start_or_create() {
  local service="$1" timeout="$2" id
  id="$(container_id "$service")"
  if [ -n "$id" ] && [ "$rebuild" -eq 0 ]; then
    printf '\nResuming existing %s...\n' "$service"
    start_existing "$service" "$id" "$timeout"
  else
    printf '\nStarting %s from local images...\n' "$service"
    if [ "$rebuild" -eq 1 ]; then
      "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout "$timeout" "$service"
    else
      "${compose[@]}" up -d --no-recreate --no-build --pull never --wait --wait-timeout "$timeout" "$service"
    fi
  fi
}
start_or_create postgres 180
url="$(published_url)" || fail 'Docker did not report a loopback browser mapping for this project.'
public_port="${url#http://127.0.0.1:}"
public_port="${public_port%/classroom}"
export DS60_PUBLIC_PORT="$public_port"
# If PostgreSQL was recreated externally, an old app still points at the old
# network namespace. A changed dynamic host port also needs the exact Host/Origin
# setting updated. Repair only that app container, using an existing local image.
postgres_now="$(container_id postgres)"
repair_lab=0
if [ -n "$lab_id" ] && [ "$rebuild" -eq 0 ]; then
  lab_network="$("$docker_cli" inspect --format '{{.HostConfig.NetworkMode}}' "$lab_id")"
  if [ "$old_public_port" != "$public_port" ] || [ "$lab_network" != "container:$postgres_now" ]; then repair_lab=1; fi
fi
if [ "$repair_lab" -eq 1 ]; then
  restore_app_image_name || fail 'The app needs its network/public-port setting repaired but its matching local image could not be recovered. Saved volumes are retained. Use ./classroom --rebuild with the same project/options.'
  original_image_id="$("$docker_cli" inspect --format '{{.Image}}' "$lab_id")"
  repair_image_id="$("$docker_cli" image inspect --format '{{.Id}}' "$app_image")"
  [[ "$original_image_id" =~ ^sha256:[a-f0-9]{64}$ ]] && [ "$original_image_id" = "$repair_image_id" ] || fail 'The app image name now points to a different image. Resume will not silently upgrade it. Use ./classroom --rebuild with the same project/options to apply the update; saved volumes are retained.'
  printf '\nRepairing the app connection to the current database container; saved volumes are retained.\n'
  "${compose[@]}" up -d --no-deps --force-recreate --no-build --pull never --wait --wait-timeout 180 lab
else
  start_or_create lab 180
fi
# New workers need the initializer completed, but starting old workers should
# preserve their IDs and should not trigger dependency recreation.
for service in "${services[@]}"; do
  id="$(container_id "$service")"
  if [ -n "$id" ] && [ "$rebuild" -eq 0 ]; then
    start_existing "$service" "$id" 120
  else
    "${compose[@]}" up -d --no-deps --no-build --pull never --wait --wait-timeout 120 "$service"
  fi
done
"${compose[@]}" exec -T lab python /opt/course/docker/healthcheck.py
url="$(published_url)" || fail 'The containers are healthy, but their loopback browser address could not be determined. Use ./classroom status.'
# Verify the host-facing route too, including its exact Host header.
if command -v curl >/dev/null 2>&1; then
  curl --noproxy '*' --fail --silent --show-error --max-time 10 "$url" >/dev/null || fail 'The host browser URL is not reachable. Keep the error, check the engine port forwarding, and use ./classroom --rebuild with the same project/options if images are outdated.'
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
    fail 'The host browser URL did not return HTTP 200. Check the engine and use ./classroom --rebuild with the same project/options if images are outdated.'
  fi
fi
[ ! -d "$state_dir/classroom.url" ] || fail 'The classroom URL path is a directory; it was preserved.'
url_temp="$(mktemp "$state_dir/url.XXXXXX")"
printf '%s\n' "$url" >"$url_temp"
mv -f "$url_temp" "$state_dir/classroom.url"
printf '\nReady: %s\nSaved learning and database data remain in project %s Docker volumes.\nStop safely with: ./classroom stop --project %s\n' "$url" "$project_name" "$project_name"
if [ "$no_browser" -eq 0 ]; then
  if [ "$(uname -s)" = Darwin ] && command -v open >/dev/null 2>&1; then
    open "$url" || printf 'Open %s in your browser.\n' "$url"
  elif [ -n "${WSL_DISTRO_NAME:-}" ] || { [ -r /proc/sys/kernel/osrelease ] && grep -qi microsoft /proc/sys/kernel/osrelease; }; then
    if command -v wslview >/dev/null 2>&1; then
      wslview "$url" || printf 'Open %s in your Windows browser.\n' "$url"
    elif command -v cmd.exe >/dev/null 2>&1; then
      cmd.exe /c start '' "$url" || printf 'Open %s in your Windows browser.\n' "$url"
    else printf 'Open %s in your Windows browser.\n' "$url"; fi
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1 || printf 'Open %s in your browser.\n' "$url"
  else printf 'Open %s in your browser.\n' "$url"; fi
fi
