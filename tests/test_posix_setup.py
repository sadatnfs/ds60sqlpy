"""Exercise bootstrap decisions without package downloads or user-level writes."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "setup.sh"
SHELL = shutil.which("sh")
pytestmark = pytest.mark.skipif(os.name == "nt" or SHELL is None, reason="POSIX shell required")

# The fake executable logs external commands and emulates only creating a
# virtual environment. No pip, uv, Jupyter, doctor, registry, or network runs.
FAKE_PYTHON = """#!/bin/sh
printf 'python:%s\\n' "$*" >> "$DS60_SETUP_TEST_LOG"
if [ "$1" = "-c" ]; then exit "${DS60_SETUP_TEST_PROBE_STATUS:-0}"; fi
if [ "$1" = "-m" ] && [ "$2" = "venv" ]; then
  /bin/mkdir -p "$3/bin"
  /bin/cp "$0" "$3/bin/python"
fi
if [ "$1" = "-m" ] && [ "$2" = "pip" ]; then
  exit "${DS60_SETUP_TEST_INSTALL_STATUS:-0}"
fi
"""


def executable(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


@pytest.fixture
def sandbox(tmp_path: Path) -> tuple[Path, Path, dict[str, str]]:
    repo = tmp_path / "course with spaces"
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)
    shutil.copyfile(SCRIPT, scripts / "setup.sh")
    tools = tmp_path / "tools"
    tools.mkdir()
    # Include only explicitly controlled tools, even if the host has uv or a
    # newer unsupported Python. dirname remains available for script discovery.
    executable(tools / "python3.12", FAKE_PYTHON)
    dirname = shutil.which("dirname")
    assert dirname is not None
    (tools / "dirname").symlink_to(dirname)
    log = tmp_path / "calls.log"
    env = {
        **os.environ,
        "PATH": str(tools),
        "DS60_SETUP_TEST_LOG": str(log),
        "UV_PROJECT_ENVIRONMENT": str(tmp_path / "unrelated environment"),
        "UV_PYTHON": "3.99",
    }
    return repo, log, env


def run_setup(
    sandbox: tuple[Path, Path, dict[str, str]], *args: str
) -> subprocess.CompletedProcess[str]:
    repo, _, env = sandbox
    return subprocess.run(
        [SHELL or "sh", str(repo / "scripts" / "setup.sh"), *args],
        cwd=repo.parent,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )


def test_project_bootstrap_is_path_safe_and_installs_shared_core(
    sandbox: tuple[Path, Path, dict[str, str]],
) -> None:
    repo, log, _ = sandbox
    result = run_setup(sandbox, "--dependency-mode", "project")
    assert result.returncode == 0, result.stderr
    calls = log.read_text(encoding="utf-8")
    assert f"-m venv {repo}/.venv" in calls
    assert ".[notebooks,data,quality,bridge,professional,sql-notebooks]" in calls
    assert "-m ipykernel install --user --name ds60sqlpy" in calls
    assert "scripts/course.py doctor --no-database" in calls
    assert "No database was contacted or modified" in result.stdout


def test_rerun_reuses_existing_environment_without_creating_it_again(
    sandbox: tuple[Path, Path, dict[str, str]],
) -> None:
    repo, log, env = sandbox
    executable(repo / ".venv" / "bin" / "python", FAKE_PYTHON)
    # No supported base interpreter is needed once .venv is ready.
    (Path(env["PATH"]) / "python3.12").unlink()
    result = run_setup(sandbox)
    assert result.returncode == 0, result.stderr
    assert "Reusing " in result.stdout
    assert "-m venv" not in log.read_text(encoding="utf-8")


@pytest.mark.parametrize("broken_interpreter", [False, True])
def test_incomplete_or_unsupported_environment_is_preserved(
    sandbox: tuple[Path, Path, dict[str, str]], broken_interpreter: bool
) -> None:
    repo, log, env = sandbox
    state = repo / ".venv" / "my-notes.txt"
    state.parent.mkdir()
    state.write_text("keep this", encoding="utf-8")
    if broken_interpreter:
        executable(repo / ".venv" / "bin" / "python", FAKE_PYTHON)
        env["DS60_SETUP_TEST_PROBE_STATUS"] = "1"
    result = run_setup(sandbox)
    assert result.returncode != 0
    assert "not deleted automatically" in result.stderr
    assert state.read_text(encoding="utf-8") == "keep this"
    assert "-m pip" not in (log.read_text(encoding="utf-8") if log.exists() else "")


def test_locked_mode_never_silently_falls_back_or_creates_environment(
    sandbox: tuple[Path, Path, dict[str, str]],
) -> None:
    repo, _, _ = sandbox
    result = run_setup(sandbox, "--dependency-mode", "locked")
    assert result.returncode != 0
    assert "Locked mode requires uv" in result.stderr
    assert not (repo / ".venv").exists()


def test_auto_locked_mode_targets_repository_and_preserves_declared_profile(
    sandbox: tuple[Path, Path, dict[str, str]],
) -> None:
    repo, log, env = sandbox
    executable(
        Path(env["PATH"]) / "uv",
        '#!/bin/sh\nprintf "uv:%s|environment:%s|python:%s\\n" '
        '"$*" "$UV_PROJECT_ENVIRONMENT" "$UV_PYTHON" >> "$DS60_SETUP_TEST_LOG"\n',
    )
    result = run_setup(sandbox, "--advanced")
    assert result.returncode == 0, result.stderr
    calls = log.read_text(encoding="utf-8")
    assert f"uv:sync --locked --python {repo}/.venv/bin/python" in calls
    assert f"|environment:{repo}/.venv|python:{repo}/.venv/bin/python" in calls
    for extra in ("bridge", "professional", "sql-notebooks", "ml", "nlp", "geo"):
        assert f"--extra {extra}" in calls
    assert "-m pip" not in calls


def test_failed_install_stops_before_registering_kernel(
    sandbox: tuple[Path, Path, dict[str, str]],
) -> None:
    _, log, env = sandbox
    env["DS60_SETUP_TEST_INSTALL_STATUS"] = "19"
    result = run_setup(sandbox, "--dependency-mode", "project")
    assert result.returncode == 19
    assert "-m ipykernel" not in log.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "args",
    [
        ("--unknown",),
        ("--dependency-mode",),
        ("--advanced", "unexpected"),
        ("--dependency-mode", "typo"),
    ],
)
def test_bad_arguments_fail_before_environment_writes(
    sandbox: tuple[Path, Path, dict[str, str]], args: tuple[str, ...]
) -> None:
    repo, _, _ = sandbox
    result = run_setup(sandbox, *args)
    assert result.returncode == 2
    assert "Usage:" in result.stderr
    assert not (repo / ".venv").exists()
