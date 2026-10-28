#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
cd "$project_dir"
[[ $# == 2 ]] || {
  echo 'Use the fixed workshop prepare action.' >&2
  exit 2
}
hive_image=$1 java_image=$2
[[ $hive_image == ds60-apache-hive-upstream:4.2.1 && $java_image =~ ^ds60sqlpy-worker-java21:[0-9]+\.[0-9]+\.[0-9]+$ ]] || exit 2
unset DOCKER_DEFAULT_PLATFORM
if command -v docker >/dev/null 2>&1; then docker_cmd=$(command -v docker); else docker_cmd=${HOME}/.rd/bin/docker; fi
if [[ -n ${DOCKER_CONTEXT:-} ]]; then
  endpoint=$("$docker_cmd" context inspect "$DOCKER_CONTEXT" --format '{{.Endpoints.docker.Host}}')
elif [[ -n ${DOCKER_HOST:-} ]]; then
  endpoint=$DOCKER_HOST
else endpoint=$("$docker_cmd" context inspect --format '{{.Endpoints.docker.Host}}'); fi
[[ $endpoint == unix://* ]] || {
  echo 'Use a local Unix-socket Docker engine.' >&2
  exit 2
}
engine=$("$docker_cmd" info --format '{{.OSType}}|{{.Architecture}}')
case "$engine" in
  'linux|aarch64' | 'linux|arm64') engine='linux|arm64' ;;
  'linux|x86_64' | 'linux|amd64') engine='linux|amd64' ;;
  *)
    echo 'Use a native Linux engine; automatic emulation is disabled.' >&2
    exit 2
    ;;
esac
for selected in "$hive_image" "$java_image"; do
  actual=$("$docker_cmd" image inspect --format '{{.Os}}|{{.Architecture}}' "$selected")
  [[ $actual == "$engine" ]] || {
    echo 'Prepare the native image; automatic emulation is disabled.' >&2
    exit 2
  }
  declared=$("$docker_cmd" image inspect --format '{{json .Config.Volumes}}' "$selected")
  [[ $declared == null || $declared == '{}' ]] || {
    echo 'Unexpected image-declared volumes.' >&2
    exit 2
  }
