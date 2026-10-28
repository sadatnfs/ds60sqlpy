"""Fixed, bounded operations for the optional personal-learning workers.

These adapters execute trusted learner code. A worker is not a hostile-code
sandbox. Images, resource limits and network access belong to the host launcher.
"""

from __future__ import annotations

import contextlib
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Any

MAX_SOURCE_BYTES = 262_144
MAX_OUTPUT_BYTES = 128_000
MAX_SCRATCH_BYTES = 32 * 1024 * 1024
MAX_SCRATCH_FILES = 1024
TIMEOUTS = (15, 60, 120)


@dataclass(frozen=True)
class WorkerProfile:
    id: str
    language: str
    filename: str
    verification_ids: tuple[str, ...] = ()


PROFILES = {
    "dbt-duckdb": WorkerProfile("dbt-duckdb", "sql", "model.sql"),
    "data-engineering": WorkerProfile("data-engineering", "python", "main.py"),
    "data-platforms-python": WorkerProfile("data-platforms-python", "python", "main.py"),
    "stan-cpu": WorkerProfile("stan-cpu", "stan", "main.stan"),
    "julia": WorkerProfile("julia", "julia", "main.jl"),
    "jax-cpu": WorkerProfile("jax-cpu", "python", "main.py"),
    "bayesian-cpu": WorkerProfile("bayesian-cpu", "python", "main.py"),
    "r-statistics": WorkerProfile("r-statistics", "r", "main.R"),
    "python-core": WorkerProfile("python-core", "python", "main.py", ("llm-causal-attention-v1",)),
    "tensorflow-cpu": WorkerProfile("tensorflow-cpu", "python", "main.py", ("tf-gradient-v1",)),
    "llm-torch-cpu": WorkerProfile(
        "llm-torch-cpu", "python", "main.py", ("llm-causal-attention-v1",)
    ),
    "c17": WorkerProfile("c17", "c", "main.c"),
    "go": WorkerProfile("go", "go", "main.go"),
    "csharp-dotnet": WorkerProfile("csharp-dotnet", "csharp", "Program.cs"),
    "rust-stable": WorkerProfile("rust-stable", "rust", "main.rs"),
    "swift-linux": WorkerProfile("swift-linux", "swift", "main.swift"),
    "java21": WorkerProfile("java21", "java", "Main.java"),
    "javascript-node": WorkerProfile("javascript-node", "javascript", "main.mjs"),
    "typescript-node": WorkerProfile("typescript-node", "typescript", "main.mts"),
    "cpp20": WorkerProfile("cpp20", "cpp", "main.cpp", ("cpp-ownership-v1",)),
    "php-cli": WorkerProfile("php-cli", "php", "main.php"),
    "cuda-cpp": WorkerProfile("cuda-cpp", "cpp", "main.cu"),
    "cuda-python": WorkerProfile("cuda-python", "python", "main.py"),
    "pytorch-cuda": WorkerProfile("pytorch-cuda", "python", "main.py"),
    "tensorflow-cuda": WorkerProfile("tensorflow-cuda", "python", "main.py"),
    "k8s-kind": WorkerProfile("k8s-kind", "yaml", "lesson.yaml", ("k8s-readiness-v1",)),
    "scala-jvm": WorkerProfile("scala-jvm", "scala", "Main.scala"),
    "spark-local-scala": WorkerProfile(
        "spark-local-scala", "scala", "Main.scala", ("spark-rows-v1",)
    ),
    "spark-local-python": WorkerProfile(
        "spark-local-python", "python", "main.py", ("spark-rows-v1",)
    ),
}


@dataclass
class OperationResult:
    returncode: int | None
    output: str
    truncated: bool
    status: str
    detail: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)


