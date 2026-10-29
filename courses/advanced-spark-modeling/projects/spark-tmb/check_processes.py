"""Actual process cleanup checks using a stub interpreter, not model evidence."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from runner import execute
from spark_tmb import evaluate_prepared
from spark_tmb.fixed_bridge import PreparedTMB, evaluate_r, request_for

ROOT = Path(__file__).resolve().parent


def running(pid):
    if sys.platform.startswith("linux"):
        try:
            return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"
        except FileNotFoundError:
            return False
    result = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True)
    return bool(result.stdout.strip()) and not result.stdout.strip().startswith("Z")


def fixture(root):
    """Fake library bytes exercise process ownership only, never a native load."""
    project, build = root / "project", root / "build"
    (project / "models").mkdir(parents=True)
    build.mkdir()
    shutil.copyfile(ROOT / "registry.json", project / "registry.json")
    for path in (ROOT / "models").glob("*.cpp"):
        shutil.copyfile(path, project / "models" / path.name)
    library = build / "normal_mean.so"
    library.write_bytes(b"process lifecycle fixture; not compiled code")

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    (build / "receipt.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "registry_sha256": digest(project / "registry.json"),
                "abi": {
                    "R": "4.6.1",
                    "TMB": "1.9.25",
                    "Matrix": "1.7.6",
                    "architecture": "fixture",
                },
                "models": {
                    "normal_mean": {
                        "library": "normal_mean.so",
                        "library_sha256": digest(library),
                        "source_sha256": digest(project / "models/normal_mean.cpp"),
                    }
                },
            }
        )
    )
    return project, build


def run_checks():
    results = []
    with tempfile.TemporaryDirectory(prefix="tmb-cleanup-check-") as directory:
        temporary = Path(directory)
        project, build = fixture(temporary)
        actual_popen = subprocess.Popen
        for adapter in ("runner", "registry", "fixed-bridge"):
            for mode in ("parent-exit", "timeout"):
                pidfile = temporary / f"{adapter}-{mode}.pid"
                ready = temporary / f"{adapter}-{mode}.ready"
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

                def launch(arguments, *args, parent_source=parent, **kwargs):
                    # Substitute only the interpreter command, preserving real
                    # Popen/session/stdout/timeout behavior. /tmp may be noexec.
                    if arguments[0] == "Rscript":
                        arguments = [sys.executable, "-c", parent_source]
                    return actual_popen(arguments, *args, **kwargs)

                budget = 3 if mode == "parent-exit" else 1
                pid = None
                try:
                    with patch.object(subprocess, "Popen", side_effect=launch):
                        try:
                            if adapter == "runner":
                                execute([sys.executable, "-c", parent], seconds=budget)
                            elif adapter == "registry":
                                evaluate_prepared(
                                    "normal_mean",
                                    {"y": [1, 2]},
                                    [0, 0],
                                    root=project,
                                    build_dir=build,
                                    timeout=budget,
                                )
                            else:
                                request = request_for(
                                    "normal_mean",
                                    [
                                        {"row_id": "a", "group_id": "g", "y": 1},
                                        {"row_id": "b", "group_id": "g", "y": 2},
                                    ],
                                    [0, 0],
                                )
                                evaluate_r(request, PreparedTMB(str(project), str(build), budget))
                        except SystemExit as exc:
                            assert adapter == "runner" and mode == "parent-exit" and exc.code == 7
                        except subprocess.TimeoutExpired:
                            assert mode == "timeout"
                        except ValueError as exc:
                            assert (
                                adapter != "runner" and mode == "parent-exit" and "(7)" in str(exc)
                            )
                        else:
                            raise AssertionError("Failed or expired process was accepted")
                    pid = int(pidfile.read_text())
                    for _ in range(50):
                        if not running(pid):
                            break
                        time.sleep(0.02)
                    assert not running(pid), f"{adapter} left a SIGTERM-ignoring descendant alive"
                    results.append({"adapter": adapter, "mode": mode, "descendant_stopped": True})
                finally:
                    if pid is None and pidfile.exists():
                        pid = int(pidfile.read_text())
                    if pid is not None and running(pid):
                        os.kill(pid, signal.SIGKILL)
    return results


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "case": "process-cleanup",
                "checks": run_checks(),
                "scope": "real subprocess lifecycle with a stub interpreter, not model execution",
            }
        )
    )
