#!/usr/bin/env bash
set -euo pipefail
python3 /project/configure.py
exec /opt/cassandra/bin/cassandra -f
