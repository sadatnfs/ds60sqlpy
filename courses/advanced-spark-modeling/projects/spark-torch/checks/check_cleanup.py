"""Actual Linux process checks for the project supervisor's cleanup boundary."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from check_package import run as capture
from runner import execute


def running(pid: int) -> bool:
    path = Path(f"/proc/{pid}/stat")
    try:
        # A killed child can briefly remain as a zombie awaiting the container
        # init's reap; it cannot execute learner code in that state.
        state = path.read_text().rsplit(")", 1)[1].split()[0]
        return state != "Z"
    except FileNotFoundError:
        return False


def run():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for adapter, mode in (
            (name, mode)
            for name in ("runner", "package-capture")
            for mode in ("parent-exit", "timeout")
        ):
            pidfile = root / f"{adapter}-{mode}.pid"
            ready = root / f"{adapter}-{mode}.ready"
            child = (
                "import signal,time,pathlib;"
                "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                f"pathlib.Path({str(ready)!r}).write_text('ready');"
                "time.sleep(60)"
            )
            parent = (
                "import pathlib,subprocess,sys,time\n"
                f"p=subprocess.Popen([sys.executable,'-c',{child!r}])\n"
                f"pathlib.Path({str(pidfile)!r}).write_text(str(p.pid))\n"
                f"while not pathlib.Path({str(ready)!r}).exists(): time.sleep(0.01)\n"
                + ("sys.exit(7)\n" if mode == "parent-exit" else "time.sleep(60)\n")
            )
            try:
                function = execute if adapter == "runner" else capture
                function([sys.executable, "-c", parent], seconds=1)
            except SystemExit as error:
                assert mode == "parent-exit" and error.code == 7
            except RuntimeError as error:
                assert adapter == "package-capture" and mode == "parent-exit"
                assert "exit 7" in str(error)
            except TimeoutError:
                assert adapter == "package-capture" and mode == "timeout"
            except subprocess.TimeoutExpired:
                assert mode == "timeout"
            else:
                raise AssertionError("failed/expired subprocess was accepted")
            pid = int(pidfile.read_text())
            for _ in range(50):
                if not running(pid):
                    break
                time.sleep(0.02)
            assert not running(pid), "orphaned descendant survived supervisor cleanup"
    print(
        json.dumps(
            {
                "kind": "linux-supervisor-descendant-cleanup",
                "passed": True,
                "parent_exit_and_timeout": True,
                "package_capture_parent_exit_and_timeout": True,
            }
        )
    )


if __name__ == "__main__":
    run()
