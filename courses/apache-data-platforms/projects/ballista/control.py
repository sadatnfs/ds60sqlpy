"""Use the local private socket, without an engine socket or external endpoint."""

from __future__ import annotations

import argparse
import json
import socket

parser = argparse.ArgumentParser()
parser.add_argument(
    "action",
    choices=[
        "health",
        "one-slot",
        "two-slots",
        "stop-executor",
        "start-executor",
        "restart-scheduler",
    ],
)
action = parser.parse_args().action
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
    client.settimeout(75)
    client.connect("/tmp/ds60-ballista-control.sock")
    client.sendall(json.dumps({"action": action}).encode())
    client.shutdown(socket.SHUT_WR)
    raw = bytearray()
    while chunk := client.recv(1024):
        raw.extend(chunk)
        if len(raw) > 4096:
            raise ValueError("Control response exceeds budget")
result = json.loads(raw)
print(json.dumps(result))
if result.get("passed") is not True:
    raise SystemExit(2)
