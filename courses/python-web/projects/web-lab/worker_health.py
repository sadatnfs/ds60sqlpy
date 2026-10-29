"""Readiness means this live worker recently completed a PostgreSQL job poll."""

from __future__ import annotations

import json
import math
import os
import stat
import tempfile
import time
from pathlib import Path

HEARTBEAT = Path("/tmp/web-worker-heartbeat.json")
MAX_AGE_SECONDS = 15.0


def record_poll(path: Path = HEARTBEAT) -> None:
    payload = json.dumps({"pid": os.getpid(), "completed_monotonic": time.monotonic()})
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=path.parent, prefix=".worker-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def healthy(path: Path = HEARTBEAT) -> bool:
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_size > 256:
                return False
            value = json.loads(stream.read(257))
        if not isinstance(value, dict) or set(value) != {"pid", "completed_monotonic"}:
            return False
        pid, completed = value["pid"], value["completed_monotonic"]
        if type(pid) is not int or pid <= 0 or type(completed) not in (float, int):
            return False
        if not math.isfinite(completed) or not 0 <= time.monotonic() - completed <= MAX_AGE_SECONDS:
            return False
        os.kill(pid, 0)
        return True
    except (OSError, ValueError, TypeError, OverflowError):
        return False


if __name__ == "__main__":
    raise SystemExit(0 if healthy() else 1)
