"""python-pro-02 learner lab: concurrency and parallelism.

The worked example measures a sequential local wait. Complete the TODO
functions before comparing your design with the reference implementation.

Professional learner deep dive (python-pro-02)
------------------------------------------------

Mental model:
Concurrency overlaps work; parallelism executes work simultaneously. `asyncio` is effective when
many operations spend time awaiting nonblocking I/O. Threads can overlap blocking I/O behind a
synchronous API. Processes bypass the Global Interpreter Lock for CPU-bound Python work but
require serialization, startup, and platform-safe entry points.  Unlimited fan-out converts
latency into memory, connection, and rate pressure. A production design needs admission bounds,
result/error accounting, cancellation cleanup, timeouts, ordering semantics, and measurement
against a sequential baseline.

API/boundary anatomy:
* workload classification: identifies CPU time, blocking/nonblocking I/O, data transfer, and
  external capacity before selecting a primitive.
* semaphore/worker queue: bounds active and queued work rather than creating one task per input.
* structured result: associates each input with success/failure/cancellation so no work
  disappears.

Micro-example A — state the execution choice from the blocking behavior::

    def choose_execution(*, waits_nonblocking=False, waits_blocking=False, cpu_python=False):
        if sum((waits_nonblocking, waits_blocking, cpu_python)) != 1:
            raise ValueError("classify one dominant workload")
        if waits_nonblocking:
            return "asyncio"
        if waits_blocking:
            return "threads"
        return "processes-or-native-vectorization"

    assert choose_execution(waits_nonblocking=True) == "asyncio"
    assert choose_execution(cpu_python=True) == "processes-or-native-vectorization"

Expected: The decision follows where time is spent, not a belief that one primitive is
          universally faster.

Micro-example B — prove an async concurrency ceiling::

    import asyncio

    async def demo():
        gate = asyncio.Semaphore(2)
        active = 0
        peak = 0

        async def work(value):
            nonlocal active, peak
            async with gate:
                active += 1
                peak = max(peak, active)
                await asyncio.sleep(0)
                active -= 1
                return value * 2

        results = await asyncio.gather(*(work(i) for i in range(6)))
        return results, peak

    results, peak = asyncio.run(demo())
    print(results, peak)
    assert results == [0, 2, 4, 6, 8, 10] and peak == 2

Expected: All inputs are accounted for while no more than two operations enter the protected
          section.

Debugging rule: Measure sequential and candidate paths, record active/queued counts, per-item
                results, timeout/cancellation cleanup, serialization size, and platform start
                method.

The snippets demonstrate mechanics only. They do not complete the
numbered TODOs below; implement those from their stated contracts and
prove normal, boundary, and failure behavior.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable, Sequence
from typing import Literal, TypeVar

T = TypeVar("T")
R = TypeVar("R")
Workload = Literal["async-io", "blocking-io", "cpu"]
Model = Literal["asyncio", "threads", "processes"]


def choose_execution_model(
    workload: Workload,
    *,
    async_api_available: bool,
) -> Model:
    """Choose the first concurrency model to evaluate.

    TODO:
    - cooperative async I/O with an async API -> asyncio
    - blocking I/O without an async API -> threads
    - substantial pure-Python CPU work -> processes

    Reject contradictory input such as claiming an async API for CPU work.
    """

    raise NotImplementedError("complete choose_execution_model")


async def bounded_map(
    items: Sequence[T],
    worker: Callable[[T], Awaitable[R]],
    *,
    worker_count: int,
    queue_capacity: int,
) -> list[R]:
    """Map an async worker while bounding active work and queued work.

    TODO: use an ``asyncio.Queue(maxsize=queue_capacity)``, a fixed number of
    consumers, and ``asyncio.TaskGroup``. Preserve input order. A worker
    exception must cancel sibling work rather than being hidden.
    """

    raise NotImplementedError("complete bounded_map")


def deterministic_lost_update(initial: int = 0) -> tuple[int, int]:
    """Model two unsynchronized read/modify/write operations.

    TODO: return ``(unsafe_result, serialized_result)``. Force both unsafe
    workers to read the same initial snapshot before either writes. This
    demonstrates the race without relying on a timing-sensitive thread test.
    """

    raise NotImplementedError("complete deterministic_lost_update")


async def _worked_wait(delay: float) -> str:
    await asyncio.sleep(delay)
    return f"waited {delay:.3f}s"


async def worked_example() -> None:
    """Run a deterministic sequential baseline and show unfinished exercises."""

    started = time.perf_counter()
    messages = [await _worked_wait(delay) for delay in (0.01, 0.01, 0.01)]
    elapsed = time.perf_counter() - started
    print(f"Sequential async baseline: {messages}; elapsed >= 0.03? {elapsed >= 0.03}")

    checks: tuple[tuple[str, Callable[[], object]], ...] = (
        (
            "execution-model choice",
            lambda: choose_execution_model("blocking-io", async_api_available=False),
        ),
        ("lost-update model", deterministic_lost_update),
    )
    for label, call in checks:
        try:
            value = call()
        except NotImplementedError:
            print(f"TODO: {label}")
        else:
            print(f"Completed: {label} -> {value!r}")


# === Numbered professional practice ===
#
# Attempt every exercise before opening solutions. Keep evidence in a copy
# under .learning/ or in tests; do not overwrite the reference solution.
# Full acceptance checks and progressive hints:
# companion-guides/py_pro_02_concurrency_parallelism.md
#
# Exercise 1 — choose a model
# Prompt: Implement `choose_execution_model` in the learner artifact. For each case, write
# one sentence explaining the choice: - an async database driver, - a synchronous file
# metadata API, - image transforms written in pure Python, - three tiny computations.
# Reject labels that contradict each other. An async function that performs computation
# without `await` is still CPU work and blocks the event loop.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 2 — build a bounded async map
# Prompt: Implement `bounded_map` with: 1. `asyncio.Queue(maxsize=queue_capacity)`, 2. one
# producer, 3. a fixed number of consumers, 4. indexed items so results retain input
# order, 5. a unique sentinel per consumer, and 6. `asyncio.TaskGroup`. Place
# `queue.task_done()` in `finally`. Let exceptions propagate. Do not catch
# `CancelledError` unless cleanup requires it; if caught, re-raise it.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 3 — add per-item timeouts
# Prompt: Wrap each worker call with `asyncio.timeout`. Test one worker slower than the
# limit. Inspect the `ExceptionGroup` from `TaskGroup`, and verify a `finally` block
# returns the active count to zero. Prediction: what happens to sibling consumers when one
# item times out?
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 4 — adapt blocking I/O
# Prompt: Use `ThreadPoolExecutor(max_workers=N)` for deterministic `time.sleep` jobs.
# Compare sequential and threaded elapsed time with generous bounds, then verify ordered
# results rather than treating speed as the correctness assertion. Explain why a thread
# pool requires a deliberate `max_workers`, even if the remote service could theoretically
# accept more requests.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 5 — isolate CPU work
# Prompt: Make the CPU function a top-level function with serializable arguments and
# results. Use `multiprocessing.get_context("spawn")` with `ProcessPoolExecutor`, and
# create processes only beneath an `if __name__ == "__main__":` guard. Run the solution
# with `--with-processes`; explain when startup makes a small workload slower.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 6 — reason about shared state
# Prompt: Implement `deterministic_lost_update`. Force two workers to read the same
# snapshot, then apply both writes. Compare with two serialized increments. List three
# repairs: - one owner task/process receives update messages, - a lock protects the
# complete read/modify/write unit, or - an external system performs an atomic update.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 7 — prove cancellation cleanup
# Prompt: Cancel `bounded_map` while workers are active. Instrument acquired resources and
# prove active count, queued acknowledgements, and child tasks return to zero before the
# parent finishes.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 8 — inspect structured failures
# Prompt: Run multiple workers that fail with different typed exceptions. Use `except*` to
# handle one expected category while preserving unexpected failures and their original
# tracebacks.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 9 — stream a backpressured producer
# Prompt: Adapt `bounded_map` from a finite Sequence to an async iterator whose length is
# unknown. Preserve output order without retaining every input or creating one task per
# item.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 10 — trace context across boundaries
# Prompt: Set a request ID in `contextvars`, then observe propagation through an async
# task, `asyncio.to_thread`, a raw thread-pool submission, and a spawned process. Make any
# explicit propagation visible.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 11 — design graceful executor shutdown
# Prompt: Own a thread or process pool through a context manager. Stop accepting new work,
# wait with a bounded policy, cancel pending futures when allowed, and report unfinished
# work without hanging interpreter exit.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 12 — make an evidence-based model decision
# Prompt: Benchmark sequential, bounded asyncio/threads, and spawned processes on
# representative I/O and CPU fixtures. Record correctness, startup, throughput, peak
# active work, transfer size, and cleanup—not just fastest elapsed time.
# Verify: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    asyncio.run(worked_example())
