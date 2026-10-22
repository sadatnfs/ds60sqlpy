#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
bash scripts/docker_lab.sh "$@"
result=$?
if [ "$result" -ne 0 ]; then read -r -p 'Press Enter to close this window.'; fi
exit "$result"
