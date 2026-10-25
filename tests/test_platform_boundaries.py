"""Platform guards preserve cleanup and refuse unsupported filesystem mutations."""

from __future__ import annotations

import importlib.util
import os
import signal
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

from ds60sqlpy import execution, kubernetes_module, worker_operations

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def initializer() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "platform_initializer_test", ROOT / "docker/init_module_runtime.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("entrypoint", ["initialize", "_initialize_locked"])
def test_windows_initializer_refuses_before_creating_storage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    initializer: ModuleType,
    entrypoint: str,
) -> None:
    runtime, learning = tmp_path / "runtime", tmp_path / "learning"
    monkeypatch.setattr(sys, "platform", "win32")
    with pytest.raises(initializer.InitializationRefusal, match="POSIX container runtime"):
        getattr(initializer, entrypoint)(runtime, learning, 1000, 1000)
    assert not runtime.exists() and not learning.exists()


@pytest.mark.parametrize("platform", ["win32", "darwin"])
def test_isolated_kubectl_refuses_unsupported_platform_before_writing_credentials(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    platform: str,
) -> None:
    config = tmp_path / "scoped.kubeconfig.json"
    config.write_bytes(b"previous synthetic configuration")
    monkeypatch.setattr(sys, "platform", platform)
    lease: Any = object()
    with pytest.raises(kubernetes_module.KubernetesRefusal, match="Linux credential supervisor"):
        kubernetes_module.KubectlClient(lease, tmp_path, isolate_user=True)
    assert config.read_bytes() == b"previous synthetic configuration"


def test_isolated_kubectl_refuses_non_root_linux_before_writing_credentials(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = tmp_path / "scoped.kubeconfig.json"
    config.write_bytes(b"previous synthetic configuration")
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(os, "geteuid", lambda: 1000, raising=False)
    lease: Any = object()
    with pytest.raises(kubernetes_module.KubernetesRefusal, match="Linux credential supervisor"):
        kubernetes_module.KubectlClient(lease, tmp_path, isolate_user=True)
    assert config.read_bytes() == b"previous synthetic configuration"


class Process:
    pid = 1234567

    def __init__(self) -> None:
        self.returncode: int | None = None
        self.kills = 0
        self.waits: list[float | None] = []

    def poll(self) -> int | None:
        return self.returncode

    def kill(self) -> None:
        self.kills += 1
        self.returncode = -9

    def wait(self, timeout: float | None = None) -> int:
        self.waits.append(timeout)
        self.returncode = 0
        return 0


@pytest.mark.parametrize("platform", ["linux", "darwin"])
def test_posix_worker_reaps_descendants_even_after_group_leader_exits(
    monkeypatch: pytest.MonkeyPatch,
    platform: str,
) -> None:
    signals: list[tuple[int, int]] = []
    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.setattr(signal, "SIGKILL", 9, raising=False)
    monkeypatch.setattr(os, "killpg", lambda pid, sig: signals.append((pid, sig)), raising=False)
    process = Process()
    worker_operations._stop_tree(cast(subprocess.Popen[bytes], process))
    assert signals == [(process.pid, signal.SIGTERM), (process.pid, 9)]
    assert process.waits == [0.25, 2] and process.returncode == 0


def test_posix_pad_and_cluster_cleanup_keep_process_group_kill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    signals: list[tuple[int, int]] = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(signal, "SIGKILL", 9, raising=False)
    monkeypatch.setattr(os, "killpg", lambda pid, sig: signals.append((pid, sig)), raising=False)
    for stop in (execution.PadRunner._stop, kubernetes_module._stop):
        stop(cast(subprocess.Popen[bytes], Process()))
    assert signals == [(Process.pid, 9), (Process.pid, 9)]


def test_unsupported_native_worker_cleanup_does_not_use_posix_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    commands: list[list[str]] = []
    monkeypatch.setattr(sys, "platform", "win32")

    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("Windows must not use POSIX group signaling")

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        commands.append(command)
        assert kwargs["timeout"] == 5
        return subprocess.CompletedProcess(command, 0, b"", b"")

    monkeypatch.setattr(os, "killpg", forbidden, raising=False)
    monkeypatch.setattr(subprocess, "run", run)
    for stop in (worker_operations._stop_tree, kubernetes_module._stop):
        process = Process()
        stop(cast(subprocess.Popen[bytes], process))
        assert process.kills == 1
    assert commands == []
    with pytest.raises(RuntimeError, match="POSIX runtime"):
        worker_operations._signal_group(Process.pid, 9)
