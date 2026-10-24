"""python-perf-01 learner lab: measurement-first optimization.

Professional learner deep dive (python-perf-01)
------------------------------------------------

Mental model:
Performance engineering begins with a user-visible budget and a reproducible workload. Wall-
clock timing includes noise from warm-up, caching, scheduling, CPU frequency, allocation, and
I/O. Repeat measurements, report a distribution, and keep correctness checks beside the
benchmark.  Profiling locates where time or memory is spent; algorithmic analysis explains how
cost grows. Optimize the measured bottleneck, then rerun correctness and end-to-end evidence.
Faster code that changes results, ordering, errors, or resource bounds is a regression.

API/boundary anatomy:
* benchmark contract: fixes data size/distribution, environment, warm-up, repetitions,
  statistic, and correctness invariant.
* profile → hypothesis → one change: connects an observed hotspot to a scoped optimization
  rather than guessing.
* scale curve + budget: measures several input sizes and checks latency/memory against an
  explicit threshold.

Micro-example A — report repeat timing instead of one lucky run::

    import statistics
    import timeit

    samples = timeit.repeat(
        "sum(range(10_000))",
        repeat=7,
        number=200,
    )
    report = {
        "median_seconds": statistics.median(samples),
        "min_seconds": min(samples),
        "max_seconds": max(samples),
    }
    print(report)
    assert report["min_seconds"] <= report["median_seconds"] <= report["max_seconds"]

Expected: Repeated timings vary; median and range reveal noise that one measurement hides.

Micro-example B — contrast quadratic and linear duplicate detection::

    def has_duplicate_quadratic(values):
        return any(values[i] in values[:i] for i in range(len(values)))

    def has_duplicate_linear(values):
        seen = set()
        for value in values:
            if value in seen:
                return True
            seen.add(value)
        return False

    for size in (100, 1_000):
        data = list(range(size))
        assert has_duplicate_quadratic(data) == has_duplicate_linear(data) == False
    print("both implementations agree on measured inputs")

Expected: Both functions preserve the Boolean contract, while the set-based design has expected
          linear rather than quadratic growth.

Debugging rule: Reproduce the workload, record environment, profile CPU/memory/I/O, validate
                outputs, change one hotspot, and compare repeated end-to-end distributions.

The snippets demonstrate mechanics only. They do not complete the
numbered TODOs below; implement those from their stated contracts and
prove normal, boundary, and failure behavior.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Literal

Decision = Literal[
    "fix-correctness",
    "reduce-memory",
    "reduce-transfer",
    "optimize-hotspot",
    "keep-current",
]


def first_duplicate_linear(values: Sequence[int]) -> int | None:
    """Return the first value encountered for a second time.

    TODO: preserve semantics while replacing repeated prefix scans with a set.
    """

    raise NotImplementedError("complete first_duplicate_linear")


def estimated_transfer_bytes(
    payload_bytes: int,
    *,
    workers: int,
    copies_per_worker: int,
) -> int:
    """TODO: validate nonnegative inputs and estimate copied process bytes."""

    raise NotImplementedError("complete estimated_transfer_bytes")


def choose_next_step(
    *,
    equivalent: bool,
    peak_bytes: int,
    memory_budget_bytes: int,
    transfer_fraction: float,
    hotspot_fraction: float,
) -> Decision:
    """TODO: apply the guide's deterministic evidence-priority policy."""

    raise NotImplementedError("complete choose_next_step")


def first_duplicate_quadratic(values: Sequence[int]) -> int | None:
    """Worked baseline whose repeated prefix membership is O(n squared)."""

    for index, value in enumerate(values):
        if value in values[:index]:
            return value
    return None


def self_check() -> None:
    workload = [4, 1, 3, 2, 3, 4]
    print("Worked baseline duplicate:", first_duplicate_quadratic(workload))
    checks: tuple[tuple[str, Callable[[], object]], ...] = (
        ("linear equivalent", lambda: first_duplicate_linear(workload)),
        (
            "process transfer estimate",
            lambda: estimated_transfer_bytes(1_024, workers=4, copies_per_worker=2),
        ),
        (
            "evidence decision",
            lambda: choose_next_step(
                equivalent=True,
                peak_bytes=100,
                memory_budget_bytes=1_000,
                transfer_fraction=0.1,
                hotspot_fraction=0.2,
            ),
        ),
    )
    for label, call in checks:
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


