"""Reference implementation for python-perf-01.

Timings are evidence printed for the current machine. Correctness tests never
assert that an implementation must be faster by a universal threshold.
"""

from __future__ import annotations

import cProfile
import importlib.util
import io
import json
import pstats
import timeit
import tracemalloc
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from statistics import median
from typing import Generic, Literal, TypeVar

T = TypeVar("T")
Decision = Literal[
    "fix-correctness",
    "reduce-memory",
    "reduce-transfer",
    "optimize-hotspot",
    "keep-current",
]
CacheDecision = Literal["cache", "do-not-cache", "measure"]
NativeDecision = Literal["improve-algorithm", "batch-native-boundary", "keep-python", "measure"]


@dataclass(frozen=True)
class BenchmarkPlan:
    warmup_calls: int = 3
    repeats: int = 5
    calls_per_repeat: int = 10

    def __post_init__(self) -> None:
        if self.warmup_calls < 0:
            raise ValueError("warmup_calls must be non-negative")
        if self.repeats < 1 or self.calls_per_repeat < 1:
            raise ValueError("repeats and calls_per_repeat must be positive")


@dataclass(frozen=True)
class TimingReport:
    samples_seconds: tuple[float, ...]
    calls_per_repeat: int
    minimum_seconds: float
    median_seconds: float
    maximum_seconds: float


@dataclass(frozen=True)
class Profiled(Generic[T]):
    result: T
    report: str
    displayed_rows: int


@dataclass(frozen=True)
class MemoryMeasured(Generic[T]):
    result: T
    current_bytes: int
    peak_bytes: int


def benchmark(
    operation: Callable[[], object],
    plan: BenchmarkPlan | None = None,
) -> TimingReport:
    """Warm up and collect repeated ``timeit`` samples."""

    active_plan = BenchmarkPlan() if plan is None else plan
    for _ in range(active_plan.warmup_calls):
        operation()
    timer = timeit.Timer(operation)
    samples = tuple(
        timer.repeat(
            repeat=active_plan.repeats,
            number=active_plan.calls_per_repeat,
        )
    )
    return TimingReport(
        samples_seconds=samples,
        calls_per_repeat=active_plan.calls_per_repeat,
        minimum_seconds=min(samples),
        median_seconds=median(samples),
        maximum_seconds=max(samples),
    )


def profile_call(operation: Callable[[], T], *, rows: int = 8) -> Profiled[T]:
    """Return the value and a cumulative ``cProfile`` text report."""

    if rows < 1:
        raise ValueError("rows must be positive")
    profiler = cProfile.Profile()
    result = profiler.runcall(operation)
    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats("cumulative").print_stats(rows)
    return Profiled(result, stream.getvalue(), rows)


def measure_peak_memory(operation: Callable[[], T]) -> MemoryMeasured[T]:
    """Measure traced Python allocation state for one local operation."""

    if tracemalloc.is_tracing():
        raise RuntimeError("tracemalloc is already active")
    tracemalloc.start()
    try:
        result = operation()
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return MemoryMeasured(result, current, peak)


def first_duplicate_quadratic(values: Sequence[int]) -> int | None:
    """Repeated prefix scans preserve first-second-occurrence semantics."""

    for index, value in enumerate(values):
        if value in values[:index]:
            return value
    return None


def first_duplicate_linear(values: Sequence[int]) -> int | None:
    """Use expected O(n) set membership while preserving the same semantics."""

    seen: set[int] = set()
    for value in values:
        if value in seen:
            return value
        seen.add(value)
    return None


def sum_materialized_squares(values: Sequence[int]) -> int:
    """Allocate an intermediate list before summing."""

    return sum([value * value for value in values])


def sum_streamed_squares(values: Sequence[int]) -> int:
    """Stream values through a generator expression."""

    return sum(value * value for value in values)


def sum_squares_loop(values: Sequence[float]) -> float:
    total = 0.0
    for value in values:
        total += value * value
    return total


def numpy_sum_squares(values: Sequence[float]) -> float:
    """Optional vectorized comparison; package availability is explicit."""

    if importlib.util.find_spec("numpy") is None:
        raise ModuleNotFoundError("NumPy is not installed; use the data profile")
    import numpy as np

    array = np.asarray(values, dtype=np.float64)
    return float(np.square(array).sum())


def serialized_payload_bytes(payload: Mapping[str, Sequence[int]]) -> int:
    """Measure one safe JSON representation used for a process-boundary model."""

    text = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    )
    return len(text.encode("utf-8"))


