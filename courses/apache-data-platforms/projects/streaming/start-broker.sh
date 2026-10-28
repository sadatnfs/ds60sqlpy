#!/usr/bin/env bash
set -euo pipefail
[[ ${CLUSTER_ID:-} =~ ^[A-Za-z0-9_-]{22}$ ]] || {
  echo 'Invalid owned cluster identity.' >&2
  exit 2
}
data=/var/lib/kafka/data
if [[ ! -f $data/meta.properties ]]; then
  [[ -z $(find "$data" -mindepth 1 -maxdepth 1 -print -quit) ]] || {
    echo 'Data exists without meta.properties. Refusing to reformat; inspect the owned volume.' >&2
    exit 2
  }
  /opt/kafka/bin/kafka-storage.sh format --cluster-id "$CLUSTER_ID" --config /project/server.properties
else
  recorded=$(sed -n 's/^cluster.id=//p' "$data/meta.properties")
  [[ $recorded == "$CLUSTER_ID" ]] || {
    echo 'Persisted Kafka cluster identity mismatch.' >&2
    exit 2
  }
fi
exec /opt/kafka/bin/kafka-server-start.sh /project/server.properties
