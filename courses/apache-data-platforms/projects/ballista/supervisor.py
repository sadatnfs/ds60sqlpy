"""Own exact native service subprocesses and a private bounded control socket."""

from __future__ import annotations

import json
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

SOCKET = "/tmp/ds60-ballista-control.sock"
stop = threading.Event()
children: dict[str, subprocess.Popen[bytes]] = {}
slots = 1


def listening(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
            return True
    except OSError:
        return False


def halt(name: str) -> None:
    child = children.pop(name, None)
    if child is None:
        return
    if child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=5)
    else:
        child.wait()


def launch(name: str) -> None:
    if name in children and children[name].poll() is None:
        raise ValueError("Role is already running")
    command = [sys.executable, "/project/role.py", name]
    if name == "executor":
        command.extend(["--slots", str(slots)])
    child = subprocess.Popen(command)
    children[name] = child
    ports = [50050] if name == "scheduler" else [50051, 50052]
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if child.poll() is not None:
            raise RuntimeError("Native role exited before readiness")
        if all(listening(port) for port in ports):
            return
        time.sleep(0.1)
    raise TimeoutError("Native role did not become ready")


def state() -> dict[str, object]:
    return {
        "scheduler_pid": children["scheduler"].pid,
        "executor_pid": None if "executor" not in children else children["executor"].pid,
        "scheduler_alive": children["scheduler"].poll() is None,
        "executor_alive": "executor" in children and children["executor"].poll() is None,
        "task_slots": slots,
    }


def handle(action: str) -> dict[str, object]:
    global slots
    if action == "health":
        current = state()
        if (
            not current["scheduler_alive"]
            or not current["executor_alive"]
            or not all(listening(p) for p in [50050, 50051, 50052])
        ):
            raise RuntimeError("Known service subprocess is not ready")
    elif action in ("one-slot", "two-slots"):
        halt("executor")
        halt("scheduler")
        slots = 1 if action == "one-slot" else 2
        launch("scheduler")
        launch("executor")
    elif action == "stop-executor":
        halt("executor")
    elif action == "start-executor":
        launch("executor")
    elif action == "restart-scheduler":
        halt("executor")
        halt("scheduler")
        launch("scheduler")
        launch("executor")
    else:
        raise ValueError("Unknown owned control action")
    return state()


def respond(connection: socket.socket, result: dict[str, object]) -> bool:
    """A disconnected observer must not terminate the native service owner."""
    try:
        connection.sendall(json.dumps(result).encode())
    except OSError:
        return False
    return True


def main() -> None:
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    if Path(SOCKET).exists() or Path(SOCKET).is_symlink():
        raise ValueError("Unexpected control socket path")
    try:
        launch("scheduler")
        launch("executor")
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(SOCKET)
            Path(SOCKET).chmod(0o600)
            server.listen(2)
            server.settimeout(0.5)
            while not stop.is_set():
                try:
                    connection, _ = server.accept()
                except TimeoutError:
                    continue
                with connection:
                    connection.settimeout(2)
                    raw = connection.recv(1025)
                    try:
                        if len(raw) > 1024:
                            raise ValueError("Control request exceeds budget")
                        request = json.loads(raw)
                        if type(request) is not dict or set(request) != {"action"}:
                            raise ValueError("Unexpected control fields")
                        result = {"passed": True, **handle(request["action"])}
                    except Exception as error:
                        result = {
                            "passed": False,
                            "error_type": type(error).__name__,
                            "error": str(error),
                        }
                    respond(connection, result)
    finally:
        halt("executor")
        halt("scheduler")
        Path(SOCKET).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
