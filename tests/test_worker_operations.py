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
    assert (
        result.status == "succeeded"
        and result.returncode == 0
        and result.output.splitlines() == ["42"]
    )
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


def test_merged_capture_cannot_reorder_final_stderr_behind_buffered_stdout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ds60sqlpy import worker_operations

    prefix_done, stderr_seen = threading.Event(), threading.Event()
    prefix = b"HEAD\n" + b"x" * 100000 + b"PREFIX-DRAINED\n"
    flood = b"x" * 100000

    def chunks(value: bytes) -> list[bytes]:
        return [value[index : index + 8192] for index in range(0, len(value), 8192)]

    class Pipe:
        def __init__(
            self,
            data: list[bytes],
            *,
            wait_before: int | None = None,
            signal: threading.Event | None = None,
        ) -> None:
            self.data = data
            self.position = 0
            self.wait_before = wait_before
            self.signal = signal
            self.finished = False

        def read1(self, size: int) -> bytes:
            if self.position == self.wait_before:
                assert self.signal is not None and self.signal.wait(2)
            if self.position == len(self.data):
                self.finished = True
                return b""
            value = self.data[self.position]
            self.position += 1
            assert len(value) <= size
            return value

        def close(self) -> None:
            pass

    class Process:
        returncode: int | None = None
        pid = 1234567

        def __init__(self, merged: bool) -> None:
            # Separate reader scheduling deterministically drains final stderr
            # before the remaining stdout. A merged pipe retains write order.
            self.stdout = (
                Pipe(chunks(prefix) + chunks(flood) + [b"TAIL\n"])
                if merged
                else Pipe(
                    chunks(prefix) + chunks(flood),
                    wait_before=len(chunks(prefix)),
                    signal=stderr_seen,
                )
            )
            self.stderr = None if merged else Pipe([b"TAIL\n"], wait_before=0, signal=prefix_done)

        def poll(self) -> int | None:
            if self.stdout.finished and (self.stderr is None or self.stderr.finished):
                self.returncode = 7
            return self.returncode

    def observe(text: str, _truncated: bool) -> None:
        if "PREFIX-DRAINED" in text:
            prefix_done.set()
        if "TAIL" in text:
            stderr_seen.set()

    def start(_command: list[str], **options: Any) -> Process:
        return Process(options["stderr"] == subprocess.STDOUT)

    import subprocess

    monkeypatch.setattr(subprocess, "Popen", start)
    cleaned: list[bool] = []
    monkeypatch.setattr(worker_operations, "_stop_tree", lambda *a, **kw: cleaned.append(True))
    output = BoundedOutput(observer=observe)
    code, interrupted = run_process(
        ["synthetic-child"], tmp_path, {}, time.monotonic() + 5, threading.Event(), output
    )
    text, truncated = output.snapshot()
    assert code == 7 and interrupted is None and cleaned == [True]
    assert truncated and len(text.encode("utf-8")) <= MAX_OUTPUT_BYTES
    assert text.startswith("HEAD\n") and text.endswith("TAIL\n")


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
        started = threading.Event()
        startup_expired = threading.Event()

        def observe(text: str, _truncated: bool, ready: threading.Event = started) -> None:
            if "started" in text.splitlines():
                ready.set()

        def cancel_after_observed_start(
            ready: threading.Event = started,
            expired: threading.Event = startup_expired,
            cancellation: threading.Event = cancel,
        ) -> None:
            if not ready.wait(timeout=5):
                expired.set()
            cancellation.set()

        output = BoundedOutput(observer=observe)
        controller = threading.Thread(target=cancel_after_observed_start) if cancelled else None
        if controller:
            controller.start()
        try:
            code, status = run_process(
                [sys.executable, str(source)],
                tmp_path,
                child_environment(tmp_path),
                time.monotonic() + (10 if cancelled else 0.4),
                cancel,
                output,
            )
            assert status == ("cancelled" if cancelled else "timed_out")
            assert code is not None and code != 0
            if cancelled:
                assert not startup_expired.is_set(), (
                    "Child startup was not observed before cancellation"
                )
                assert "started" in output.snapshot()[0].splitlines()
            # The timeout still includes interpreter startup. Under contention
            # it may legitimately reap the child before any output is written.
        finally:
            if controller:
                started.set()  # Release the helper if process startup itself failed.
                controller.join(timeout=1)
                assert not controller.is_alive()


