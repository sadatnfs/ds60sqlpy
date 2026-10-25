"""CPU-only contract tests for optional GPU admission, execution and quarantine.

These tests deliberately do not claim a real NVIDIA device ran a kernel.
"""

from __future__ import annotations

import sys
import threading
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from ds60sqlpy import gpu_runtime, worker_operations
from ds60sqlpy.module_worker import WorkerRequestError, WorkerState
from ds60sqlpy.worker_operations import BoundedOutput, OperationResult


@pytest.mark.parametrize("profile", sorted(gpu_runtime.GPU_PROFILES))
def test_gpu_environment_exposes_only_selected_container_device_without_secrets(
    profile: str,
    tmp_path: Path,
) -> None:
    environment = worker_operations.child_environment(
        tmp_path,
        {
            "PATH": "/usr/bin",
            "CUDA_VISIBLE_DEVICES": "all",
            "NVIDIA_VISIBLE_DEVICES": "all",
            "DS60_WORKER_TOKEN": "private",
            "DATABASE_URL": "private",
            "PYTHONOPTIMIZE": "1",
            "HTTP_PROXY": "private",
        },
        profile_id=profile,
    )
    assert environment["CUDA_VISIBLE_DEVICES"] == "0"
    assert environment["CUDA_CACHE_PATH"] == str(tmp_path / "cuda-cache")
    assert environment["HF_HUB_OFFLINE"] == "1"
    assert environment["TF_FORCE_GPU_ALLOW_GROWTH"] == "true"
    assert (
        not {
            "DS60_WORKER_TOKEN",
            "DATABASE_URL",
            "NVIDIA_VISIBLE_DEVICES",
            "PYTHONOPTIMIZE",
            "HTTP_PROXY",
        }
        & environment.keys()
    )


@pytest.mark.parametrize(
    "profile", ["python-core", "tensorflow-cpu", "llm-torch-cpu", "cpp20", None]
)
def test_cpu_profiles_continue_hiding_gpus(profile: str | None, tmp_path: Path) -> None:
    environment = worker_operations.child_environment(
        tmp_path,
        {"CUDA_VISIBLE_DEVICES": "0"},
        profile_id=profile,
    )
    assert environment["CUDA_VISIBLE_DEVICES"] == ""
    assert "CUDA_CACHE_PATH" not in environment
    assert "TF_FORCE_GPU_ALLOW_GROWTH" not in environment


def test_cuda_cpp_has_one_fixed_source_target_and_no_shell(tmp_path: Path) -> None:
    compiling, run = gpu_runtime.commands("cuda-cpp", tmp_path)
    assert len(compiling) == 1
    argv = compiling[0]
    assert argv[0] == "nvcc"
    assert argv[-3:] == ["main.cu", "-o", "program"]
    assert "-std=c++20" in argv
    assert "-gencode=arch=compute_75,code=[sm_75,compute_75]" in argv
    assert run == [str(tmp_path / "program")]
    assert not {"sh", "bash", "-c"} & set(argv)
    assert worker_operations.PROFILES["cuda-cpp"].filename == "main.cu"


@pytest.mark.parametrize("profile", ["cuda-python", "pytorch-cuda", "tensorflow-cuda"])
def test_gpu_python_profiles_share_only_fixed_entrypoint(profile: str, tmp_path: Path) -> None:
    compiling, run = gpu_runtime.commands(profile, tmp_path)
    assert compiling == []
    assert run == [sys.executable, "-u", "main.py"]


def test_unknown_gpu_profile_cannot_choose_a_command(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="registered CUDA profile"):
        gpu_runtime.commands("bash -c something", tmp_path)
    assert not list(tmp_path.iterdir())


def test_cpp_probe_requires_allocation_launch_completion_and_readback(tmp_path: Path) -> None:
    commands = gpu_runtime.probe_commands("cuda-cpp", tmp_path)
    source = (tmp_path / "main.cu").read_text()
    assert len(commands) == 2
    for requirement in (
        "cudaGetDeviceCount",
        "cudaMalloc",
        "<<<1, 1>>>",
        "cudaGetLastError",
        "cudaDeviceSynchronize",
        "cudaMemcpy",
        "cudaFree",
        "result != 42",
    ):
        assert requirement in source
    assert "return 77" in source  # No device is not readiness.
    assert "return 79" in source  # Wrong answer is not readiness.