done
hive_id=$("$docker_cmd" image inspect --format '{{.Id}}' "$hive_image")
java_id=$("$docker_cmd" image inspect --format '{{.Id}}' "$java_image")
[[ $hive_id =~ ^sha256:[a-f0-9]{64}$ && $java_id =~ ^sha256:[a-f0-9]{64}$ ]] || exit 2
[[ ! -L .workshop ]] || exit 2
mkdir -p .workshop
[[ ! -e .workshop/preparation.owner && ! -L .workshop/preparation.owner ]] || {
  echo 'Earlier metadata preparation requires ownership reconciliation; no replay occurred.' >&2
  exit 2
}
[[ ! -L .workshop/preparation-lock ]] || exit 2
mkdir .workshop/preparation-lock 2>/dev/null || {
  echo 'Metadata preparation is already locked; inspect its owner.' >&2
  exit 2
}
printf '%s\n' "$$" >.workshop/preparation-lock/pid
owner=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
[[ $owner =~ ^[a-f0-9]{32}$ ]] || exit 2
(
  umask 077
  set -o noclobber
  printf '%s\n' "$owner" >.workshop/preparation.owner
)
stage="$PWD/.workshop/metadata-build-$owner"
mkdir "$stage"
cleanup() {
  local ids id actual role image state saved_owner kind
  [[ -f .workshop/preparation.owner && ! -L .workshop/preparation.owner && $(cat .workshop/preparation.owner) == "$owner" ]] || return 2
  ids=$("$docker_cmd" ps -aq --no-trunc --filter "label=org.ds60.workshop.owner=$owner" --filter 'label=org.ds60.workshop.kind=apache-hive-preparation') || return 2
  for id in $ids; do
    [[ $id =~ ^[a-f0-9]{64}$ ]] || return 2
    actual=$("$docker_cmd" inspect --format '{{index .Config.Labels "org.ds60.workshop.owner"}}|{{index .Config.Labels "org.ds60.workshop.kind"}}|{{index .Config.Labels "org.ds60.workshop.role"}}|{{.Image}}|{{.State.Status}}' "$id") || return 2
    IFS='|' read -r saved_owner kind role image state <<<"$actual"
    [[ $saved_owner == "$owner" && $kind == apache-hive-preparation ]] || return 2
    case "$role" in
      classpath) [[ $image == "$hive_id" && $state == created ]] || return 2 ;;
      compiler | verifier)
        [[ $image == "$java_id" ]] || return 2
        case "$state" in
          running) "$docker_cmd" stop --time 10 "$id" >/dev/null || return 2 ;;
          created | exited) ;;
          *) return 2 ;;
        esac
        ;;
      *) return 2 ;;
    esac
    "$docker_cmd" rm "$id" >/dev/null || return 2
  done
  [[ -z $("$docker_cmd" ps -aq --no-trunc --filter "label=org.ds60.workshop.owner=$owner" --filter 'label=org.ds60.workshop.kind=apache-hive-preparation') ]] || return 2
  [[ $stage == "$PWD/.workshop/metadata-build-$owner" && -d $stage && ! -L $stage ]] || return 2
  rm -rf "$stage" || return 2
  rm .workshop/preparation.owner || return 2
}
finish() {
  local code=$?
  trap - EXIT INT TERM
  if cleanup; then
    if [[ -f .workshop/preparation-lock/pid && ! -L .workshop/preparation-lock/pid && $(cat .workshop/preparation-lock/pid) == "$$" ]]; then
      rm .workshop/preparation-lock/pid || code=2
      rmdir .workshop/preparation-lock || code=2
    else code=2; fi
  else
    echo 'Preparation resources are uncertain; retained owner/stage require reconciliation.' >&2
    code=2
  fi
  exit "$code"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
common=("$docker_cmd" create --pull never --network none --memory 512m --cpus 1 --pids-limit 128 --read-only --cap-drop ALL --security-opt no-new-privileges --user "$(id -u):$(id -g)" --tmpfs "/tmp:rw,nosuid,noexec,size=64m" --entrypoint python3
--label "org.ds60.workshop.owner=$owner" --label org.ds60.workshop.kind=apache-hive-preparation
--env "DS60_HIVE_SOURCE_IMAGE_ID=$hive_id" --env "DS60_HIVE_JAVA_IMAGE_ID=$java_id"
--mount "type=bind,source=$PWD/prepare_metadata.py,target=/project/prepare_metadata.py,readonly"
--mount "type=bind,source=$PWD/MetadataProbe.java,target=/project/MetadataProbe.java,readonly")
if [[ -e .workshop/metadata-client || -L .workshop/metadata-client ]]; then
  [[ -d .workshop/metadata-client && ! -L .workshop/metadata-client ]] || exit 2
  client=$("${common[@]}" --name "ds60-hive-verify-$owner" --label org.ds60.workshop.role=verifier --mount "type=bind,source=$PWD/.workshop/metadata-client,target=/prepared,readonly" "$java_id" /project/prepare_metadata.py verify)
else
  container=$("$docker_cmd" create --pull never --network none --entrypoint /bin/true --name "ds60-hive-classpath-$owner" --label "org.ds60.workshop.owner=$owner" --label org.ds60.workshop.kind=apache-hive-preparation --label org.ds60.workshop.role=classpath "$hive_id")
  [[ $container =~ ^[a-f0-9]{64}$ ]] || exit 2
  "$docker_cmd" cp "$container:/opt/hive/lib" "$stage/hive-lib"
  "$docker_cmd" cp "$container:/opt/hadoop/share/hadoop/common" "$stage/hadoop-common"
  client=$("${common[@]}" --name "ds60-hive-compile-$owner" --label org.ds60.workshop.role=compiler --mount "type=bind,source=$stage,target=/prepared" "$java_id" /project/prepare_metadata.py compile)
fi
[[ $client =~ ^[a-f0-9]{64}$ ]] || exit 2
"$docker_cmd" start --attach "$client"
[[ $("$docker_cmd" inspect --format '{{.State.ExitCode}}' "$client") == 0 ]] || exit 2
if [[ ! -e .workshop/metadata-client ]]; then
  mkdir "$stage/accepted"
  mv "$stage/classes" "$stage/identity.tsv" "$stage/accepted/"
  mv "$stage/accepted" .workshop/metadata-client
fi
