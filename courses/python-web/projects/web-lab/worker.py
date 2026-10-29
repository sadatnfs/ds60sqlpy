"""One durable worker; PostgreSQL row locks also keep overlapping workers safe."""

from __future__ import annotations

import signal
import threading
from collections.abc import Callable
from pathlib import Path

from worker_health import HEARTBEAT, record_poll


def run(tick: Callable[[], object], stop: threading.Event, heartbeat: Path = HEARTBEAT) -> None:
    heartbeat.unlink(missing_ok=True)
    try:
        while not stop.is_set():
            tick()
            # Publish only after the job transaction completes successfully.
            record_poll(heartbeat)
            stop.wait(0.2)
    finally:
        heartbeat.unlink(missing_ok=True)


def main() -> None:
    import store

    stop = threading.Event()

    def request_stop(signum: int, frame: object) -> None:
        stop.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    run(store.worker_tick, stop)


if __name__ == "__main__":
    main()
