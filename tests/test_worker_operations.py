"""Value-based adapters and real bounded processes without image downloads."""

from __future__ import annotations

import json
import os
import shutil
import sys
import threading
import time
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.worker_operations import (
    MAX_OUTPUT_BYTES,
    BoundedOutput,
    child_environment,
    execute_operation,
    run_process,
    validate_operation,
    verify_python_namespace,
)

ROOT = Path(__file__).resolve().parents[1]


def execute(
    tmp_path: Path, source: str, *, profile: str = "python-core", verification: str | None = None
) -> Any:
    return execute_operation(
        profile, source, tmp_path, 15, threading.Event(), lambda _: None, verification
    )


def test_real_python_exit_errors_and_no_fabricated_checks(tmp_path: Path) -> None:
    result = execute(tmp_path / "ok", "print(42)\n")
    assert result.status == "succeeded" and result.returncode == 0 and result.output == "42\n"
    assert result.checks == []
    failure = execute(tmp_path / "bad", "raise ValueError('fixture-error')\n")
    assert failure.status == "failed" and failure.returncode == 1
    assert "ValueError: fixture-error" in failure.output and "main.py" in failure.output
    explicit = execute(tmp_path / "exit", "raise SystemExit(7)\n")
    assert explicit.status == "failed" and explicit.returncode == 7


def test_output_head_tail_drains_without_hiding_exit(tmp_path: Path) -> None:
    source = (
        "import sys\nprint('HEAD')\nprint('x'*200000)\nprint('TAIL',file=sys.stderr)\nsys.exit(7)\n"
    )
    result = execute(tmp_path, source)
    assert result.truncated and len(result.output.encode()) <= MAX_OUTPUT_BYTES
    assert "HEAD" in result.output and "TAIL" in result.output
    assert result.status == "failed" and result.returncode == 7
    invalid = BoundedOutput(100)
    invalid.append(b"\xff" * 90)
    assert len(invalid.snapshot()[0].encode()) <= 100
    assert invalid.snapshot()[1] is True


def test_child_environment_has_no_service_or_host_secrets(tmp_path: Path) -> None:
    result = child_environment(
        tmp_path,
        {
            "PATH": "/usr/bin",
            "DS60_WORKER_TOKEN_FILE": "private",
            "AWS_SECRET_ACCESS_KEY": "secret",
            "PGPASSWORD": "secret",
            "DS60_MODULE_ENDPOINTS": "private",
            "HTTP_PROXY": "private",
        },
    )
    assert result["PATH"] == "/usr/bin"
    assert not any(
        key in result
        for key in (
            "DS60_WORKER_TOKEN_FILE",
            "AWS_SECRET_ACCESS_KEY",
            "PGPASSWORD",
            "HTTP_PROXY",
            "DS60_MODULE_ENDPOINTS",
        )
    )
    assert result["HF_HUB_OFFLINE"] == "1" and result["CUDA_VISIBLE_DEVICES"] == ""


def test_cancel_and_timeout_reap_real_children(tmp_path: Path) -> None:
    script = "import time\nprint('started',flush=True)\ntime.sleep(20)\n"
    source = tmp_path / "main.py"
    source.write_text(script)
    for cancelled in (False, True):
        cancel = threading.Event()
        output = BoundedOutput()
        timer = threading.Timer(0.2, cancel.set) if cancelled else None
        if timer:
            timer.start()
        try:
            code, status = run_process(
                [sys.executable, str(source)],
                tmp_path,
                child_environment(tmp_path),
                time.monotonic() + 0.4,
                cancel,
                output,
            )
            assert status == ("cancelled" if cancelled else "timed_out")
            assert code is not None and code != 0 and "started" in output.snapshot()[0]
        finally:
            if timer:
                timer.cancel()
                timer.join()


