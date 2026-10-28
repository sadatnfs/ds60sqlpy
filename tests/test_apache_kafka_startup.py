"""Kafka startup argv and owned failure diagnostics without a Docker engine."""

from __future__ import annotations

import os
import runpy
import shlex
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "courses/apache-data-platforms/projects/streaming"
QUALIFIER = ROOT / "courses/apache-data-platforms/authoring/qualify_workshop.py"


@pytest.fixture
def broker(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    """Run the maintained Bash logic with only its fixed filesystem paths replaced."""
    data = tmp_path / "data"
    data.mkdir()
    tools = tmp_path / "tools"
    tools.mkdir()
    config = tmp_path / "server.properties"
    config.write_text("fixture configuration\n")
    calls = tmp_path / "calls"
    calls.mkdir()
    for name, label in [("kafka-storage.sh", "storage"), ("kafka-server-start.sh", "server")]:
        tool = tools / name
        tool.write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\n"
            f'printf "%s\\0" "$@" > "$KAFKA_CALL_DIR/{label}.argv"\n'
        )
        tool.chmod(0o755)
    script = tmp_path / "start-broker.sh"
    source = (PROJECT / "start-broker.sh").read_text()
    source = source.replace("data=/var/lib/kafka/data", "data=" + shlex.quote(str(data)))
    source = source.replace("/project/server.properties", shlex.quote(str(config)))
    for name in ["kafka-storage.sh", "kafka-server-start.sh"]:
        source = source.replace("/opt/kafka/bin/" + name, shlex.quote(str(tools / name)))
    script.write_text(source)
    return script, data, config, calls


def run_broker(
    broker: tuple[Path, Path, Path, Path], cluster: str
) -> subprocess.CompletedProcess[str]:
    script, _, _, calls = broker
    return subprocess.run(
        ["bash", str(script)],
        env=os.environ | {"CLUSTER_ID": cluster, "KAFKA_CALL_DIR": str(calls)},
        capture_output=True,
        text=True,
        timeout=5,
    )


def argv(path: Path) -> list[str]:
    return [value.decode() for value in path.read_bytes().split(b"\0")[:-1]]


@pytest.mark.parametrize("cluster", ["A" * 22, "-" + "A" * 21, "_" + "A" * 21, "--" + "A" * 20])
def test_new_broker_binds_every_valid_cluster_identity_as_one_option_value(
    broker: tuple[Path, Path, Path, Path], cluster: str
) -> None:
    result = run_broker(broker, cluster)
    _, _, config, calls = broker
    assert result.returncode == 0, result.stderr
    assert argv(calls / "storage.argv") == [
        "format",
        "--cluster-id=" + cluster,
        "--config",
        str(config),
    ]
    assert argv(calls / "server.argv") == [str(config)]


@pytest.mark.parametrize("cluster", ["", "A" * 21, "A" * 23, "!" + "A" * 21, "A" * 21 + "\n"])
def test_invalid_cluster_identity_stops_before_any_kafka_tool(
    broker: tuple[Path, Path, Path, Path], cluster: str
) -> None:
    result = run_broker(broker, cluster)
    assert result.returncode == 2
    assert "Invalid owned cluster identity" in result.stderr
    assert not list(broker[3].iterdir())


def test_dirty_unformatted_data_is_preserved_without_start_or_format(
    broker: tuple[Path, Path, Path, Path],
) -> None:
    retained = broker[1] / "retained-record"
    retained.write_bytes(b"retained fixture data")
    result = run_broker(broker, "A" * 22)
    assert result.returncode == 2
    assert "Refusing to reformat" in result.stderr
    assert retained.read_bytes() == b"retained fixture data"
    assert not list(broker[3].iterdir())


def test_persisted_mismatched_identity_is_preserved_without_start_or_format(
    broker: tuple[Path, Path, Path, Path],
) -> None:
    metadata = broker[1] / "meta.properties"
    original = "cluster.id=" + "B" * 22 + "\nnode.id=1\n"
    metadata.write_text(original)
    result = run_broker(broker, "A" * 22)
    assert result.returncode == 2
    assert "Persisted Kafka cluster identity mismatch" in result.stderr
    assert metadata.read_text() == original
    assert not list(broker[3].iterdir())