def estimated_transfer_bytes(
    payload_bytes: int,
    *,
    workers: int,
    copies_per_worker: int,
) -> int:
    if payload_bytes < 0 or workers < 1 or copies_per_worker < 1:
        raise ValueError("payload must be nonnegative and copy counts positive")
    return payload_bytes * workers * copies_per_worker


@lru_cache(maxsize=128)
def cached_fibonacci(number: int) -> int:
    if number < 0:
        raise ValueError("number must be non-negative")
    if number < 2:
        return number
    return cached_fibonacci(number - 1) + cached_fibonacci(number - 2)


def choose_cache_policy(
    *,
    reuse_fraction: float,
    estimated_entries: int,
    bytes_per_entry: int,
    memory_budget_bytes: int,
    freshness_required: bool,
) -> CacheDecision:
    if not 0 <= reuse_fraction <= 1:
        raise ValueError("reuse_fraction must be between zero and one")
    if min(estimated_entries, bytes_per_entry, memory_budget_bytes) < 0:
        raise ValueError("memory values must be non-negative")
    if freshness_required or estimated_entries * bytes_per_entry > memory_budget_bytes:
        return "do-not-cache"
    if reuse_fraction >= 0.5:
        return "cache"
    return "measure"


def choose_native_boundary(
    *,
    hotspot_fraction: float,
    calls_across_boundary: int,
    transfer_bytes: int,
    algorithm_improvement_available: bool,
) -> NativeDecision:
    if not 0 <= hotspot_fraction <= 1:
        raise ValueError("hotspot_fraction must be between zero and one")
    if calls_across_boundary < 0 or transfer_bytes < 0:
        raise ValueError("boundary costs must be non-negative")
    if algorithm_improvement_available:
        return "improve-algorithm"
    if hotspot_fraction < 0.5:
        return "keep-python"
    if calls_across_boundary > 1_000 or transfer_bytes > 10_000_000:
        return "measure"
    return "batch-native-boundary"


def choose_next_step(
    *,
    equivalent: bool,
    peak_bytes: int,
    memory_budget_bytes: int,
    transfer_fraction: float,
    hotspot_fraction: float,
) -> Decision:
    """Prioritize correctness, hard bounds, and measured concentration."""

    if min(peak_bytes, memory_budget_bytes) < 0:
        raise ValueError("memory values must be non-negative")
    if not 0 <= transfer_fraction <= 1 or not 0 <= hotspot_fraction <= 1:
        raise ValueError("fractions must be between zero and one")
    if not equivalent:
        return "fix-correctness"
    if peak_bytes > memory_budget_bytes:
        return "reduce-memory"
    if transfer_fraction >= 0.3:
        return "reduce-transfer"
    if hotspot_fraction >= 0.5:
        return "optimize-hotspot"
    return "keep-current"


def representative_workload(size: int = 2_000) -> list[int]:
    if size < 2:
        raise ValueError("size must be at least two")
    values = list(range(size))
    values.append(size // 2)
    return values


def main() -> int:
    workload = representative_workload()
    baseline = first_duplicate_quadratic(workload)
    candidate = first_duplicate_linear(workload)
    print("equivalent:", baseline == candidate, "duplicate:", candidate)

    plan = BenchmarkPlan(warmup_calls=2, repeats=5, calls_per_repeat=5)
    baseline_timing = benchmark(lambda: first_duplicate_quadratic(workload), plan)
    candidate_timing = benchmark(lambda: first_duplicate_linear(workload), plan)
    print("baseline timing evidence:", baseline_timing)
    print("candidate timing evidence:", candidate_timing)

    profile = profile_call(lambda: first_duplicate_linear(workload))
    print("profile report first line:", profile.report.splitlines()[0])
    materialized = measure_peak_memory(lambda: sum_materialized_squares(workload))
    streamed = measure_peak_memory(lambda: sum_streamed_squares(workload))
    print(
        "memory evidence:",
        {"materialized_peak": materialized.peak_bytes, "streamed_peak": streamed.peak_bytes},
    )

    payload_bytes = serialized_payload_bytes({"values": workload})
    print(
        "four-worker transfer estimate:",
        estimated_transfer_bytes(payload_bytes, workers=4, copies_per_worker=1),
    )
    if importlib.util.find_spec("numpy") is None:
        print("NumPy comparison skipped; install the data profile")
    else:
        floats = [float(value) for value in workload]
        print("NumPy equivalent:", numpy_sum_squares(floats) == sum_squares_loop(floats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
