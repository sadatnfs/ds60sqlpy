#!/usr/bin/env bash
set -euo pipefail
[[ $# == 2 ]] || {
  echo 'Use the parent run.sh ipc-check action.' >&2
  exit 2
}
platform_image=$1
docker_cmd=$2
[[ $platform_image =~ ^ds60sqlpy-worker-data-platforms-python:([0-9]+\.[0-9]+\.[0-9]+)$ ]] || exit 2
rust_image=ds60sqlpy-worker-rust-stable:${BASH_REMATCH[1]}
engine=$("$docker_cmd" info --format '{{.OSType}}|{{.Architecture}}')
case "$engine" in
  'linux|aarch64' | 'linux|arm64') engine='linux|arm64' ;;
  'linux|x86_64' | 'linux|amd64') engine='linux|amd64' ;;
  *)
    echo 'Use a native Linux AMD64 or ARM64 engine.' >&2
    exit 2
    ;;
esac
for image in "$platform_image" "$rust_image"; do
  actual=$("$docker_cmd" image inspect --format '{{.Os}}|{{.Architecture}}' "$image")
  [[ $actual == "$engine" ]] || {
    echo 'Prepare both native classroom images; automatic emulation is disabled.' >&2
    exit 2
  }
done
workspace=$(mktemp -d "${TMPDIR:-/tmp}/ds60-arrow-ipc.XXXXXXXX")
cleanup() {
  rm -f "$workspace/input.arrow" "$workspace/output.arrow"
  rmdir "$workspace"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
base=("$docker_cmd" run --rm --network none --read-only --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges:true --pids-limit 128 --memory 1g --cpus 2 -v "$PWD:/project:ro")
"${base[@]}" --tmpfs /tmp:rw,nosuid,noexec,size=64m --entrypoint python3 "$platform_image" /project/ipc_fixture.py write >"$workspace/input.arrow"
"${base[@]}" -i --tmpfs /tmp:rw,nosuid,exec,size=256m --workdir /tmp --entrypoint bash "$rust_image" -c 'rustc --edition=2024 -C debuginfo=0 -L dependency=/opt/course-rust/target/release/deps --extern arrow=/opt/course-rust/libarrow.rlib /project/ipc_bridge.rs -o /tmp/bridge && exec /tmp/bridge' <"$workspace/input.arrow" >"$workspace/output.arrow"
"${base[@]}" -i --tmpfs /tmp:rw,nosuid,noexec,size=64m --entrypoint python3 "$platform_image" /project/ipc_fixture.py read <"$workspace/output.arrow"