@pytest.mark.parametrize("profile", sorted(gpu_runtime.GPU_PROFILES))
def test_real_probe_failure_never_becomes_ready(
    profile: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_process(
        argv: list[str],
        directory: Path,
        environment: dict[str, str],
        deadline: float,
        cancel: threading.Event,
        output: BoundedOutput,
        **limits: Any,
    ) -> tuple[int | None, str | None]:
        calls.append(argv)
        assert environment["CUDA_VISIBLE_DEVICES"] == "0"
        assert deadline > 0 and not cancel.is_set()
        if argv[0] == "nvcc":
            assert (directory / "main.cu").is_file()
            return 0, None  # Compiling alone must not establish readiness.
        output.append(b"No actual CUDA device; numerical probe unavailable.\n")
        return 77, None

    monkeypatch.setattr(worker_operations, "run_process", fake_process)
    ready, detail = worker_operations.probe_profile(profile)
    assert ready is False
    assert "probe failed" in detail and "unavailable" in detail
    assert len(calls) == (2 if profile == "cuda-cpp" else 1)


def test_probe_compile_error_prevents_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_process(
        argv: list[str],
        directory: Path,
        environment: dict[str, str],
        deadline: float,
        cancel: threading.Event,
        output: BoundedOutput,
        **limits: Any,
    ) -> tuple[int | None, str | None]:
        calls.append(argv)
        output.append(b"nvcc compile failure\n")
        return 1, None

    monkeypatch.setattr(worker_operations, "run_process", fake_process)
    ready, detail = worker_operations.probe_profile("cuda-cpp")
    assert ready is False and "compile failure" in detail
    assert len(calls) == 1 and calls[0][0] == "nvcc"


def test_torch_probe_rejects_a_cpu_tensor_even_if_device_discovery_claims_gpu(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cpu_result = SimpleNamespace(is_cuda=False, cpu=lambda: 42)
    fake_torch = SimpleNamespace(
        version=SimpleNamespace(cuda="test"),
        cuda=SimpleNamespace(is_available=lambda: True, synchronize=lambda: None),
        tensor=lambda *args, **kwargs: SimpleNamespace(sum=lambda: cpu_result),
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    with pytest.raises(AssertionError):
        exec(gpu_runtime.PYTHON_PROBES["pytorch-cuda"], {})


def test_tensorflow_probe_disables_soft_placement_and_rejects_cpu_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import contextlib

    calls: list[Any] = []
    fake_tf = SimpleNamespace(
        test=SimpleNamespace(is_built_with_cuda=lambda: True),
        config=SimpleNamespace(
            list_physical_devices=lambda kind: ["GPU"],
            experimental=SimpleNamespace(
                set_memory_growth=lambda device, enabled: calls.append((device, enabled))
            ),
            set_soft_device_placement=lambda enabled: calls.append(enabled),
        ),
        device=lambda name: contextlib.nullcontext(),
        constant=lambda values: values,
        reduce_sum=lambda values: SimpleNamespace(device="/device:CPU:0", numpy=lambda: 42),
    )
    monkeypatch.setitem(sys.modules, "tensorflow", fake_tf)
    with pytest.raises(AssertionError):
        exec(gpu_runtime.PYTHON_PROBES["tensorflow-cuda"], {})
    assert False in calls
    assert ("GPU", True) in calls


def test_cupy_probe_fails_before_array_creation_if_no_device(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_cp = SimpleNamespace(
        cuda=SimpleNamespace(runtime=SimpleNamespace(getDeviceCount=lambda: 0))
    )
    monkeypatch.setitem(sys.modules, "cupy", fake_cp)
    with pytest.raises(AssertionError):
        exec(gpu_runtime.PYTHON_PROBES["cuda-python"], {})


def test_cuda_execution_uses_one_total_deadline_and_stages_literal_source(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[tuple[list[str], float]] = []
    source = "// learner text is source, never shell argv\nint main(){return 0;}\n"
    statuses: list[str] = []

    def fake_process(
        argv: list[str],
        directory: Path,
        environment: dict[str, str],
        deadline: float,
        cancel: threading.Event,
        output: BoundedOutput,
        **limits: Any,
    ) -> tuple[int | None, str | None]:
        calls.append((argv, deadline))
        assert (directory / "main.cu").read_text() == source
        assert environment["CUDA_VISIBLE_DEVICES"] == "0"
        assert limits == {}
        output.append(b"compile or run observation\n")
        return 0, None

    monkeypatch.setattr(worker_operations, "run_process", fake_process)
    result = worker_operations.execute_operation(
        "cuda-cpp", source, tmp_path, 15, threading.Event(), statuses.append
    )
    assert result.status == "succeeded" and result.checks == []
    assert statuses == ["compiling", "running"]
    assert len(calls) == 2
    assert calls[0][1] <= calls[1][1]
    assert calls[1][1] - calls[0][1] < 0.1


@pytest.mark.parametrize("timeout", [0, 1, 121, True])
def test_gpu_execution_rejects_unbounded_or_invalid_timeout(timeout: Any, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="total deadline"):
        worker_operations.execute_operation(
            "cuda-cpp", "", tmp_path, timeout, threading.Event(), lambda value: None
        )
    assert not list(tmp_path.iterdir())


def test_gpu_execution_rejects_oversized_source_before_writing(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="256 KiB"):
        worker_operations.execute_operation(
            "cuda-python",
            "x" * (worker_operations.MAX_SOURCE_BYTES + 1),
            tmp_path,
            15,
            threading.Event(),
            lambda value: None,
        )
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "profile,status,output,detail,quarantined",
    [
        (
            "cuda-cpp",
            "timed_out",
            "",
            "Total execution deadline exceeded; child processes reaped.",
            True,
        ),
        ("cuda-python", "cancelled", "", "Cancelled and child processes reaped.", True),
        (
            "pytorch-cuda",
            "failed",
            "CUDA error: device-side assert triggered",
            "Execution completed.",
            True,
        ),
        (
            "tensorflow-cuda",
            "failed",
            "an illegal memory access was encountered",
            "Execution completed.",
            True,
        ),
        (
            "cuda-cpp",
            "failed",
            "nvcc: syntax error",
            "Compilation did not produce a runnable artifact.",
            False,
        ),
        ("cuda-cpp", "timed_out", "", "Compilation did not produce a runnable artifact.", False),
        ("cuda-python", "failed", "AssertionError: expected 42", "Execution completed.", False),
        ("cuda-cpp", "succeeded", "validated", "Execution completed.", False),
        (
            "python-core",
            "timed_out",
            "",
            "Total execution deadline exceeded; child processes reaped.",
            False,
        ),
    ],
)
def test_device_fault_quarantine_blocks_next_job_but_retains_result(
    profile: str,
    status: str,
    output: str,
    detail: str,
    quarantined: bool,
) -> None:
    def executor(*args: Any, **kwargs: Any) -> OperationResult:
        return OperationResult(0 if status == "succeeded" else 1, output, False, status, detail)

    state = WorkerState(profile, executor=executor, ready=True, isolate_jobs=False)
    payload: dict[str, Any] = {
        "job_id": uuid.uuid4().hex,
        "profile": profile,
        "operation": "execute",
        "source": "learner source retained by the application",
        "language": worker_operations.PROFILES[profile].language,
        "timeout_seconds": 15,
        "verification_id": None,
    }
    try:
        state.submit(payload)
        assert state.thread is not None
        state.thread.join(timeout=3)
        assert not state.thread.is_alive()
        receipt = state.get(payload["job_id"])
        assert receipt["status"] == status and receipt["output"] == output
        assert receipt["checks"] == []
        assert state.ready is not quarantined
        if quarantined:
            assert "No GPU reset was attempted" in state.detail
            with pytest.raises(WorkerRequestError, match="owner review") as error:
                state.submit({**payload, "job_id": uuid.uuid4().hex})
            assert error.value.status == 503
            assert state.get(payload["job_id"])["output"] == output
        else:
            state.submit({**payload, "job_id": uuid.uuid4().hex})
    finally:
        state.close()


@pytest.mark.parametrize(
    "detail,returncode,quarantined",
    [
        ("Scratch allowance exceeded; child processes reaped.", -15, True),
        ("Execution completed; no verifier was requested.", -9, True),
        ("Execution completed; no verifier was requested.", -11, True),
        ("Compilation did not produce a runnable artifact.", -9, False),
    ],
)
def test_gpu_resource_or_signal_interruption_requires_review_unless_compile_only(
    detail: str,
    returncode: int,
    quarantined: bool,
) -> None:
    def executor(*args: Any, **kwargs: Any) -> OperationResult:
        return OperationResult(returncode, "retained diagnostic", False, "failed", detail)

    state = WorkerState("cuda-cpp", executor=executor, ready=True, isolate_jobs=False)
    payload: dict[str, Any] = {
        "job_id": uuid.uuid4().hex,
        "profile": "cuda-cpp",
        "operation": "execute",
        "source": "int main() { return 0; }",
        "language": "cpp",
        "timeout_seconds": 15,
        "verification_id": None,
    }
    try:
        state.submit(payload)
        assert state.thread is not None
        state.thread.join(timeout=3)
        assert not state.thread.is_alive()
        receipt = state.get(payload["job_id"])
        assert receipt["returncode"] == returncode
        assert receipt["output"] == "retained diagnostic"
        assert state.ready is not quarantined
        if quarantined:
            with pytest.raises(WorkerRequestError, match="owner review"):
                state.submit({**payload, "job_id": uuid.uuid4().hex})
    finally:
        state.close()


def test_cpp_probe_reports_device_failure_phase_for_beginner_diagnosis() -> None:
    source = gpu_runtime.CPP_PROBE
    assert "cudaGetErrorString(status)" in source
    assert "CUDA device discovery" in source
    assert "No NVIDIA CUDA device is visible" in source
    assert "CUDA readback did not match the expected result" in source


@pytest.mark.parametrize("profile", sorted(gpu_runtime.GPU_PROFILES))
def test_successful_error_explanation_does_not_quarantine_gpu_worker(profile: str) -> None:
    explanation = (
        "Examples to recognize: illegal memory access; device-side assert; "
        "unspecified launch failure; context is destroyed; cudaErrorIllegalAddress.\n"
        "This program explained diagnostics and completed successfully.\n"
    )

    def executor(*args: Any, **kwargs: Any) -> OperationResult:
        return OperationResult(0, explanation, False, "succeeded", "Execution completed.")

    state = WorkerState(profile, executor=executor, ready=True, isolate_jobs=False)
    job_id = uuid.uuid4().hex
    payload: dict[str, Any] = {
        "job_id": job_id,
        "profile": profile,
        "operation": "execute",
        "source": "# A successful diagnostic-teaching program",
        "language": worker_operations.PROFILES[profile].language,
        "timeout_seconds": 15,
        "verification_id": None,
    }
    try:
        state.submit(payload)
        assert state.thread is not None
        state.thread.join(timeout=3)
        assert not state.thread.is_alive()
        receipt = state.get(job_id)
        assert receipt["status"] == "succeeded" and receipt["returncode"] == 0
        assert receipt["output"] == explanation
        assert state.ready is True
        # The learner can submit the next exercise without an unnecessary restart.
        next_job_id = uuid.uuid4().hex
        state.submit({**payload, "job_id": next_job_id})
        assert state.thread is not None
        state.thread.join(timeout=3)
        assert not state.thread.is_alive()
        assert state.get(next_job_id)["status"] == "succeeded"
        assert state.get(job_id)["output"] == explanation
    finally:
        state.close()
