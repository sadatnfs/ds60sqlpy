"""Real-process regressions for the narrowly scoped .NET compiler allowance."""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

import pytest

from ds60sqlpy import worker_operations
from ds60sqlpy.worker_operations import (
    MAX_SCRATCH_BYTES,
    BoundedOutput,
    child_environment,
    execute_operation,
    run_process,
)

pytestmark = pytest.mark.skipif(os.name != "posix", reason="Supported worker limits are POSIX")


def run_python(
    directory: Path,
    source: str,
    *,
    file_limit_bytes: int = MAX_SCRATCH_BYTES,
    environment: dict[str, str] | None = None,
) -> tuple[int | None, str | None, str]:
    directory.mkdir(parents=True, exist_ok=True)
    output = BoundedOutput()
    code, status = run_process(
        [sys.executable, "-c", source],
        directory,
        child_environment(directory) if environment is None else environment,
        time.monotonic() + 10,
        threading.Event(),
        output,
        file_limit_bytes=file_limit_bytes,
    )
    return code, status, output.snapshot()[0]


@pytest.mark.skipif(
    sys.platform != "linux" or not hasattr(os, "memfd_create"),
    reason="Linux memfd demonstrates the Roslyn backing-file limit without a disk file",
)
@pytest.mark.parametrize("compile_allowance", [False, True])
def test_anonymous_48_mib_backing_file_requires_the_trusted_compile_allowance(
    tmp_path: Path, compile_allowance: bool
) -> None:
    source = """
import os
fd = os.memfd_create('compiler-backing-fixture')
try:
    os.ftruncate(fd, 48 * 1024 * 1024)
    print(os.fstat(fd).st_size)
finally:
    os.close(fd)
"""
    code, status, output = run_python(
        tmp_path,
        source,
        file_limit_bytes=MAX_SCRATCH_BYTES * (2 if compile_allowance else 1),
    )
    assert status is None
    if compile_allowance:
        assert code == 0 and output.strip() == str(48 * 1024 * 1024)
    else:
        assert code != 0 and "File too large" in output
    assert list(tmp_path.iterdir()) == []  # Anonymous descriptor is not workspace growth.


def test_an_environment_value_cannot_promote_the_default_runtime_limit(tmp_path: Path) -> None:
    environment = child_environment(tmp_path)
    environment["_DS60_FILE_LIMIT_BYTES"] = str(MAX_SCRATCH_BYTES * 2)
    before = dict(environment)
    code, status, output = run_python(
        tmp_path,
        "import json,os,resource; "
        "print(json.dumps({'limit':resource.getrlimit(resource.RLIMIT_FSIZE),"
        "'internal':os.environ.get('_DS60_FILE_LIMIT_BYTES')}))",
        environment=environment,
    )
    assert code == 0 and status is None
    assert json.loads(output) == {"limit": [MAX_SCRATCH_BYTES, MAX_SCRATCH_BYTES], "internal": None}
    assert environment == before
    inherited = child_environment(tmp_path, {"_DS60_FILE_LIMIT_BYTES": str(MAX_SCRATCH_BYTES * 2)})
    assert "_DS60_FILE_LIMIT_BYTES" not in inherited


@pytest.mark.parametrize("remain_alive", [False, True])
def test_larger_compiler_descriptor_limit_never_expands_actual_workspace_allowance(
    tmp_path: Path, remain_alive: bool
) -> None:
    source = (
        "import time\n"
        "with open('oversized.bin','wb') as stream:\n"
        f"    stream.truncate({MAX_SCRATCH_BYTES + 1})\n"
        "print('file created', flush=True)\n" + ("time.sleep(20)\n" if remain_alive else "")
    )
    began = time.monotonic()
    code, status, output = run_python(tmp_path, source, file_limit_bytes=MAX_SCRATCH_BYTES * 2)
    assert status == "failed"
    assert code is not None
    assert "scratch allowance" in output
    assert time.monotonic() - began < 5
    assert (tmp_path / "oversized.bin").stat().st_size == MAX_SCRATCH_BYTES + 1


@pytest.mark.parametrize("profile", ["csharp-dotnet", "swift-linux", "c17"])
def test_only_csharp_compilation_gets_64_mib_and_every_runtime_returns_to_32_mib(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, profile: str
) -> None:
    # Substitute tiny compiler/runtime executables, not run_process. The real
    # supervisor and process wrapper must install and reset the actual limits.
    def commands(profile_id: str, directory: Path) -> tuple[list[list[str]], list[str]]:
        assert profile_id == profile
        compiler = (
            "import pathlib,resource; "
            "limit=resource.getrlimit(resource.RLIMIT_FSIZE)[0]; "
            "pathlib.Path('compiled-limit.txt').write_text(str(limit)); "
            "print('compiler completed')"
        )
        runtime = (
            "import pathlib,resource; "
            "print('compile='+pathlib.Path('compiled-limit.txt').read_text()); "
            "print('runtime='+str(resource.getrlimit(resource.RLIMIT_FSIZE)[0]))"
        )
        return [[sys.executable, "-c", compiler]], [sys.executable, "-c", runtime]

    monkeypatch.setattr(worker_operations, "language_commands", commands)
    stages: list[str] = []
    result = execute_operation(
        profile,
        "// source is retained while the test supplies a tiny prepared compiler",
        tmp_path,
        15,
        threading.Event(),
        stages.append,
    )
    assert result.status == "succeeded" and result.returncode == 0
    compile_limit = MAX_SCRATCH_BYTES * (2 if profile == "csharp-dotnet" else 1)
    assert f"compile={compile_limit}" in result.output
    assert f"runtime={MAX_SCRATCH_BYTES}" in result.output
    assert stages == ["compiling", "running"]
    assert result.checks == []


@pytest.mark.parametrize("profile", ["csharp-dotnet", "swift-linux", "c17"])
def test_a_failed_compiler_never_starts_the_runtime_or_reports_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, profile: str
) -> None:
    def commands(profile_id: str, directory: Path) -> tuple[list[list[str]], list[str]]:
        return (
            [
                [
                    sys.executable,
                    "-c",
                    "print('controlled compiler diagnostic'); raise SystemExit(7)",
                ]
            ],
            [
                sys.executable,
                "-c",
                "from pathlib import Path; Path('MUST_NOT_RUN').write_text('ran')",
            ],
        )

    monkeypatch.setattr(worker_operations, "language_commands", commands)
    stages: list[str] = []
    source = "retained learner draft"
    result = execute_operation(profile, source, tmp_path, 15, threading.Event(), stages.append)
    assert result.status == "failed" and result.returncode == 7
    assert "controlled compiler diagnostic" in result.output
    assert "Compilation" in result.detail
    assert stages == ["compiling"]
    assert result.checks == []
    assert not (tmp_path / "MUST_NOT_RUN").exists()
    filename = worker_operations.PROFILES[profile].filename
    assert (tmp_path / filename).read_text() == source


@pytest.mark.parametrize("limit", [0, MAX_SCRATCH_BYTES - 1, MAX_SCRATCH_BYTES * 3])
def test_unreviewed_descriptor_limits_are_rejected_before_starting_a_process(
    tmp_path: Path, limit: int
) -> None:
    with pytest.raises(ValueError, match="reviewed"):
        run_python(
            tmp_path,
            "from pathlib import Path; Path('MUST_NOT_RUN').write_text('ran')",
            file_limit_bytes=limit,
        )
    assert not (tmp_path / "MUST_NOT_RUN").exists()