def test_persisted_matching_identity_starts_without_formatting(
    broker: tuple[Path, Path, Path, Path],
) -> None:
    cluster = "-" + "A" * 21
    metadata = broker[1] / "meta.properties"
    original = "cluster.id=" + cluster + "\nnode.id=1\n"
    metadata.write_text(original)
    result = run_broker(broker, cluster)
    assert result.returncode == 0, result.stderr
    assert metadata.read_text() == original
    assert not (broker[3] / "storage.argv").exists()
    assert argv(broker[3] / "server.argv") == [str(broker[2])]


@pytest.fixture
def qualifier(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Callable[..., dict[str, Any]], Path]:
    namespace = runpy.run_path(str(QUALIFIER))
    qualify = namespace["qualify"]
    base = tmp_path / "source"
    source = base / "projects/streaming"
    source.mkdir(parents=True)
    (source / "run.sh").write_text("# Synthetic launcher; command is intercepted.\n")
    monkeypatch.setitem(qualify.__globals__, "BASE", base)
    return qualify, tmp_path / "copied-workshop"


@pytest.mark.parametrize("logs_fail", [False, True])
def test_failed_start_retains_bounded_safe_diagnostics_before_guarded_cleanup(
    qualifier: tuple[Callable[..., dict[str, Any]], Path],
    monkeypatch: pytest.MonkeyPatch,
    logs_fail: bool,
) -> None:
    qualify, workspace = qualifier
    calls: list[list[str]] = []
    unsafe = (
        # secret-scan: allow-fixture
        "https://fixture-user:temporary-secret@example.test/log?signature=temporary-token#fragment"
    )

    def command(arguments: list[str], directory: Path, **kwargs: Any) -> str:
        assert directory == workspace
        calls.append(arguments)
        if arguments[1:3] == ["info", "--format"]:
            return "linux/arm64"
        assert arguments[:2] == ["bash", "run.sh"]
        if arguments[2:] == ["start", "--binary"]:
            (workspace / ".env").write_text("synthetic owned identity\n")
            raise RuntimeError("Original startup failure")
        if arguments[2:] == ["logs"]:
            diagnostic = "x" * 7000 + "\n" + unsafe
            if logs_fail:
                raise RuntimeError(diagnostic)
            return diagnostic
        assert arguments[2:] == ["destroy", "--confirm-owned-data-loss"]
        return "Owned cleanup complete"

    monkeypatch.setitem(qualify.__globals__, "command", command)
    report = qualify("streaming", workspace, prepare=False, require_ipc=False)
    assert report["passed"] is False and report["cleanup"] is True
    assert report["error"] == "Original startup failure"
    assert [call[2:] for call in calls[1:]] == [
        ["start", "--binary"],
        ["logs"],
        ["destroy", "--confirm-owned-data-loss"],
    ]
    field = "failure_logs_error" if logs_fail else "failure_logs"
    diagnostic = report[field]
    assert len(diagnostic) <= 6000
    assert "https://example.test/log" in diagnostic
    assert "temporary-secret" not in diagnostic and "temporary-token" not in diagnostic
    assert "fixture-user" not in diagnostic and "fragment" not in diagnostic
    for path in workspace.glob("*.log"):
        saved = path.read_text()
        assert "temporary-secret" not in saved and "temporary-token" not in saved


def test_failed_start_without_owned_identity_does_not_request_logs_or_destroy(
    qualifier: tuple[Callable[..., dict[str, Any]], Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    qualify, workspace = qualifier
    calls: list[list[str]] = []

    def command(arguments: list[str], directory: Path, **kwargs: Any) -> str:
        assert directory == workspace
        calls.append(arguments)
        if arguments[1:3] == ["info", "--format"]:
            return "linux/arm64"
        assert arguments == ["bash", "run.sh", "start", "--binary"]
        raise RuntimeError("Start failed before owned identity")

    monkeypatch.setitem(qualify.__globals__, "command", command)
    report = qualify("streaming", workspace, prepare=False, require_ipc=False)
    assert report["passed"] is False and report["cleanup"] is True
    assert report["error"] == "Start failed before owned identity"
    assert "failure_logs" not in report and "failure_logs_error" not in report
    assert len(calls) == 2