@pytest.mark.skipif(os.name != "posix", reason="Optional worker containers run Linux POSIX jobs.")
def test_learner_job_is_stopped_first_when_memory_runs_out(tmp_path: Path) -> None:
    source = (
        "from pathlib import Path\n"
        "score = Path('/proc/self/oom_score_adj')\n"
        "print(score.read_text().strip() if score.exists() else 'no-proc')\n"
    )
    result = execute(tmp_path, source)
    # Without /proc (macOS hosts) the wrapper still runs the program.
    expected = "1000" if Path("/proc/self/oom_score_adj").exists() else "no-proc"
    assert result.status == "succeeded" and result.output.strip() == expected


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

    def verify(directory: Path, source: str) -> Any:
        # Each typed harness compiles two translation units and links a program.
        # Use the existing 60-second classroom deadline under parallel host load:
        # this assertion concerns ownership semantics, not compiler throughput.
        phases: list[str] = []
        result = execute_operation(
            "cpp20", source, directory, 60, threading.Event(), phases.append, "cpp-ownership-v1"
        )
        assert phases == ["compiling", "compiling", "compiling", "running", "verifying"], (
            result.output
        )
        return result

    source = (ROOT / "courses/cpp/solutions/cpp-009_solution.cpp").read_text()
    result = verify(tmp_path / "reference", source)
    assert result.status == "succeeded", result.output
    assert len(result.checks) == 14 and all(check["passed"] for check in result.checks)
    learner = (ROOT / "courses/cpp/lessons/cpp-009.cpp").read_text()
    failed = verify(tmp_path / "learner", learner)
    assert failed.status == "failed", failed.output
    assert any(not check["passed"] for check in failed.checks)


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

    monkeypatch.setattr(os, "killpg", denied, raising=False)
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


def test_module_python_errors_start_at_the_learner_frame(tmp_path: Path) -> None:
    source = "def ratio(count):\n    return 10 / count\n\nprint(ratio(0))\n"
    result = execute(tmp_path / "runtime", source)
    assert result.output.startswith(
        'Traceback (most recent call last):\n  File "main.py", line 4, in <module>\n'
    )
    assert 'File "main.py", line 2, in ratio' in result.output
    assert result.output.rstrip().endswith("ZeroDivisionError: division by zero")
    assert "<frozen runpy>" not in result.output and "worker_figures" not in result.output
    syntax = execute(tmp_path / "syntax", "values = [1]\nfor value in values\n    print(value)\n")
    assert syntax.output == (
        '  File "main.py", line 2\n    for value in values\n                       ^\n'
        "SyntaxError: expected ':'\n"
    )
    verified = execute(
        tmp_path / "verified", "print([][1])\n", verification="llm-causal-attention-v1"
    )
    assert verified.output.startswith(
        'Traceback (most recent call last):\n  File "main.py", line 1, in <module>\n'
    )
    assert "verify.py" not in verified.output and "<frozen runpy>" not in verified.output
    # PyTensor (imported by PyMC) replaces sys.excepthook with one that calls
    # sys.__excepthook__; the report must stay trimmed through such hooks.
    hooked = execute(
        tmp_path / "hooked",
        "import sys\nsys.excepthook = lambda *error: sys.__excepthook__(*error)\n"
        "raise ValueError('boom')\n",
    )
    assert hooked.output == (
        'Traceback (most recent call last):\n  File "main.py", line 3, in <module>\n'
        "    raise ValueError('boom')\nValueError: boom\n"
    )
    assert result.raw_output is syntax.raw_output is verified.raw_output is None


