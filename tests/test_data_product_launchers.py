"""First-start serialization and scope guards without a real Docker daemon."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "courses/data-ml-engineering/projects/data-product/run.sh"


@pytest.fixture
def launcher(tmp_path: Path) -> dict[str, Any]:
    project = tmp_path / "owned project"
    project.mkdir()
    shutil.copyfile(SCRIPT, project / "run.sh")
    binaries = tmp_path / "bin"
    binaries.mkdir()
    log = tmp_path / "calls.jsonl"
    fake = binaries / "docker"
    fake.write_text(
        f"#!{sys.executable}\n"
        + """import json,os,sys,time
from pathlib import Path
a=sys.argv[1:]
with Path(os.environ['PRODUCT_TEST_LOG']).open('a') as f:f.write(json.dumps(a)+'\\n')
scenario=os.environ.get('PRODUCT_TEST_SCENARIO','')
if a[:2]==['context','inspect']:
    print('ssh://remote.invalid' if os.environ.get('DOCKER_CONTEXT')=='remote-test' else 'unix:///local.sock')
elif a[:1]==['info']:print('linux|aarch64')
elif a[:2]==['image','inspect']:
    print('sha256:'+'a'*64+'|linux|arm64' if '.Id' in a[a.index('--format')+1] else 'linux|arm64')
elif a[:1]==['ps']:
    if scenario=='listing-failure':sys.exit(9)
elif a[:2]==['network','ls']:
    if scenario=='foreign-network':print('network-one')
elif a[:2]==['network','inspect']:print('different-workshop|different-owner')
elif a[:1]==['run']:
    joined=' '.join(a)
    if 'secrets.token_hex' in joined:
        time.sleep(0.4);print('b'*32)
    elif 'os.stat' in joined:print('1000:1000')
    else:print('library initialization passed')
elif a[:1]==['compose']:pass
else:sys.exit(8)
"""
    )
    fake.chmod(0o755)
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("DOCKER_", "DS60_PRODUCT_"))
    }
    environment.update(
        PATH=str(binaries) + os.pathsep + os.environ.get("PATH", os.defpath),
        PRODUCT_TEST_LOG=str(log),
    )
    return {"root": project, "env": environment, "log": log}


def invoke(
    launcher: dict[str, Any], *args: str, scenario: str = "", extra: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/bin/bash", "run.sh", *args],
        cwd=launcher["root"],
        env={**launcher["env"], "PRODUCT_TEST_SCENARIO": scenario, **(extra or {})},
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )


def saved(launcher: dict[str, Any]) -> Path:
    root: Path = launcher["root"] / ".workshop"
    for name in ("raw", "published", "control", "private"):
        (root / name).mkdir(parents=True)
    settings = root / "settings.env"
    settings.write_text(
        "\n".join(
            [
                "DS60_PRODUCT_CONFIG_VERSION=1",
                "DS60_PRODUCT_OWNER=" + "b" * 32,
                "DS60_PRODUCT_PROJECT=ds60-data-product-" + "b" * 12,
                "DS60_PRODUCT_IMAGE_REF=ds60sqlpy-worker-data-engineering:1.0.0",
                "DS60_PRODUCT_IMAGE_ID=sha256:" + "a" * 64,
                "DS60_PRODUCT_ARCH=arm64",
                "DS60_PRODUCT_PORT=18894",
                "DS60_PRODUCT_UID=1000",
                "DS60_PRODUCT_GID=1000",
                "",
            ]
        )
    )
    return settings


def calls(launcher: dict[str, Any]) -> list[list[str]]:
    return (
        [json.loads(line) for line in launcher["log"].read_text().splitlines()]
        if launcher["log"].exists()
        else []
    )


@pytest.mark.parametrize("action", ["start", "stop", "resume", "replace", "down"])
def test_extra_lifecycle_arguments_fail_before_docker_or_state(
    action: str, launcher: dict[str, Any]
) -> None:
    result = invoke(launcher, action, "--unknown")
    assert result.returncode == 2 and not calls(launcher)
    assert not (launcher["root"] / ".workshop").exists()


def test_explicit_context_overrides_an_ambient_local_host(launcher: dict[str, Any]) -> None:
    result = invoke(
        launcher,
        "start",
        extra={"DOCKER_CONTEXT": "remote-test", "DOCKER_HOST": "unix:///claimed-local.sock"},
    )
    assert result.returncode == 2
    assert calls(launcher)[0][:2] == ["context", "inspect"]
    assert "remote-test" in calls(launcher)[0]
    assert not any(call[0] in {"info", "run", "compose"} for call in calls(launcher))
    assert not (launcher["root"] / ".workshop").exists()


@pytest.mark.parametrize("scenario", ["foreign-network", "listing-failure"])
def test_uncertain_resource_ownership_prevents_compose_mutation(
    scenario: str, launcher: dict[str, Any]
) -> None:
    saved(launcher)
    result = invoke(launcher, "down", scenario=scenario)
    assert result.returncode == 2
    assert not any(call[0] == "compose" for call in calls(launcher))


def test_port_reconfiguration_obeys_the_existing_action_lock(launcher: dict[str, Any]) -> None:
    settings = saved(launcher)
    old = settings.read_bytes()
    lock = settings.parent / "action.lock"
    lock.mkdir()
    (lock / "pid").write_text("999999\n")
    result = invoke(launcher, "configure-port", "18899")
    assert result.returncode == 2 and settings.read_bytes() == old


def test_two_first_starts_cannot_replace_the_selected_owner(launcher: dict[str, Any]) -> None:
    first = subprocess.Popen(
        ["/bin/bash", "run.sh", "start"],
        cwd=launcher["root"],
        env=launcher["env"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 5
        while not (launcher["root"] / ".workshop/action.lock/pid").exists():
            if time.monotonic() >= deadline or first.poll() is not None:
                raise AssertionError("First start did not acquire its initialization lock")
            time.sleep(0.01)
        second = invoke(launcher, "start")
        stdout, stderr = first.communicate(timeout=10)
        assert first.returncode == 0, (stdout, stderr)
        assert second.returncode == 2 and "lock" in second.stderr
        generation = [
            call
            for call in calls(launcher)
            if call[0] == "run" and "secrets.token_hex" in " ".join(call)
        ]
        assert len(generation) == 1
        assert (
            "DS60_PRODUCT_OWNER=" + "b" * 32
            in (launcher["root"] / ".workshop/settings.env").read_text()
        )
    finally:
        if first.poll() is None:
            first.kill()
            first.communicate()
