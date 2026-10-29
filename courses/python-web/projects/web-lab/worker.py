"""One durable worker; PostgreSQL row locks also keep overlapping workers safe."""

import signal
import threading

import store

stop = threading.Event()


def request_stop(signum, frame):
    stop.set()


signal.signal(signal.SIGTERM, request_stop)
signal.signal(signal.SIGINT, request_stop)
while not stop.is_set():
    store.worker_tick()
    stop.wait(0.2)
