"""Failure and cleanup behavior for the explicitly invoked R reference checker."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "r_reference_checker", ROOT / "courses/r/authoring/check_references.py"
)
assert spec and spec.loader
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def test_zero_exit_without_reference_marker_is_not_a_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="unrelated output", stderr="")

    monkeypatch.setattr(checker.subprocess, "run", fake_run)
    result = checker.run_program(
        {"lesson": "r-001", "kind": "reference", "source": "print(1)\n"}, "sha256:fixture", 5
    )
    assert not result["passed"] and result["exit_code"] == 0
    run, cleanup = calls
    name = run[run.index("--name") + 1]
    assert name.startswith("ds60-r-reference-")
    assert cleanup == ["docker", "rm", "--force", name]
    assert run[run.index("--network") + 1] == "none"
    assert run[run.index("--pull") + 1] == "never"
    assert "--read-only" in run and "--mount" not in run and "-v" not in run


def test_timeout_removes_only_the_container_owned_by_that_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if command[1] == "run":
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(checker.subprocess, "run", fake_run)
    result = checker.run_program(
        {"lesson": "r-001", "kind": "example-1", "source": "repeat {}\n"}, "sha256:fixture", 1
    )
    assert result["timed_out"] and not result["passed"]
    assert result["exit_code"] is None
    name = calls[0][calls[0].index("--name") + 1]
    assert calls[1] == ["docker", "rm", "--force", name]
    assert len(calls) == 2


def test_reference_hash_binds_the_exact_submitted_source(monkeypatch: pytest.MonkeyPatch) -> None:
    import hashlib

    source = 'cat("r-001 reference checks passed\\n")\n'

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if command[1] == "run":
            assert kwargs["input"] == source
        return subprocess.CompletedProcess(
            command, 0, stdout="r-001 reference checks passed\n", stderr=""
        )

    monkeypatch.setattr(checker.subprocess, "run", fake_run)
    result = checker.run_program(
        {"lesson": "r-001", "kind": "reference", "source": source}, "sha256:fixture", 5
    )
    assert result["passed"]
    assert result["source_sha256"] == hashlib.sha256(source.encode()).hexdigest()
