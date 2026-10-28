"""Run actual native Ballista service roles, as independent processes on one container host."""

from __future__ import annotations

import argparse
import signal
import threading

from ballista import BallistaExecutor, BallistaScheduler

parser = argparse.ArgumentParser()
parser.add_argument("role", choices=["scheduler", "executor"])
parser.add_argument("--slots", type=int, choices=[1, 2], default=1)
args = parser.parse_args()
stop = threading.Event()
signal.signal(signal.SIGTERM, lambda *_: stop.set())
signal.signal(signal.SIGINT, lambda *_: stop.set())
service = (
    BallistaScheduler(bind_host="127.0.0.1", bind_port=50050)
    if args.role == "scheduler"
    else BallistaExecutor(
        bind_host="127.0.0.1",
        bind_port=50051,
        scheduler_host="localhost",
        scheduler_port=50050,
        concurrent_tasks=args.slots,
    )
)
service.start()
try:
    stop.wait()
finally:
    service.close()
