from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import TypedDict, cast

import pytest

from scripts import docker_lab


@pytest.fixture
def fake_engine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    commands = tmp_path / "commands"
    commands.mkdir()
    log = tmp_path / "docker-calls.jsonl"
    docker = commands / "docker"
    docker.write_text(
        "#!"
        + sys.executable
        + "\n"
        + """
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with Path(os.environ['DS60_LAUNCH_TEST_LOG']).open('a') as f:
    f.write(json.dumps({'args': args, 'state': os.environ.get('DS60_LEARNING_DIR'),
        'uid': os.environ.get('DS60_UID'), 'rootless': os.environ.get('DS60_ROOTLESS'),
        'context': os.environ.get('DOCKER_CONTEXT'), 'host': os.environ.get('DOCKER_HOST')})+'\\n')
if args[:2] == ['context', 'inspect']: print('unix:///test/docker.sock')
elif args[:1] == ['info']:
    security = ['name=rootless'] if os.environ.get('TEST_ROOTLESS') else []
    info = {'OSType':'linux', 'SecurityOptions':security}
    value = args[-1]
    if 'OSType' in value: print('linux')
    elif 'SecurityOptions' in value: print(json.dumps(info['SecurityOptions']))
    else: print(json.dumps(info))
elif args[:2] == ['image', 'inspect']:
    if os.environ.get('TEST_IMAGE_MISSING'): sys.exit(1)
    print('sha256:local')
elif 'version' in args: print('Docker Compose version v2.30.0')
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)
    if os.name == "nt":
        fake_script = commands / "fake_docker.py"
        docker.rename(fake_script)
        docker = commands / "docker.cmd"
        docker.write_text(f'@echo off\n"{sys.executable}" "{fake_script}" %*\n', encoding="utf-8")
    curl = commands / "curl"
    curl.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    curl.chmod(0o755)
    monkeypatch.setenv("PATH", str(commands) + os.pathsep + os.environ.get("PATH", ""))
    monkeypatch.setenv("DS60_LAUNCH_TEST_LOG", str(log))
    monkeypatch.delenv("DOCKER_HOST", raising=False)
    monkeypatch.delenv("DOCKER_CONTEXT", raising=False)
    monkeypatch.setattr(docker_lab, "ROOT", tmp_path / "course with spaces")
    return docker, log


class EngineCall(TypedDict):
    args: list[str]
    state: str | None
    uid: str | None
    rootless: str | None
    context: str | None
    host: str | None


def calls(path: Path) -> list[EngineCall]:
    return [cast(EngineCall, json.loads(line)) for line in path.read_text().splitlines()]


def test_doctor_does_not_create_or_change_progress(
    fake_engine: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    data = tmp_path / "not-created"
    assert docker_lab.main(["doctor", "--data-dir", str(data)]) == 0
    assert not data.exists()
    assert not any(
        "up" in item["args"] or "build" in item["args"] for item in calls(fake_engine[1])
    )


def test_start_preserves_host_progress_builds_locally_and_opens_browser(
    fake_engine: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = tmp_path / "my course state"
    data.mkdir()
    evidence = data / "progress.json"
    evidence.write_bytes(b"previous learner evidence")
    monkeypatch.setenv("TEST_IMAGE_MISSING", "1")
    opened: list[str] = []
    monkeypatch.setattr(docker_lab, "wait_for_lab", lambda url: None)
    monkeypatch.setattr(docker_lab, "open_browser", opened.append)
    assert docker_lab.main(["start", "--data-dir", str(data), "--port", "18888"]) == 0
    recorded = calls(fake_engine[1])
    assert any("build" in entry["args"] for entry in recorded)
    assert any("up" in entry["args"] and "--wait" in entry["args"] for entry in recorded)
    assert not any("push" in entry["args"] for entry in recorded)
    assert opened == ["http://127.0.0.1:18888/learn"]
    assert evidence.read_bytes() == b"previous learner evidence"
    assert next(entry for entry in recorded if "up" in entry["args"])["state"] == str(data)


def test_rootless_uses_mapped_identity_and_stop_keeps_files(
    fake_engine: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = tmp_path / "state"
    data.mkdir()
    (data / "pad.py").write_text("print(42)", encoding="utf-8")
    monkeypatch.setenv("TEST_ROOTLESS", "1")
    assert docker_lab.main(["stop", "--data-dir", str(data)]) == 0
    stop = next(item for item in calls(fake_engine[1]) if "stop" in item["args"])
    assert stop["uid"] == "0" and stop["rootless"] == "1"
    assert (data / "pad.py").read_text() == "print(42)"
    assert not any("down" in item["args"] for item in calls(fake_engine[1]))


def test_remote_engine_is_rejected_before_contact(
    fake_engine: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DOCKER_HOST", "ssh://remote.example")
    assert docker_lab.main(["doctor", "--data-dir", str(tmp_path / "none")]) == 2
    assert not fake_engine[1].exists()


@pytest.mark.parametrize(
    "endpoint",
    [
        # secret-scan: allow-fixture
        "tcp://localhost:2375@remote.example",
        # secret-scan: allow-fixture
        "tcp://127.0.0.1:2375@remote.example",
        "tcp://localhost:2375/remote",
        "unix://remote.example/socket",
    ],
)
@pytest.mark.parametrize(
    "launcher",
    [
        "python",
        pytest.param("bash", marks=pytest.mark.skipif(os.name == "nt", reason="POSIX shell")),
    ],
)
def test_misleading_local_prefix_cannot_contact_a_remote_engine(
    fake_engine: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch, endpoint: str, launcher: str
) -> None:
    monkeypatch.setenv("DOCKER_HOST", endpoint)
    if launcher == "python":
        assert docker_lab.main(["doctor"]) == 2
    else:
        script = Path(__file__).resolve().parents[1] / "scripts/docker_lab.sh"
        result = subprocess.run(["bash", str(script), "doctor"], capture_output=True, check=False)
        assert result.returncode == 2
    assert not fake_engine[1].exists()


@pytest.mark.parametrize(
    "launcher",
    [
        "python",
        pytest.param("bash", marks=pytest.mark.skipif(os.name == "nt", reason="POSIX shell")),
    ],
)
def test_explicit_local_host_cannot_be_overridden_by_remote_context(
    fake_engine: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    launcher: str,
) -> None:
    monkeypatch.setenv("DOCKER_HOST", "unix:///test/docker.sock")
    monkeypatch.setenv("DOCKER_CONTEXT", "remote-context")
    data = tmp_path / "state"
    if launcher == "python":
        assert docker_lab.main(["status", "--data-dir", str(data)]) == 0
    else:
        source = Path(__file__).resolve().parents[1] / "scripts/docker_lab.sh"
        result = subprocess.run(
            ["bash", str(source), "status", "--data-dir", str(data)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
    recorded = calls(fake_engine[1])
    assert recorded
    assert all(item["host"] == "unix:///test/docker.sock" for item in recorded)
    assert all(item["context"] is None for item in recorded)
    assert not data.exists()


@pytest.mark.skipif(os.name == "nt", reason="POSIX shell; PowerShell is tested separately")
def test_bash_launcher_preserves_progress_and_passes_safe_paths(
    fake_engine: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    source = Path(__file__).resolve().parents[1] / "scripts/docker_lab.sh"
    data = tmp_path / "state with spaces"
    data.mkdir()
    (data / "progress.json").write_bytes(b"keep this")
    completed = subprocess.run(
        ["bash", str(source), "start", "--data-dir", str(data), "--no-browser"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert (data / "progress.json").read_bytes() == b"keep this"
    up = next(item for item in calls(fake_engine[1]) if "up" in item["args"])
    assert up["state"] == str(data)
    assert "--wait" in up["args"]
