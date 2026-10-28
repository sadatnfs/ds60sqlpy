#!/usr/bin/env bash
set -euo pipefail
[[ $# == 1 ]] || {
  echo 'Use one fixed Flink service role.' >&2
  exit 2
}
case "$1" in jobmanager | taskmanager) role=$1 ;; *)
  echo 'Unknown service role.' >&2
  exit 2
  ;;
esac
export FLINK_HOME=/opt/flink
export FLINK_CONF_DIR=/project/conf
export FLINK_LOG_DIR=/state/logs/$role
export FLINK_PID_DIR=/tmp/flink-pids
mkdir -p "$FLINK_LOG_DIR" "$FLINK_PID_DIR"
exec "$FLINK_HOME/bin/$role.sh" start-foreground
