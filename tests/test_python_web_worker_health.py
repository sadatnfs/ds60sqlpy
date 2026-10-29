"""A worker health check must observe a recent completed poll and a live process."""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from types import ModuleType

import pytest

PROJECT = Path(__file__).resolve().parents[1] / "courses/python-web/projects/web-lab"


@pytest.fixture
def modules(monkeypatch: pytest.MonkeyPatch) -> tuple[ModuleType, ModuleType]:
    monkeypatch.syspath_prepend(str(PROJECT))
    return importlib.import_module("worker_health"), importlib.import_module("worker")


def test_poll_and_clean_stop(tmp_path: Path, modules: tuple[ModuleType, ModuleType]) -> None:
    health, worker = modules
    path = tmp_path / "heartbeat"
    stop = threading.Event()
    calls = []

    def tick() -> None:
        assert not path.exists()
        calls.append("committed")
        stop.set()

    worker.run(tick, stop, path)
    assert calls == ["committed"] and not path.exists()
    health.record_poll(path)
    assert health.healthy(path)
    assert path.stat().st_mode & 0o777 == 0o600


def test_failed_tick_never_renews_old_heartbeat(
    tmp_path: Path, modules: tuple[ModuleType, ModuleType]
) -> None:
    health, worker = modules
    path = tmp_path / "heartbeat"
    health.record_poll(path)

    def failed_tick() -> None:
        assert not path.exists()
        raise RuntimeError("database unavailable")

    with pytest.raises(RuntimeError, match="database unavailable"):
        worker.run(failed_tick, threading.Event(), path)
    assert not path.exists() and not health.healthy(path)


@pytest.mark.parametrize(
    "content", [b"not json", b"{}", b"x" * 257, b'{"pid":true,"completed_monotonic":0}']
)
def test_invalid_heartbeat(
    tmp_path: Path, modules: tuple[ModuleType, ModuleType], content: bytes
) -> None:
    health, _ = modules
    path = tmp_path / "heartbeat"
    path.write_bytes(content)
    assert not health.healthy(path)


def test_stale_future_nonfinite_and_dead_process(
    tmp_path: Path, modules: tuple[ModuleType, ModuleType], monkeypatch: pytest.MonkeyPatch
) -> None:
    health, _ = modules
    path = tmp_path / "heartbeat"
    monkeypatch.setattr(health.time, "monotonic", lambda: 100.0)
    for timestamp in (84.9, 100.1, float("nan"), float("inf")):
        path.write_text(json.dumps({"pid": os.getpid(), "completed_monotonic": timestamp}))
        assert not health.healthy(path)
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait(timeout=10)
    path.write_text(json.dumps({"pid": child.pid, "completed_monotonic": 100.0}))
    assert not health.healthy(path)


def test_symlink_is_not_read(tmp_path: Path, modules: tuple[ModuleType, ModuleType]) -> None:
    health, _ = modules
    target = tmp_path / "target"
    health.record_poll(target)
    link = tmp_path / "link"
    link.symlink_to(target)
    assert not health.healthy(link)
