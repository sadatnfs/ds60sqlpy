"""Fake local engine checks for explicit optional Kubernetes launcher preparation."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

pytestmark = pytest.mark.skipif(
    os.name == "nt",
    reason="POSIX executable fake harness; native Windows launcher acceptance is separate.",
)

ROOT = Path(__file__).resolve().parents[1]


def fixture_environment(tmp_path: Path) -> tuple[dict[str, str], Path, Path]:
    binary = tmp_path / "bin"
    binary.mkdir()
    log = tmp_path / "commands.jsonl"
    common = """import json, os, sys
from pathlib import Path
with Path(os.environ['FAKE_LOG']).open('a') as out:
    out.write(json.dumps({'args':sys.argv[1:],'tool':Path(sys.argv[0]).name,
        'k8s':os.environ.get('DS60_K8S_SESSION_DIR'),
        'host':os.environ.get('DOCKER_HOST'), 'context':os.environ.get('DOCKER_CONTEXT'),
        'endpoints':os.environ.get('DS60_MODULE_ENDPOINTS')})+'\\n')
"""
    docker = binary / "docker"
    docker.write_text(
        "#!"
        + sys.executable
        + "\n"
        + common
        + """
args=sys.argv[1:]
if args[:2]==['context','inspect']: print('unix:///fake/local.sock')
elif args[:1]==['info'] and '{{.OSType}}' in args: print('linux')
elif args[:1]==['info'] and '{{json .SecurityOptions}}' in args: print('[]')
elif args[:1]==['run']:
    print('Filesystem 1024-blocks Used Available Capacity Mounted')
    print('fixture 90000000 1000 80000000 1% /')
"""
    )
    inspector = binary / "host-python"
    inspector.write_text(
        "#!"
        + sys.executable
        + "\n"
        + common
        + """
assert sys.argv[2]=='inspect'
sys.exit(2 if os.environ.get('FAIL_INSPECT') else 0)
"""
    )
    df = binary / "df"
    df.write_text(
        "#!/bin/sh\nprintf 'Filesystem 1024-blocks Used Available Capacity Mounted\\n"
        "fixture 90000000 1000 80000000 1%% /\\n'\n"
    )
    for item in (docker, inspector, df):
        item.chmod(0o755)
    environment = dict(os.environ)
    for key in ("DOCKER_HOST", "DOCKER_CONTEXT", "DS60_MODULE_PROFILES", "DS60_PYTHON_IMAGE"):
        environment.pop(key, None)
    environment.update(
        PATH=str(binary) + os.pathsep + os.environ.get("PATH", ""),
        FAKE_LOG=str(log),
        DS60_MODULE_RUNTIME_DIR=str(tmp_path / "private"),
        DS60_LEARNING_DIR=str(tmp_path / "learning"),
        DS60_MODULE_PROJECT="fake-modules",
        POWERSHELL_TELEMETRY_OPTOUT="1",
    )
    return environment, log, inspector


def records(log: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


def invoke(
    engine: str, action: str, env: dict[str, str], inspector: Path, session: Path | None
) -> subprocess.CompletedProcess[str]:
    if engine == "bash":
        command = [
            "bash",
            str(ROOT / "scripts/module_lab.sh"),
            action,
            "--profiles",
            "k8s-kind",
            "--python",
            str(inspector),
            "--no-browser",
        ]
        if session is not None:
            command += ["--k8s-session", str(session)]
    else:
        runtime = os.environ.get("DS60_PWSH") or shutil.which("pwsh")
        if not runtime:
            pytest.skip("Private PowerShell runtime not selected.")
        command = [
            runtime,
            "-NoProfile",
            "-File",
            str(ROOT / "scripts/module_lab.ps1"),
            action,
            "-Profiles",
            "k8s-kind",
            "-Python",
            str(inspector),
            "-NoBrowser",
        ]
        if session is not None:
            command += ["-K8sSession", str(session)]
    return subprocess.run(
        command, env=env, cwd=ROOT, capture_output=True, text=True, timeout=30, check=False
    )


@pytest.mark.parametrize("engine", ["bash", "powershell"])
@pytest.mark.parametrize("case", ["missing", "rejected", "ready", "status", "stop"])
def test_kubernetes_start_requires_explicit_lease_but_stop_does_not_release(
    tmp_path: Path, engine: str, case: str
) -> None:
    env, log, inspector = fixture_environment(tmp_path)
    session = None if case == "missing" else tmp_path / "private-k8s"
    if case == "rejected":
        env["FAIL_INSPECT"] = "1"
    action = case if case in ("status", "stop") else "start"
    result = invoke(engine, action, env, inspector, session)
    commands = records(log)
    mutations = [item for item in commands if "up" in item["args"]]
    if case in ("missing", "rejected"):
        assert result.returncode != 0
        assert not mutations
        assert not (tmp_path / "private").exists()
        assert not (tmp_path / "learning").exists()
    else:
        assert result.returncode == 0, result.stdout + result.stderr
        compose = [
            item for item in commands if item["args"][:1] == ["compose"] and "-f" in item["args"]
        ]
        assert compose and all(
            str(ROOT / "compose.kubernetes.yaml") in item["args"] for item in compose
        )
        assert all(item["k8s"] == str(session) for item in compose)
        assert all(
            item["host"] == "unix:///fake/local.sock" and not item["context"] for item in compose
        )
        assert json.loads(compose[-1]["endpoints"])["k8s-kind"] == "http://kubernetes-worker:8081"
        assert bool(mutations) == (case == "ready")
        assert not any("prepare" in item["args"] or "release" in item["args"] for item in commands)
        if case in ("status", "stop"):
            assert not any(item["tool"] == "host-python" for item in commands)
            assert not (tmp_path / "private").exists()


def test_bash_build_prepares_fixture_without_a_cluster_or_lease(tmp_path: Path) -> None:
    env, log, inspector = fixture_environment(tmp_path)
    result = invoke("bash", "build", env, inspector, None)
    assert result.returncode == 0, result.stdout + result.stderr
    commands = records(log)
    fixture = [item for item in commands if item["args"][:1] == ["build"]]
    assert len(fixture) == 1 and "ds60sqlpy-k8s-fixture:0.2.0" in fixture[0]["args"]
    assert not any(item["tool"] == "host-python" for item in commands)
    assert not any("create" in item["args"] or "release" in item["args"] for item in commands)


def test_bash_remote_context_is_refused_before_daemon_probe(tmp_path: Path) -> None:
    env, log, inspector = fixture_environment(tmp_path)
    env["DOCKER_HOST"] = "tcp://unrelated.example:2376"
    result = invoke("bash", "start", env, inspector, tmp_path / "private-k8s")
    assert result.returncode != 0
    assert not records(log)


def test_bash_private_runtime_parent_cannot_link_into_progress(tmp_path: Path) -> None:
    env, log, _ = fixture_environment(tmp_path)
    portable = tmp_path / ".learning"
    portable.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(portable, target_is_directory=True)
    env["DS60_MODULE_RUNTIME_DIR"] = str(alias / "private")
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/module_lab.sh"),
            "start",
            "--profiles",
            "python-core",
            "--no-browser",
        ],
        env=env,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode != 0
    assert list(portable.iterdir()) == []
    assert not any("up" in item["args"] for item in records(log))
