#!/usr/bin/env bash
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
image=${DS60_DATA_IMAGE:-ds60sqlpy-worker-data-engineering:1.3.0}
exec docker run --rm --pull never --init --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
  --tmpfs /tmp:rw,nosuid,size=256m --env HOME=/tmp \
  --env DBT_SEND_ANONYMOUS_USAGE_STATS=false --env DO_NOT_TRACK=true \
  --mount "type=bind,src=$project_dir,dst=/project" --workdir /project \
  --entrypoint dbt "$image" --no-send-anonymous-usage-stats "$@" --profiles-dir /project