# === Numbered professional practice ===
#
# Attempt every exercise before opening solutions. Keep evidence in a copy
# under .learning/ or in tests; do not overwrite the reference solution.
# Full acceptance checks and progressive hints:
# companion-guides/py_perf_01_measurement_optimization.md
#
# Exercise 1 — Define semantics before speed
# Prompt: For `[4, 1, 3, 2, 3, 4]`, the answer is `3`: the duplicate whose *second*
# occurrence appears first. Complete `first_duplicate_linear` with a set and prove
# equivalence for empty, unique, immediate, and competing duplicates.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 2 — Build a representative timing plan
# Prompt: Choose a workload size large enough to rise above timer noise but small enough
# for quick study. Warm up separately, then collect at least five repeated batches with
# `timeit`. Record Python version, platform, input size, and plan. Do not assert
# “candidate < baseline” in the test suite. CI hosts, antivirus, power state, and
# schedulers make that flaky.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 3 — Ask cProfile a different question
# Prompt: Profile one complete representative call and sort by cumulative time. Locate the
# call path, not just the leaf with the largest self time. Reduce the workload if
# profiling overhead dominates, and do not compare profiled seconds directly with
# unprofiled `timeit` seconds.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 4 — Measure allocation pressure
# Prompt: Compare materialized-list and generator sums with `tracemalloc`. Assert equal
# results and report bounds (`peak >= current >= 0`). Explain why `tracemalloc` may not
# see memory allocated inside every native library.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 5 — Compare optional vectorization
# Prompt: With NumPy installed, compare a Python loop with `np.square(array).sum()`.
# Include conversion from Python values when that conversion exists in the real workflow.
# Small input can favor the loop; already-resident large arrays can favor vectorized
# native work. Measure both representative cases.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 6 — Model process transfer
# Prompt: Serialize a safe local JSON payload and measure its byte length. Complete
# `estimated_transfer_bytes`. Four workers each receiving two copies move eight payload
# equivalents before computation. Real process protocols may add framing, copies, or
# shared-memory complexity.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 7 — Evaluate caching
# Prompt: Use `cached_fibonacci.cache_info()` to observe hits. Then evaluate a real
# candidate by: - measured reuse, - entry count and bytes, - invalidation/freshness rules,
# - key cardinality, and - whether retained objects prevent memory release. Caching a low-
# reuse, high-cardinality result can make performance worse.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 8 — Bound native/FFI work
# Prompt: Use the policy to prefer an available algorithm improvement. If a measured
# hotspot remains, batch native calls and cap transfer. Survey Cython, Rust/PyO3, C/C++
# extensions, and `ctypes`/`cffi`; record build wheels, ABI, ownership, error, and safety
# obligations before choosing one.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 9 — Apply the evidence decision
# Prompt: Complete `choose_next_step` in priority order: 1. fix unequal behavior, 2.
# reduce peak memory beyond budget, 3. reduce transfer consuming at least 30 percent, 4.
# optimize a hotspot consuming at least 50 percent, or 5. keep the current implementation.
# Thresholds are a transparent lesson policy, not universal laws. Return the evidence and
# selected action so a reviewer can reproduce the decision.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 10 — compare timing distributions
# Prompt: Run interleaved repeated batches for baseline and candidate, report median,
# spread, paired ratios/differences, environment, and correctness. Avoid a binary CI speed
# assertion.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 11 — diagnose warmup, GC, and environment noise
# Prompt: Measure cold import/first call separately from steady state. Repeat with garbage
# collection controlled, background load noted, and process affinity/power assumptions
# documented rather than hidden.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 12 — trade algorithm speed for memory
# Prompt: Compare set-based first-duplicate search with a sorted/indexed alternative under
# a strict memory budget. Preserve 'first second occurrence' semantics and report
# time/peak memory across unique-heavy and duplicate-early inputs.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 13 — test vectorized dtype boundaries
# Prompt: Compare Python integer sum-of-squares with NumPy int32, int64, float, and object
# arrays near overflow. Detect silent overflow and choose a validated dtype.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 14 — evaluate shared-memory process input
# Prompt: Compare normal process serialization with read-only shared memory for one large
# numeric payload. Include setup/copy, worker mapping, cleanup, spawn compatibility, and
# ownership failure cases.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 15 — separate I/O concurrency from CPU optimization
# Prompt: Benchmark a local fake I/O wait and a pure-Python CPU loop under sequential,
# async/thread, and process designs. Explain why each model helps one workload and may
# hurt another.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 16 — prevent a cache stampede
# Prompt: Model many callers missing one expensive cache key. Add single-flight ownership,
# bounded wait, success publication, failure cleanup, and stale/retry policy with injected
# time.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 17 — review an FFI ownership boundary
# Prompt: Specify one batched native function: accepted buffer dtype/layout, length,
# ownership/lifetime, mutability, error mapping, GIL behavior, panic/exception
# containment, and platform wheel matrix.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 18 — design a continuous performance gate
# Prompt: Define a stable local/CI benchmark artifact with workload version, correctness
# hash, environment, raw timings, peak memory, practical regression budget, comparison
# policy, and an investigation path instead of an immediate flaky fail.
# Verify: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    self_check()