def test_runner_errors_keep_the_complete_traceback(tmp_path: Path) -> None:
    import subprocess

    # No main.py: the failure belongs to the runner, so nothing is trimmed.
    run = subprocess.run(
        [sys.executable, "-m", "ds60sqlpy.worker_figures"],
        cwd=tmp_path,
        env=child_environment(tmp_path),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert run.returncode == 1
    assert "worker_figures.py" in run.stderr and "FileNotFoundError" in run.stderr


def test_only_the_arviz_refactor_notice_is_silenced(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "arviz.py").write_text(
        "import warnings\n"
        'warnings.warn("\\nArviZ is undergoing a major refactor to improve flexibility.",'
        " FutureWarning)\n"
    )
    source = 'import warnings\nimport arviz\nwarnings.warn("learner notice", FutureWarning)\n'
    result = execute(tmp_path, source + 'print("done")\n')
    assert result.status == "succeeded"
    assert "ArviZ is undergoing" not in result.output
    assert "FutureWarning: learner notice" in result.output and "done" in result.output


def test_job_details_use_plain_words(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from ds60sqlpy import worker_operations

    assert execute(tmp_path / "ok", "print(1)\n").detail == "The program finished."
    exited = execute(tmp_path / "exit", "raise SystemExit(3)\n")
    assert exited.detail == "The program finished with exit code 3."
    killed = execute(tmp_path / "kill", "import os, signal\nos.kill(os.getpid(), signal.SIGKILL)\n")
    assert (killed.status, killed.returncode) == ("failed", -9)
    assert killed.detail == "The program was stopped by the system (signal 9)."
    aborted = execute(tmp_path / "abort", "import os\nos.abort()\n")
    assert aborted.detail == "The program stopped itself after an error (signal 6)."
    cancel = threading.Event()
    cancel.set()
    stopped = execute_operation("python-core", "print(1)\n", tmp_path / "stop", 15, cancel, print)
    assert (stopped.status, stopped.detail) == ("cancelled", "Cancelled; the program was stopped.")
    monkeypatch.setattr(worker_operations, "run_process", lambda *a, **kw: (-15, "timed_out"))
    late = execute(tmp_path / "late", "print(1)\n")
    assert (late.status, late.detail) == ("timed_out", "Stopped at the time limit.")


def test_runner_jvm_notices_are_hidden_but_kept_in_the_raw_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ds60sqlpy import worker_operations

    tools = tmp_path / "tools"
    tools.mkdir()

    def tool(name: str, body: str) -> str:
        # Stand-ins print the startup notice first, as a real JVM does.
        path = tools / name
        path.write_text(
            f"#!{sys.executable}\nimport os, sys\n"
            "notice = 'Picked up JAVA_TOOL_OPTIONS: ' + os.environ['JAVA_TOOL_OPTIONS']\n"
            "print(notice, file=sys.stderr)\n" + body
        )
        path.chmod(0o755)
        return str(path)

    javac = tool("javac", "print('Main.java:3: warning: [rawtypes] found raw type')\n")
    # The learner program relays a child JVM's stderr; that copy stays visible.
    java = tool("java", "print('Hello')\nprint(notice)\n")
    monkeypatch.setattr(
        worker_operations, "language_commands", lambda profile, directory: ([[javac]], [java])
    )
    result = execute_operation(
        "java21", "class Main {}", tmp_path / "job", 15, threading.Event(), lambda _: None
    )
    notice = "Picked up JAVA_TOOL_OPTIONS: " + child_environment(tmp_path)["JAVA_TOOL_OPTIONS"]
    warning = "Main.java:3: warning: [rawtypes] found raw type"
    assert result.status == "succeeded"
    assert result.output == f"{warning}\nHello\n{notice}\n"
    assert result.raw_output == f"{notice}\n{warning}\n{notice}\nHello\n{notice}\n"


def test_jvm_notices_match_across_chunks_and_only_at_the_start() -> None:
    from ds60sqlpy.worker_operations import _ChildOutput

    notice = b"Picked up JAVA_TOOL_OPTIONS: -Xint\n"
    incubator = b"WARNING: Using incubator modules: jdk.incubator.vector\n"
    raw, shown = BoundedOutput(), BoundedOutput()
    sink = _ChildOutput(raw, shown, (notice, notice, incubator))
    stream = notice + notice + incubator + b"row 1\n" + notice
    for byte in stream:
        sink.append(bytes([byte]))
    sink.finish()
    assert shown.snapshot()[0] == "row 1\n" + notice.decode()
    assert raw.snapshot()[0] == stream.decode()
    other, cut = BoundedOutput(), BoundedOutput()
    different = _ChildOutput(BoundedOutput(), other, (notice,))
    different.append(b"Picked up JAVA_TOOL_OPTIONS: -Xss1m\nok\n")
    ended = _ChildOutput(BoundedOutput(), cut, (notice,))
    ended.append(b"Picked up JAVA")
    for sink in (different, ended):
        sink.finish()
    assert other.snapshot()[0] == "Picked up JAVA_TOOL_OPTIONS: -Xss1m\nok\n"
    assert cut.snapshot()[0] == "Picked up JAVA"


def test_php_runs_the_learner_file_once_without_a_lint_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ds60sqlpy import worker_operations

    commands: list[list[str]] = []

    def record(argv: list[str], *args: Any, **kwargs: Any) -> tuple[int, None]:
        commands.append(argv)
        return 0, None

    monkeypatch.setattr(worker_operations, "run_process", record)
    stages: list[str] = []
    result = execute_operation(
        "php-cli", "<?php echo 1;\n", tmp_path, 15, threading.Event(), stages.append
    )
    assert result.status == "succeeded" and stages == ["running"]
    assert len(commands) == 1 and commands[0][-1] == "main.php" and "-l" not in commands[0]


def test_node_output_hides_only_node_internals() -> None:
    from ds60sqlpy.worker_operations import display_output

    fixtures = ROOT / "tests/fixtures/run_explain/javascript-node.json"
    case = {item["case"]: item["output"] for item in json.loads(fixtures.read_text())}
    assert display_output("javascript-node", case["syntax"]) == (
        'file:///tmp/job-xxxxxxxx/main.mjs:2\nconsole.log("Hello, " + name;\n'
        "                        ^^^^\n\nSyntaxError: missing ) after argument list\n\n"
        "Node.js v24.22.3\n"
    )
    assertion = display_output("javascript-node", case["assertion"])
    assert assertion.startswith("AssertionError [ERR_ASSERTION]: Expected values")
    assert "    at file:///tmp/job-xxxxxxxx/main.mjs:4:8 {\n  generatedMessage: true," in assertion
    assert "node:internal" not in assertion and "triggerUncaughtException" not in assertion
    missing = display_output("javascript-node", case["missing-package"])
    assert missing.startswith("Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'lodash'")
    assert "main.mjs {\n  code: 'ERR_MODULE_NOT_FOUND'\n}\n" in missing
    # A built-in that the program called stays; only Node's own callers go.
    called = (
        "Error: ENOENT: no such file or directory, open 'missing.txt'\n"
        "    at Object.readFileSync (node:fs:441:20)\n"
        "    at file:///tmp/job-1/main.mjs:2:4\n"
        "    at ModuleJob.run (node:internal/modules/esm/module_job:561:25)\n"
        "    at TracingChannel.tracePromise (node:diagnostics_channel:370:14)\n"
    )
    assert display_output("typescript-node", called) == "".join(called.splitlines(True)[:3])
    printed = "node:fs:12\nnot a source excerpt\n    at home\n"
    assert display_output("javascript-node", printed) == printed


@pytest.mark.parametrize(
    "line,shown",
    [
        ("Calls: .ds60_run -> source", None),
        ("Calls: .ds60_run -> source -> withVisible -> eval -> eval", None),
        (
            "Calls: .ds60_run -> source -> withVisible -> eval -> eval -> mean_of -> check",
            "Calls: mean_of -> check",
        ),
        ("Calls: .ds60_run ... eval -> eval -> outer -> inner", "Calls: outer -> inner"),
        ("Calls: .ds60_run ... level_five -> level_six", "Calls: ... level_five -> level_six"),
        ("Calls: .ds60_run -> <Anonymous>", "Calls: .ds60_run -> <Anonymous>"),
        ("Calls: helper -> stop", "Calls: helper -> stop"),
    ],
)
def test_r_calls_line_drops_only_the_runner_chain(line: str, shown: str | None) -> None:
    from ds60sqlpy.worker_operations import display_output

    text = f"Error in f() : boom\n{line}\nExecution halted\n"
    expected = "Error in f() : boom\n" + (f"{shown}\n" if shown else "") + "Execution halted\n"
    assert display_output("r-statistics", text) == expected


def test_pyspark_json_copy_of_an_error_is_hidden_but_the_traceback_stays() -> None:
    from ds60sqlpy.worker_operations import display_output

    fixtures = ROOT / "tests/fixtures/run_explain/spark-local-python.json"
    case = next(
        item for item in json.loads(fixtures.read_text()) if item["case"] == "analysis-exception"
    )
    shown = display_output("spark-local-python", case["output"])
    assert "DataFrameQueryContextLogger" in case["output"]
    assert "QueryContextLogger" not in shown
    assert 'File "/tmp/job-xxxxxxxx/main.py", line 5, in <module>' in shown
    assert "AnalysisException: [UNRESOLVED_COLUMN.WITH_SUGGESTION]" in shown
    learner = '{"ts": "now", "level": "ERROR", "logger": "my_job", "msg": "kept"}\n'
    assert display_output("spark-local-python", learner) == learner