class BoundedOutput:
    """Retain a bounded UTF-8 head and tail from ordered child output."""

    def __init__(
        self, limit: int = MAX_OUTPUT_BYTES, observer: Callable[[str, bool], None] | None = None
    ) -> None:
        self.limit = limit
        self._head = bytearray()
        self._tail = bytearray()
        self._total = 0
        self._lock = threading.Lock()
        self.observer = observer

    def append(self, data: bytes) -> None:
        with self._lock:
            self._total += len(data)
            half = self.limit // 2
            missing = max(0, half - len(self._head))
            self._head.extend(data[:missing])
            self._tail.extend(data[missing:])
            if len(self._tail) > self.limit - half:
                del self._tail[: len(self._tail) - (self.limit - half)]
        if self.observer is not None:
            self.observer(*self.snapshot())

    def snapshot(self) -> tuple[str, bool]:
        with self._lock:
            truncated = self._total > self.limit
            separator = b"\n[output truncated; final output follows]\n" if truncated else b""
            # Leave room for the notice within the advertised byte bound.
            head = bytes(self._head)
            if truncated:
                head = head[: max(0, len(head) - len(separator))]
            data = head + separator + bytes(self._tail)
            text = data.decode("utf-8", errors="replace")
            encoded = text.encode("utf-8")
            if len(encoded) > self.limit:
                truncated = True
                separator = b"\n[output truncated; final output follows]\n"
                half = max(0, (self.limit - len(separator)) // 2)
                text = (
                    encoded[:half].decode("utf-8", errors="ignore")
                    + separator.decode()
                    + encoded[-half:].decode("utf-8", errors="ignore")
                )
            return text, truncated


def child_environment(
    directory: Path, base: Mapping[str, str] | None = None, *, profile_id: str | None = None
) -> dict[str, str]:
    """Do not pass service tokens, database credentials or cloud settings to code."""

    supplied = os.environ if base is None else base
    allowed = ("PATH", "JAVA_HOME", "SPARK_HOME", "LD_LIBRARY_PATH", "SYSTEMROOT", "WINDIR")
    environment = {key: supplied[key] for key in allowed if key in supplied}
    environment.update(
        HOME=str(directory),
        TMPDIR=str(directory),
        TEMP=str(directory),
        TMP=str(directory),
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONUNBUFFERED="1",
        PYTHONNOUSERSITE="1",
        CGO_ENABLED="0",
        GOMAXPROCS="2",
        GOTOOLCHAIN="local",
        GOPROXY="off",
        GOSUMDB="off",
        RUSTUP_HOME="/usr/local/rustup",
        RUSTUP_TOOLCHAIN="1.99.1",
        CARGO_NET_OFFLINE="true",
        DOTNET_CLI_HOME=str(directory / "dotnet-home"),
        DOTNET_CLI_TELEMETRY_OPTOUT="1",
        DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1",
        DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE="1",
        DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER="1",
        DOTNET_NOLOGO="1",
        NUGET_PACKAGES=str(directory / "nuget"),
        PYTHONPATH=str(Path(__file__).resolve().parent.parent),
        MPLBACKEND="Agg",
        MPLCONFIGDIR=str(directory / "matplotlib"),
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
        HF_DATASETS_OFFLINE="1",
        HF_HOME=str(directory / "huggingface"),
        TOKENIZERS_PARALLELISM="false",
        UV_THREADPOOL_SIZE="2",
        MLFLOW_DISABLE_AGENT_HINT="1",
        MLFLOW_ENABLE_TELEMETRY="false",
        FEAST_USAGE="False",
        DBT_SEND_ANONYMOUS_USAGE_STATS="false",
        DO_NOT_TRACK="true",
        POLARS_MAX_THREADS="2",
        TOKIO_WORKER_THREADS="2",
        RAYON_NUM_THREADS="2",
        NUMEXPR_NUM_THREADS="2",
        CUDA_VISIBLE_DEVICES="",
        OMP_NUM_THREADS="2",
        OPENBLAS_NUM_THREADS="2",
        MKL_NUM_THREADS="2",
        TF_NUM_INTRAOP_THREADS="2",
        TF_NUM_INTEROP_THREADS="1",
        SPARK_LOCAL_IP="127.0.0.1",
        JAVA_TOOL_OPTIONS=(
            "-XX:ActiveProcessorCount=2 -XX:ParallelGCThreads=2 -XX:ConcGCThreads=1"
        ),
        PYSPARK_PYTHON=sys.executable,
        PYSPARK_DRIVER_PYTHON=sys.executable,
    )
    if profile_id == "julia":
        environment.update(
            JULIA_DEPOT_PATH="/opt/julia-depot",
            JULIA_LOAD_PATH="/opt/julia-env:@stdlib",
            JULIA_PKG_OFFLINE="true",
            JULIA_CPU_TARGET="generic",
            JULIA_NUM_THREADS="2",
        )
    if profile_id == "stan-cpu":
        environment.update(STAN_NUM_THREADS="1", MAKEFLAGS="-j1")
    if profile_id == "jax-cpu":
        environment.update(JAX_PLATFORMS="cpu", XLA_FLAGS="--xla_cpu_multi_thread_eigen=false")
    if profile_id == "bayesian-cpu":
        environment.update(
            PYTENSOR_FLAGS=f"compiledir={directory / 'pytensor'},blas__ldflags=",
            NUMBA_NUM_THREADS="2",
        )
    if profile_id in {"cuda-cpp", "cuda-python", "pytorch-cuda", "tensorflow-cuda"}:
        environment.update(
            CUDA_VISIBLE_DEVICES="0",
            CUDA_CACHE_PATH=str(directory / "cuda-cache"),
            CUPY_CACHE_DIR=str(directory / "cupy-cache"),
            NUMBA_CACHE_DIR=str(directory / "numba-cache"),
            TF_FORCE_GPU_ALLOW_GROWTH="true",
        )
    return environment


# The wrapper sets limits before exec, without unsafe preexec_fn in a threaded
# HTTP process. All actual argv values are selected by the adapter below.
_LIMIT_EXEC = """
import os, resource, sys
resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
file_limit = int(os.environ.pop("_DS60_FILE_LIMIT_BYTES", "33554432"))
if file_limit not in (33554432, 67108864):
    raise SystemExit("Invalid internal file limit")
resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
resource.setrlimit(resource.RLIMIT_NOFILE, (1024, 1024))
if os.environ.pop("_DS60_DROP_USER", "0") == "1":
    os.setgroups([])
    os.setgid(65534)
    os.setuid(65534)
os.execvpe(sys.argv[1], sys.argv[1:], os.environ)
"""


def _signal_group(process_group: int, sig: int) -> None:
    if sys.platform == "win32":
        raise RuntimeError("Process-group signaling requires a POSIX runtime.")
    try:
        os.killpg(process_group, sig)
    except ProcessLookupError:
        return
    except PermissionError:
        if sys.platform != "darwin":
            raise
        # Darwin can refuse a signal to an orphan group containing only zombies.
        # Confirm every remaining member is terminal; never hide a live cleanup
        # failure or treat an inaccessible process listing as proof of cleanup.
        listing = subprocess.run(
            ["ps", "-axo", "pgid=,stat="], capture_output=True, text=True, timeout=2, check=True
        )
        members = [
            line.split()[1]
            for line in listing.stdout.splitlines()
            if len(line.split()) == 2 and line.split()[0] == str(process_group)
        ]
        if any(not state.startswith("Z") for state in members):
            raise


def _stop_tree(process: subprocess.Popen[bytes], *, isolated: bool = False) -> None:
    if sys.platform != "win32":
        _signal_group(process.pid, signal.SIGTERM)
        with contextlib.suppress(subprocess.TimeoutExpired):
            process.wait(timeout=0.25)
        # Reap descendants even if the process-group leader has already exited.
        _signal_group(process.pid, signal.SIGKILL)
    else:
        process.kill()
    if isolated and sys.platform == "linux":
        # One active job, a private container PID namespace, and a fixed job UID
        # let us reap a child that called setsid() to leave its original group.
        for entry in Path("/proc").iterdir():
            if not entry.name.isdecimal():
                continue
            try:
                if entry.stat().st_uid == 65534:
                    os.kill(int(entry.name), signal.SIGKILL)
            except (ProcessLookupError, FileNotFoundError):
                pass
    with contextlib.suppress(subprocess.TimeoutExpired):
        process.wait(timeout=2)


def _scratch_size(directory: Path) -> tuple[int, int]:
    size = 0
    count = 0
    for current, dirs, files in os.walk(directory, followlinks=False):
        dirs[:] = [name for name in dirs if not (Path(current) / name).is_symlink()]
        for name in files:
            path = Path(current) / name
            try:
                info = path.lstat()
            except FileNotFoundError:
                continue
            count += 1
            size += info.st_size
            if size > MAX_SCRATCH_BYTES or count > MAX_SCRATCH_FILES:
                return size, count
    return size, count


def run_process(
    argv: list[str],
    directory: Path,
    environment: dict[str, str],
    deadline: float,
    cancel: threading.Event,
    output: BoundedOutput,
    *,
    file_limit_bytes: int = MAX_SCRATCH_BYTES,
) -> tuple[int | None, str | None]:
    """Run fixed argv, drain output and terminate the complete owned process group."""

    if file_limit_bytes not in (MAX_SCRATCH_BYTES, MAX_SCRATCH_BYTES * 2):
        raise ValueError("Choose a reviewed process file limit.")
    process_environment = {**environment, "_DS60_FILE_LIMIT_BYTES": str(file_limit_bytes)}
    if cancel.is_set():
        return None, "cancelled"
    if time.monotonic() >= deadline:
        return None, "timed_out"
    command = [sys.executable, "-c", _LIMIT_EXEC, *argv] if os.name == "posix" else argv
    try:
        process = subprocess.Popen(
            command,
            cwd=directory,
            env=process_environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            # One pipe preserves write order. Independent readers could consume
            # buffered stdout after final stderr and evict the diagnostic tail.
            stderr=subprocess.STDOUT,
            start_new_session=os.name == "posix",
        )
    except OSError as exc:
        output.append(f"Backend could not start: {type(exc).__name__}\n".encode())
        return 127, None

    def drain(pipe: Any) -> None:
        try:
            while data := pipe.read1(8192):
                output.append(data)
        except (OSError, ValueError):
            pass
        finally:
            pipe.close()

    readers: list[threading.Thread] = []
    interrupted = None
    try:
        if process.stdout is None:
            raise RuntimeError("The child output pipe was not created.")
        readers = [threading.Thread(target=drain, args=(process.stdout,), daemon=True)]
        for reader in readers:
            reader.start()
        while process.poll() is None:
            if cancel.is_set():
                interrupted = "cancelled"
                break
            if time.monotonic() >= deadline:
                interrupted = "timed_out"
                break
            size, count = _scratch_size(directory)
            if size > MAX_SCRATCH_BYTES or count > MAX_SCRATCH_FILES:
                output.append(b"\nJob exceeded its 32 MiB / 1024-file scratch allowance.\n")
                interrupted = "failed"
                break
            cancel.wait(0.04)
    except RuntimeError:
        output.append(b"\nOutput monitoring could not start; stopping the owned job.\n")
        interrupted = "failed"
    finally:
        try:
            _stop_tree(process, isolated=environment.get("_DS60_DROP_USER") == "1")
        finally:
            for reader in readers:
                if reader.ident is not None:
                    reader.join(timeout=2)
            for pipe, reader in zip((process.stdout,), readers, strict=False):
                if pipe is not None and (reader.ident is None or not reader.is_alive()):
                    pipe.close()
        if any(reader.is_alive() for reader in readers):
            raise RuntimeError("Output cleanup did not confirm descendant termination.")
    size, count = _scratch_size(directory)
    if interrupted is None and (size > MAX_SCRATCH_BYTES or count > MAX_SCRATCH_FILES):
        output.append(b"\nJob exceeded its scratch allowance.\n")
        interrupted = "failed"
    return process.returncode, interrupted


def _compiler() -> str | None:
    return shutil.which("g++") or shutil.which("clang++")


def _scala_jars() -> list[Path]:
    spark = Path(os.environ.get("SPARK_HOME", "/opt/spark"))
    return sorted((spark / "jars").glob("*.jar"))


def _scala_compile(directory: Path, sources: list[str], spark: bool) -> list[str]:
    if spark or _scala_jars():
        jars = _scala_jars()
        classpath = os.pathsep.join(str(path) for path in jars)
        return [
            "java",
            "-Xmx768m",
            "-cp",
            classpath,
            "scala.tools.nsc.Main",
            "-usejavacp",
            "-d",
            str(directory / "classes"),
            *sources,
        ]
    return ["/opt/scala/bin/scalac", "-J-Xmx512m", "-d", str(directory / "classes"), *sources]


def _fixture_path(track: str, filename: str) -> Path:
    path = Path(__file__).resolve().parents[2] / "courses" / track / "fixtures" / filename
    if not path.is_file():
        raise ValueError(
            "The immutable registered verifier fixture is missing; rebuild this profile."
        )
    return path


def _python_verifier(verification_id: str) -> str:
    return (
        "import runpy\n"
        "from pathlib import Path\n"
        "from ds60sqlpy.worker_operations import verify_python_namespace\n"
        "namespace = runpy.run_path('main.py', run_name='__main__')\n"
        f"verify_python_namespace(namespace, {verification_id!r}, Path('checks.json'))\n"
    )


def _numeric_field_close(result: Any, key: str, expected: float) -> bool:
    import math

    actual = float(result[key])
    return math.isfinite(actual) and math.isclose(actual, expected, rel_tol=0, abs_tol=1e-12)


def _raises(function: Any, args: tuple[Any, ...], kwargs: dict[str, Any], name: str) -> bool:
    if not callable(function):
        return False
    try:
        function(*args, **kwargs)
    except Exception as exc:
        return type(exc).__name__ == name
    return False


def _write_checks(path: Path, checks: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps({"checks": checks}), encoding="utf-8")


def verify_python_namespace(namespace: dict[str, Any], verification_id: str, path: Path) -> None:
    """Execute typed, fixed numeric checks. Source output is never the oracle."""

    import numpy as np

    checks: list[dict[str, Any]] = []

    def check(name: str, function: Callable[[], bool], detail: str) -> None:
        try:
            passed = bool(function())
        except Exception as exc:
            passed = False
            detail = f"{detail} ({type(exc).__name__})"
        checks.append({"name": name, "passed": passed, "detail": detail})

    if verification_id == "tf-gradient-v1":
        fixture = json.loads(
            _fixture_path("deep-learning-tensorflow", "tf-gradient-v1.json").read_text()
        )
        function: Any = namespace.get("gradient_step")
        for index, case in enumerate(fixture["cases"]):
            try:
                result = function(**case["kwargs"]) if callable(function) else {}
            except Exception:
                result = {}
            for key, value in case["expected"].items():
                check(
                    f"case-{index + 1}-{key}",
                    partial(_numeric_field_close, result, key, float(value)),
                    "Fixed float64 gradient-step value.",
                )
        for index, case in enumerate(fixture["negative_cases"]):
            check(
                f"invalid-rate-{index + 1}",
                partial(_raises, function, (), case["kwargs"], case["exception"]),
                "Invalid learning-rate contract is enforced.",
            )
    elif verification_id == "llm-causal-attention-v1":
        fixture = json.loads(
            _fixture_path("llm-theory", "llm-causal-attention-v1.json").read_text()
        )
        function = namespace.get("attention")
        q, k, v = [np.array(fixture[name], dtype=np.float64) for name in ("q", "k", "v")]
        allowed = np.array(fixture["allowed"], dtype=bool)
        try:
            output, weights = function(q, k, v, allowed) if callable(function) else (None, None)
        except Exception:
            output, weights = None, None

        def close(actual: Any, expected: Any) -> bool:
            return np.shape(actual) == np.shape(expected) and bool(
                np.allclose(actual, expected, rtol=0, atol=1e-12)
            )

        check(
            "weights",
            lambda: close(weights, fixture["expected_weights"]),
            "Causal scaled-softmax values match the immutable numeric oracle.",
        )
        check(
            "output",
            lambda: close(output, fixture["expected_output"]),
            "Weighted values match the immutable numeric oracle.",
        )
        check(
            "masked-zero",
            lambda: bool(np.all(np.asarray(weights)[~allowed] == 0)),
            "Forbidden future positions have zero weight.",
        )

        def future() -> bool:
            actual, _ = function(q, k, np.array(fixture["future_v"], dtype=float), allowed)
            return close(actual, fixture["expected_future_output"])

        check("future-perturbation", future, "Changing future values preserves earlier outputs.")
        for case in fixture.get("cases", []):

            def run_case(c: dict[str, Any] = case) -> bool:
                actual_output, actual_weights = function(
                    *(np.array(c[name], dtype=np.float64) for name in ("q", "k", "v")),
                    np.array(c["allowed"], dtype=bool),
                )
                return close(actual_output, c["expected_output"]) and close(
                    actual_weights, c["expected_weights"]
                )

            check(
                case["name"],
                run_case,
                "Independent nonuniform/prefix oracle checks Q/K, scaling, axis and causality.",
            )
        bad_row = allowed.copy()
        bad_row[1] = False
        bad_v = v.copy()
        bad_v[0, 0] = np.nan
        cases = [
            ((q, k, v, allowed.astype(int)), "TypeError"),
            ((q, k, v, allowed[:, :2]), "ValueError"),
            ((q, k, v, bad_row), "ValueError"),
            ((q[:0], k[:0], v[:0], allowed[:0, :0]), "ValueError"),
            ((q, k, bad_v, allowed), "ValueError"),
        ]
        for index, (args, exception) in enumerate(cases):
            check(
                f"invalid-input-{index + 1}",
                partial(_raises, function, args, {}, exception),
                fixture["negative_cases"][index]["name"],
            )
    else:
        raise ValueError("Unsupported Python verification operation.")
    _write_checks(path, checks)
    if not all(item["passed"] for item in checks):
        raise SystemExit(1)


def _read_checks(directory: Path) -> list[dict[str, Any]]:
    path = directory / "checks.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 32_768:
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        checks = value["checks"]
        if not isinstance(checks, list) or not 1 <= len(checks) <= 64:
            return []
        for item in checks:
            if (
                not isinstance(item, dict)
                or set(item) != {"name", "passed", "detail"}
                or not isinstance(item["name"], str)
                or type(item["passed"]) is not bool
                or not isinstance(item["detail"], str)
                or len(item["name"]) > 100
                or len(item["detail"]) > 1000
            ):
                return []
        return checks
    except (ValueError, KeyError, OSError, TypeError):
        return []


def validate_operation(profile_id: str, language: str, verification_id: str | None) -> None:
    profile = PROFILES.get(profile_id)
    if profile is None:
        raise ValueError("Unknown worker profile.")
    if language != profile.language:
        raise ValueError("Language does not match the selected worker profile.")
    if verification_id is not None and verification_id not in profile.verification_ids:
        raise ValueError("Verification operation is not registered for this profile.")


def language_commands(profile_id: str, directory: Path) -> tuple[list[list[str]], list[str]]:
    """Reviewed single-source toolchains; source cannot supply build flags or packages."""
    node = ["node", "--unhandled-rejections=strict", "--max-old-space-size=256"]
    if profile_id == "dbt-duckdb":
        return [], [sys.executable, "-u", "-m", "ds60sqlpy.dbt_runner"]
    if profile_id == "stan-cpu":
        return [["make", "--no-print-directory", "-C", "/opt/cmdstan", str(directory / "main")]], [
            sys.executable,
            "-u",
            "-m",
            "ds60sqlpy.stan_runner",
        ]
    if profile_id == "julia":
        return [], [
            "julia",
            "--startup-file=no",
            "--history-file=no",
            "--color=no",
            "--compiled-modules=existing",
            "--project=/opt/julia-env",
            "--threads=2",
            "-L",
            "/opt/worker/worker_figures.jl",
            "main.jl",
        ]
    if profile_id == "r-statistics":
        return [], ["Rscript", "--vanilla", str(Path(__file__).with_name("worker_figures.R"))]
    if profile_id == "php-cli":
        flags = [
            "php",
            "-d",
            "display_errors=stderr",
            "-d",
            "log_errors=0",
            "-d",
            "memory_limit=128M",
            "-d",
            "zend.assertions=1",
            "-d",
            "assert.exception=1",
            "-d",
            "allow_url_fopen=0",
        ]
        return [[*flags, "-l", "main.php"]], [*flags, "main.php"]
    if profile_id == "c17":
        return [
            [
                "gcc",
                "-std=c17",
                "-O0",
                "-g",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-pthread",
                "main.c",
                "-lm",
                "-o",
                "program",
            ]
        ], [str(directory / "program")]
    if profile_id == "go":
        # The immutable import configuration and compiled standard library are
        # prepared in the image. Each job only compiles its own single source.
        config = "/opt/course-go/importcfg"
        return [
            [
                "go",
                "tool",
                "compile",
                "-importcfg",
                config,
                "-p",
                "main",
                "-o",
                "main.a",
                "main.go",
            ],
            ["go", "tool", "link", "-importcfg", config, "-o", "program", "main.a"],
        ], [str(directory / "program")]
    if profile_id == "rust-stable":
        return [
            [
                "rustc",
                "--edition=2024",
                "-C",
                "debuginfo=0",
                "-L",
                "dependency=/opt/course-rust/target/release/deps",
                "--extern",
                "arrow=/opt/course-rust/libarrow.rlib",
                "main.rs",
                "-o",
                "program",
            ]
        ], [str(directory / "program")]
    if profile_id == "swift-linux":
        return [
            [
                "swiftc",
                "-parse-as-library",
                "-swift-version",
                "6",
                "-module-cache-path",
                str(directory / "swift-module-cache"),
                "main.swift",
                "-o",
                "program",
            ]
        ], [str(directory / "program")]
    if profile_id == "csharp-dotnet":
        # The trusted project is immutable and admits only Program.cs. Offline
        # NuGet sources and disabled build servers keep every attempt bounded.
        project = Path("/opt/course-dotnet/Lesson.csproj").read_text(encoding="utf-8")
        (directory / "Lesson.csproj").write_text(project, encoding="utf-8")
        return [
            [
                "dotnet",
                "build",
                "Lesson.csproj",
                "--configfile",
                "/opt/course-dotnet/NuGet.Config",
                "--disable-build-servers",
                "--nologo",
                "--verbosity",
                "quiet",
                "-p:UseSharedCompilation=false",
                "-o",
                "compiled",
            ]
        ], ["dotnet", str(directory / "compiled/Lesson.dll")]
    if profile_id == "java21":
        library = "/opt/course-libs/h2-2.5.252.jar"
        (directory / "classes").mkdir(mode=0o755, exist_ok=True)
        return (
            [
                [
                    "javac",
                    "-encoding",
                    "UTF-8",
                    "-Xlint:all",
                    "--release",
                    "21",
                    "-cp",
                    library,
                    "-d",
                    "classes",
                    "Main.java",
                ]
            ],
            ["java", "-ea", "-Xmx512m", "-cp", os.pathsep.join(["classes", library]), "Main"],
        )
    if profile_id == "javascript-node":
        return [], [*node, "main.mjs"]
    if profile_id == "typescript-node":
        (directory / "compiled").mkdir(mode=0o755, exist_ok=True)
        return (
            [
                [
                    "node",
                    "/opt/typescript/node_modules/typescript/bin/tsc",
                    "--target",
                    "ES2022",
                    "--module",
                    "NodeNext",
                    "--moduleResolution",
                    "NodeNext",
                    "--strict",
                    "--noEmitOnError",
                    "--skipLibCheck",
                    "--types",
                    "node",
                    "--typeRoots",
                    "/opt/typescript/node_modules/@types",
                    "--outDir",
                    "compiled",
                    "main.mts",
                ]
            ],
            [*node, "compiled/main.mjs"],
        )
    raise ValueError("No fixed single-source toolchain for this profile.")


def probe_profile(profile_id: str, *, isolate_user: bool = False) -> tuple[bool, str]:
    """Execute one fixed startup smoke under a 45-second total deadline.

    HTTP health uses the cached result; it does not re-import frameworks or
    start a Spark JVM on every poll.
    """
    import tempfile

    if profile_id not in PROFILES:
        return False, "Unknown worker profile."
    if profile_id == "k8s-kind":
        return False, "Prepare an owned Kubernetes lease and its dedicated adapter first."
    assets = {
        "go": "/opt/course-go/importcfg",
        "rust-stable": "/opt/course-rust/libarrow.rlib",
        "csharp-dotnet": "/opt/course-dotnet/Lesson.csproj",
    }
    if profile_id in assets and not Path(assets[profile_id]).is_file():
        return False, "The prepared language runtime assets are missing."
    with tempfile.TemporaryDirectory(prefix="ds60-worker-probe-") as temporary:
        directory = Path(temporary)
        commands: list[list[str]]
        if profile_id in {"cuda-cpp", "cuda-python", "pytorch-cuda", "tensorflow-cuda"}:
            from ds60sqlpy.gpu_runtime import probe_commands

            commands = probe_commands(profile_id, directory)
        elif profile_id == "stan-cpu":
            commands = [
                ["/opt/cmdstan/bin/stanc", "--version"],
                [
                    "/opt/cmdstan/probe",
                    "sample",
                    "num_warmup=10",
                    "num_samples=10",
                    "random",
                    "seed=17",
                    "output",
                    "file=probe.csv",
                    "refresh=0",
                ],
                [
                    sys.executable,
                    "-c",
                    (
                        "import csv,math; "
                        "r=list(csv.DictReader(x for x in open('probe.csv') "
                        "if not x.startswith('#'))); "
                        "assert len(r)==10 and all(math.isfinite(float(x['mu'])) for x in r); "
                        "print('Stan sampler ready')"
                    ),
                ],
            ]
        elif profile_id == "julia":
            commands = [
                [
                    "julia",
                    "--startup-file=no",
                    "--compiled-modules=existing",
                    "--project=/opt/julia-env",
                    "-e",
                    (
                        "using LinearAlgebra, DataFrames, ForwardDiff, JSON3; "
                        "@assert sum([20,22])==42; "
                        "@assert ForwardDiff.derivative(x->x*x,3.0)==6.0; println(VERSION)"
                    ),
                ]
            ]
        elif profile_id == "dbt-duckdb":
            (directory / "model.sql").write_text("select 42 as answer\n", encoding="utf-8")
            commands = [[sys.executable, "-u", "-m", "ds60sqlpy.dbt_runner"]]
        elif profile_id == "data-platforms-python":
            commands = [
                [
                    sys.executable,
                    "-c",
                    (
                        "from pathlib import Path\n"
                        "import pyarrow as pa\n"
                        "from datafusion import SessionContext\n"
                        "from pyiceberg.catalog.sql import SqlCatalog\n"
                        "from pyiceberg.schema import Schema\n"
                        "from pyiceberg.types import NestedField, LongType\n"
                        "ctx=SessionContext()\n"
                        "batch=pa.record_batch({'n':[20,22]})\n"
                        "ctx.register_record_batches('numbers', [[batch]])\n"
                        "rows=ctx.sql('select sum(n) as n from numbers').collect()\n"
                        "assert pa.Table.from_batches(rows).to_pylist()==[{'n':42}]\n"
                        "root=Path.cwd()\n"
                        "catalog=SqlCatalog('probe',uri='sqlite:///'+str(root/'catalog.sqlite'),warehouse=(root/'warehouse').as_uri())\n"
                        "catalog.create_namespace('probe')\n"
                        "table=catalog.create_table('probe.numbers',schema=Schema(NestedField(1,'n',LongType(),required=False)))\n"
                        "table.append(pa.table({'n':pa.array([42],type=pa.int64())}))\n"
                        "assert table.scan().to_arrow().to_pylist()==[{'n':42}]\n"
                        "print('Arrow, DataFusion and Iceberg ready')\n"
                    ),
                ]
            ]
        elif profile_id == "data-engineering":
            commands = [
                [
                    sys.executable,
                    "-c",
                    (
                        "import polars as pl, duckdb, feast, mlflow, skops.io; "
                        "from dbt.cli.main import dbtRunner; "
                        "assert pl.DataFrame({'x':[20,22]}).select(pl.col('x').sum()).item()==42; "
                        "assert duckdb.sql('select 42').fetchall()[0][0]==42; "
                        "print('Data engineering ready')"
                    ),
                ]
            ]
        elif profile_id == "cpp20":
            compiler = _compiler()
            if compiler is None:
                return False, "The registered C++ compiler is missing."
            (directory / "probe.cpp").write_text(
                "#include <span>\n#include <array>\nint main(){std::array<int,2> a{20,22};"
                "std::span<int> s(a);return s[0]+s[1]==42?0:1;}\n"
            )
            commands = [
                [compiler, "-std=c++20", "-pthread", "probe.cpp", "-o", "probe"],
                [str(directory / "probe")],
            ]
        elif profile_id in {
            "c17",
            "go",
            "csharp-dotnet",
            "rust-stable",
            "swift-linux",
            "java21",
            "javascript-node",
            "typescript-node",
            "php-cli",
            "r-statistics",
        }:
            smoke = {
                "r-statistics": (
                    "stopifnot(sum(c(20,22)) == 42); "
                    "invisible(lapply(c('ggplot2','plotly','R6','S7','jsonlite'), loadNamespace)); "
                    "cat('R statistics ready\\n')"
                ),
                "php-cli": (
                    "<?php declare(strict_types=1); $db = new PDO('sqlite::memory:'); "
                    "assert((int)$db->query('SELECT 42')->fetchColumn() === 42); echo '42';\n"
                ),
                "c17": (
                    "#include <assert.h>\n#include <stdio.h>\n"
                    'int main(void){assert(20+22==42);puts("42");return 0;}\n'
                ),
                "go": (
                    'package main\nimport "fmt"\n'
                    'func main(){if 20+22!=42{panic("sum")};fmt.Println(42)}\n'
                ),
                "csharp-dotnet": (
                    'if (20+22 != 42) throw new Exception("sum"); Console.WriteLine(42);\n'
                ),
                "rust-stable": (
                    "use arrow::array::{Array, Int32Array}; fn main(){"
                    "let a=Int32Array::from(vec![20,22]);assert_eq!(a.len(),2);"
                    'assert_eq!(a.value(0)+a.value(1),42);println!("42");}\n'
                ),
                "swift-linux": (
                    "@main enum Lesson { static func main() {"
                    "precondition(20+22 == 42); print(42) } }\n"
                ),
                "java21": (
                    "public class Main { public static void main(String[] a) { assert "
                    "20+22==42; System.out.println(42); } }\n"
                ),
                "javascript-node": (
                    "import assert from 'node:assert/strict'; assert.equal(20+22,42); "
                    "console.log(42);\n"
                ),
                "typescript-node": (
                    "import assert from 'node:assert/strict'; const n: number = 20+22; "
                    "assert.equal(n,42); console.log(n);\n"
                ),
            }[profile_id]
            (directory / PROFILES[profile_id].filename).write_text(smoke, encoding="utf-8")
            compiling, command = language_commands(profile_id, directory)
            commands = [*compiling, command]
        elif profile_id == "scala-jvm":
            if not _scala_jars():
                return False, "The matched Scala compiler/library jars are missing."
            (directory / "classes").mkdir()
            (directory / "Main.scala").write_text(
                "object Main { def main(args:Array[String]):Unit = { require(20+22==42) } }\n"
            )
            commands = [
                _scala_compile(directory, ["Main.scala"], True),
                [
                    "java",
                    "-Xmx256m",
                    "-cp",
                    os.pathsep.join([str(directory / "classes"), *(str(p) for p in _scala_jars())]),
                    "Main",
                ],
            ]
        elif profile_id.startswith("spark-local"):
            home = Path(os.environ.get("SPARK_HOME", "/opt/spark"))
            if not (home / "bin/spark-submit").is_file() or not _scala_jars():
                return False, "The prepared Spark distribution is missing."
            (directory / "probe.py").write_text(
                "from pyspark.sql import SparkSession\n"
                "s=SparkSession.builder.master('local[2]').config('spark.ui.enabled','false')"
                ".config('spark.driver.host','127.0.0.1')"
                ".config('spark.driver.bindAddress','127.0.0.1').getOrCreate()\n"
                "try:\n assert s.range(1).count()==1\nfinally:\n s.stop()\n"
            )
            commands = [
                [
                    str(home / "bin/spark-submit"),
                    "--master",
                    "local[2]",
                    "--conf",
                    "spark.ui.enabled=false",
                    "--driver-memory",
                    "512m",
                    "probe.py",
                ]
            ]
        else:
            module = {
                "python-core": "numpy",
                "jax-cpu": "jax",
                "bayesian-cpu": "pymc",
                "tensorflow-cpu": "tensorflow",
                "llm-torch-cpu": "torch",
            }[profile_id]
            if importlib.util.find_spec(module) is None:
                return False, f"The prepared {module} package is missing."
            smoke = {
                "jax": (
                    "import jax as m; import jax.numpy as j; "
                    "assert m.default_backend() == 'cpu'; "
                    "x=m.jit(m.grad(lambda v:j.sum(v*v)))(j.array([3.,4.])); "
                    "x.block_until_ready(); assert x.tolist()==[6.,8.]"
                ),
                "pymc": (
                    "import pymc as m; import arviz as az; import numpy as np\n"
                    "with m.Model():\n"
                    " p=m.Beta('p',2,2); m.Binomial('y',n=10,p=p,observed=6)\n"
                    " trace=m.sample(draws=30,tune=30,chains=1,cores=1,random_seed=17,"
                    "progressbar=False,compute_convergence_checks=False)\n"
                    "assert np.isfinite(trace.posterior['p'].values).all()\n"
                ),
                "numpy": "import numpy as m; assert int(m.array([20,22]).sum())==42",
                "tensorflow": (
                    "import tensorflow as m; assert int(m.reduce_sum(m.constant([20,22])))==42"
                ),
                "torch": "import torch as m; assert int(m.tensor([20,22]).sum())==42",
            }[module]
            commands = [[sys.executable, "-c", smoke.rstrip() + "\nprint(m.__version__)"]]
        environment = child_environment(directory, profile_id=profile_id)
        if isolate_user:
            if sys.platform != "linux" or os.geteuid() != 0:
                return False, "A Linux root supervisor is required for the isolated backend probe."
            for path in [directory, *directory.iterdir()]:
                os.chown(path, 65534, 65534)
            environment["_DS60_DROP_USER"] = "1"
        output = BoundedOutput(4096)
        deadline = time.monotonic() + 45
        for position, command in enumerate(commands):
            limits = (
                {"file_limit_bytes": MAX_SCRATCH_BYTES * 2}
                if profile_id == "csharp-dotnet" and position < len(commands) - 1
                else {}
            )
            code, interrupted = run_process(
                command, directory, environment, deadline, threading.Event(), output, **limits
            )
            if code != 0 or interrupted:
                return False, "The fixed backend startup probe failed: " + output.snapshot()[0][
                    -400:
                ]
        return True, f"{profile_id} fixed backend startup smoke passed."


def execute_operation(
    profile_id: str,
    source: str,
    directory: Path,
    timeout_seconds: int,
    cancel: threading.Event,
    on_status: Callable[[str], None],
    verification_id: str | None = None,
    *,
    isolate_user: bool = False,
    on_output: Callable[[str, bool], None] | None = None,
) -> OperationResult:
    profile = PROFILES[profile_id]
    if profile_id == "k8s-kind":
        raise ValueError("Prepare an owned Kubernetes lease and its dedicated adapter first.")
    validate_operation(profile_id, profile.language, verification_id)
    if type(timeout_seconds) is not int or timeout_seconds not in TIMEOUTS:
        raise ValueError("Choose a 15, 60 or 120 second total deadline.")
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError("Source exceeds the 256 KiB limit.")
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    (directory / profile.filename).write_text(source, encoding="utf-8", newline="\n")
    environment = child_environment(directory, profile_id=profile_id)
    if isolate_user:
        if sys.platform != "linux" or os.geteuid() != 0:
            raise ValueError("A Linux root supervisor is required for job identity isolation.")
        os.chown(directory, 65534, 65534)
        for path in directory.iterdir():
            os.chown(path, 65534, 65534)
        environment["_DS60_DROP_USER"] = "1"
    output = BoundedOutput(observer=on_output)
    deadline = time.monotonic() + timeout_seconds
    compiling: list[list[str]] = []
    if profile_id in {"cuda-cpp", "cuda-python", "pytorch-cuda", "tensorflow-cuda"}:
        from ds60sqlpy.gpu_runtime import commands as gpu_commands

        compiling, command = gpu_commands(profile_id, directory)
    elif profile_id == "cpp20":
        compiler = _compiler() or "g++"
        compiling = [
            [
                compiler,
                "-std=c++20",
                "-pthread",
                "-O0",
                "-g",
                "-Wall",
                "-Wextra",
                "-Wconversion",
                "-Wpedantic",
                "main.cpp",
                "-o",
                "program",
            ]
        ]
        command = [str(directory / "program")]
        if verification_id == "cpp-ownership-v1":
            harness = _fixture_path("cpp", "cpp-ownership-v1.cpp")
            flags = [
                compiler,
                "-std=c++20",
                "-pthread",
                "-O0",
                "-g",
                "-Wall",
                "-Wextra",
                "-Wconversion",
                "-Wpedantic",
            ]
            compiling = [
                [*flags, "-Dmain=ds60_learner_main", "-c", "main.cpp", "-o", "learner.o"],
                [*flags, "-c", str(harness), "-o", "verifier.o"],
                [compiler, "-pthread", "learner.o", "verifier.o", "-o", "program"],
            ]
    elif profile_id in {
        "c17",
        "go",
        "csharp-dotnet",
        "rust-stable",
        "swift-linux",
        "java21",
        "javascript-node",
        "typescript-node",
        "php-cli",
        "r-statistics",
        "dbt-duckdb",
        "stan-cpu",
        "julia",
    }:
        compiling, command = language_commands(profile_id, directory)
        if isolate_user:
            for child in directory.iterdir():
                os.chown(child, 65534, 65534)
    elif profile_id in ("scala-jvm", "spark-local-scala"):
        (directory / "classes").mkdir(mode=0o755)
        if isolate_user:
            os.chown(directory / "classes", 65534, 65534)
        sources = ["Main.scala"]
        if verification_id == "spark-rows-v1":
            sources.append(str(_fixture_path("scala-spark", "Ds60Verify.scala")))
        compiling = [_scala_compile(directory, sources, profile_id.startswith("spark"))]
        if profile_id == "scala-jvm":
            classpath = os.pathsep.join(
                [str(directory / "classes"), *(str(p) for p in _scala_jars())]
            )
            command = ["java", "-Xmx512m", "-cp", classpath, "Main"]
        else:
            compiling.append(["jar", "cf", "program.jar", "-C", "classes", "."])
            home = Path(os.environ.get("SPARK_HOME", "/opt/spark"))
            command = [
                str(home / "bin/spark-submit"),
                "--master",
                "local[2]",
                "--conf",
                "spark.ui.enabled=false",
                "--driver-memory",
                "512m",
                "--class",
                "Ds60Verify" if verification_id == "spark-rows-v1" else "Main",
                "program.jar",
            ]
    elif profile_id == "spark-local-python":
        home = Path(os.environ.get("SPARK_HOME", "/opt/spark"))
        command = [
            str(home / "bin/spark-submit"),
            "--master",
            "local[2]",
            "--conf",
            "spark.ui.enabled=false",
            "--driver-memory",
            "512m",
            "main.py",
        ]
        if verification_id == "spark-rows-v1":
            # Stage only the immutable checker. It imports the submitted main.py
            # and creates its own explicit, local-only SparkSession.
            checker = _fixture_path("scala-spark", "verify_spark013.py")
            (directory / "verify_spark.py").write_text(checker.read_text(), encoding="utf-8")
            command[-1] = "verify_spark.py"
    else:
        command = [sys.executable, "-u", "-m", "ds60sqlpy.worker_figures"]
        if verification_id:
            (directory / "verify.py").write_text(
                _python_verifier(verification_id), encoding="utf-8"
            )
            command = [sys.executable, "-u", "verify.py"]
    code: int | None = None
    interrupted = None
    for compile_command in compiling:
        on_status("compiling")
        # Roslyn compilation needs a larger per-file allowance. Keep actual
        # workspace monitoring at 32 MiB and ordinary execution at the original
        # limit; only this trusted compile phase gets 64 MiB.
        limits = (
            {"file_limit_bytes": MAX_SCRATCH_BYTES * 2} if profile_id == "csharp-dotnet" else {}
        )
        code, interrupted = run_process(
            compile_command,
            directory,
            environment,
            min(deadline, time.monotonic() + 60),
            cancel,
            output,
            **limits,
        )
        if interrupted or code != 0:
            text, truncated = output.snapshot()
            return OperationResult(
                code,
                text,
                truncated,
                interrupted or "failed",
                "Compilation did not produce a runnable artifact.",
            )
    on_status("running")
    if verification_id:
        on_status("verifying")
    code, interrupted = run_process(command, directory, environment, deadline, cancel, output)
    checks = _read_checks(directory) if verification_id else []
    if verification_id and not checks:
        checks = [
            {
                "name": verification_id,
                "passed": False,
                "detail": "The registered verifier did not produce a valid check report.",
            }
        ]
    text, truncated = output.snapshot()
    status = interrupted or (
        "succeeded" if code == 0 and all(c["passed"] for c in checks) else "failed"
    )
    detail = (
        "Registered verification completed."
        if verification_id
        else "Execution completed; no verifier was requested."
    )
    if interrupted:
        detail = {
            "cancelled": "Cancelled and child processes reaped.",
            "timed_out": "Total execution deadline exceeded; child processes reaped.",
            "failed": "Scratch allowance exceeded; child processes reaped.",
        }[interrupted]
    from ds60sqlpy.plot_artifacts import read_artifacts

    artifacts, capture_warning = read_artifacts(directory)
    if capture_warning:
        detail += " " + capture_warning
    return OperationResult(code, text, truncated, status, detail, checks, artifacts)