@pytest.mark.skipif(os.name != "posix", reason="Optional worker containers run Linux POSIX jobs.")
def test_descendant_is_killed_even_after_group_leader_exit(tmp_path: Path) -> None:
    child = "import time; time.sleep(30)"
    source = (
        "import subprocess,sys\np=subprocess.Popen([sys.executable,'-c',"
        + repr(child)
        + "])\nprint(p.pid,flush=True)\n"
    )
    result = execute(tmp_path, source)
    pid = int(result.output.strip())
    # A reaped/terminated child can remain a zombie briefly until the host init
    # reaps it. ps state Z is terminal, not a surviving running descendant.
    import subprocess

    state = subprocess.run(
        ["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True, check=False
    ).stdout.strip()
    assert not state or state.startswith("Z")


def test_fixed_cpp_compile_failure_cannot_run_stale_binary(tmp_path: Path) -> None:
    if not (shutil.which("g++") or shutil.which("clang++")):
        pytest.skip("No preinstalled C++ compiler; no installation is attempted.")
    phases: list[str] = []
    result = execute_operation(
        "cpp20", "int main() { return broken; }", tmp_path, 15, threading.Event(), phases.append
    )
    assert result.status == "failed" and result.returncode != 0
    assert phases == ["compiling"] and "main.cpp" in result.output
    assert "error" in result.output.lower()


def test_real_cpp_reference_and_typed_ownership_checks(tmp_path: Path) -> None:
    if not (shutil.which("g++") or shutil.which("clang++")):
        pytest.skip("No preinstalled C++ compiler; no installation is attempted.")
    source = (ROOT / "courses/cpp/solutions/cpp-009_solution.cpp").read_text()
    result = execute(
        tmp_path / "reference", source, profile="cpp20", verification="cpp-ownership-v1"
    )
    assert result.status == "succeeded", result.output
    assert len(result.checks) == 14 and all(check["passed"] for check in result.checks)
    learner = (ROOT / "courses/cpp/lessons/cpp-009.cpp").read_text()
    failed = execute(
        tmp_path / "learner", learner, profile="cpp20", verification="cpp-ownership-v1"
    )
    assert failed.status == "failed" and any(not check["passed"] for check in failed.checks)


def test_attention_reference_against_numeric_and_negative_oracles(tmp_path: Path) -> None:
    source = (ROOT / "courses/llm-theory/solutions/llm-009_solution.py").read_text()
    result = execute(tmp_path / "reference", source, verification="llm-causal-attention-v1")
    assert result.status == "succeeded", result.output
    assert len(result.checks) == 13 and all(check["passed"] for check in result.checks)
    source = "def attention(q,k,v,allowed):\n return v, allowed.astype(float)\n"
    failed = execute(tmp_path / "broken", source, verification="llm-causal-attention-v1")
    assert failed.status == "failed" and any(not item["passed"] for item in failed.checks)


def test_tf_oracle_checks_all_cases_without_requiring_tensorflow(tmp_path: Path) -> None:
    def gradient_step(rate: float = 0.1, initial_weight: float = 0) -> dict[str, float]:
        if isinstance(rate, bool):
            raise TypeError("rate")
        if rate <= 0:
            raise ValueError("rate")
        loss = 14 / 3 * (initial_weight - 2) ** 2
        gradient = 28 / 3 * (initial_weight - 2)
        after = initial_weight - rate * gradient
        return {
            "loss_before": loss,
            "gradient": gradient,
            "weight_after": after,
            "loss_after": 14 / 3 * (after - 2) ** 2,
        }

    path = tmp_path / "checks.json"
    verify_python_namespace({"gradient_step": gradient_step}, "tf-gradient-v1", path)
    checks = json.loads(path.read_text())["checks"]
    assert len(checks) == 15 and all(item["passed"] for item in checks)
    with pytest.raises(SystemExit):
        verify_python_namespace({"gradient_step": lambda **_: {}}, "tf-gradient-v1", path)


@pytest.mark.parametrize(
    "profile,language,verification",
    [
        ("missing", "python", None),
        ("cpp20", "python", None),
        ("python-core", "python", "tf-gradient-v1"),
        ("scala-jvm", "scala", "shell"),
    ],
)
def test_operations_are_registered_not_arbitrary(
    profile: str, language: str, verification: str | None
) -> None:
    with pytest.raises(ValueError):
        validate_operation(profile, language, verification)


def test_darwin_permission_error_is_ignored_only_for_terminal_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import subprocess

    from ds60sqlpy import worker_operations

    def denied(*args: Any) -> None:
        raise PermissionError("fixture permission denial")

    monkeypatch.setattr(os, "killpg", denied)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess([], 0, "123 Z\n", ""),
    )
    worker_operations._signal_group(123, 9)
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess([], 0, "123 S\n", ""),
    )
    with pytest.raises(PermissionError):
        worker_operations._signal_group(123, 9)
    monkeypatch.setattr(sys, "platform", "linux")
    with pytest.raises(PermissionError):
        worker_operations._signal_group(123, 9)


@pytest.mark.parametrize("mutation", ["ignored-qk", "missing-scale", "wrong-axis", "swapped-qk"])
def test_attention_worker_rejects_mechanism_mutants(tmp_path: Path, mutation: str) -> None:
    import ast

    original = (ROOT / "courses/llm-theory/solutions/llm-009_solution.py").read_text()
    tree = ast.parse(original)
    function = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "attention"
    )
    extracted = ast.get_source_segment(original, function)
    assert extracted is not None
    # Invoke only the submitted API. Its own optional verify()/stdout cannot
    # supply the worker's oracle or hide a mechanism defect.
    source = "import numpy as np\n" + extracted + "\n"
    replacements = {
        "ignored-qk": ("scores = (q @ k.T) / np.sqrt(width)", "scores = np.zeros((count,count))"),
        "missing-scale": ("scores = (q @ k.T) / np.sqrt(width)", "scores = q @ k.T"),
        "wrong-axis": ("weights.sum(axis=1, keepdims=True)", "weights.sum(axis=0, keepdims=True)"),
        "swapped-qk": (
            "scores = (q @ k.T) / np.sqrt(width)",
            "scores = (k @ q.T) / np.sqrt(width)",
        ),
    }
    before, after = replacements[mutation]
    assert before in source
    result = execute(
        tmp_path, source.replace(before, after), verification="llm-causal-attention-v1"
    )
    assert result.status == "failed" and result.returncode != 0
    assert any(
        item["name"].startswith("nonuniform-") and not item["passed"] for item in result.checks
    )


def test_output_thread_start_failure_reaps_the_already_spawned_process(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import subprocess

    original = subprocess.Popen
    children: list[subprocess.Popen[bytes]] = []

    def capture(*args: Any, **kwargs: Any) -> subprocess.Popen[bytes]:
        process = original(*args, **kwargs)
        children.append(process)
        return process

    def fail_start(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("cannot start new thread")

    monkeypatch.setattr(subprocess, "Popen", capture)
    monkeypatch.setattr(threading.Thread, "start", fail_start)
    output = BoundedOutput()
    try:
        code, status = run_process(
            [sys.executable, "-c", "import time;time.sleep(20)"],
            tmp_path,
            child_environment(tmp_path),
            time.monotonic() + 1,
            threading.Event(),
            output,
        )
        assert status == "failed" and code is not None
        assert children[0].poll() is not None
        assert "Output monitoring could not start" in output.snapshot()[0]
    finally:
        for process in children:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=3)
