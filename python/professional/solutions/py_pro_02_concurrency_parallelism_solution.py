"""Reference implementation for python-pro-02.

The module demonstrates bounded asyncio work, blocking I/O in threads, and
pure-Python CPU work in spawned processes. Workloads are deterministic and
small enough for a lesson and its tests.
"""

from __future__ import annotations

import argparse
import asyncio
import multiprocessing
import time
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Generic, Literal, TypeVar, cast

T = TypeVar("T")
R = TypeVar("R")
Workload = Literal["async-io", "blocking-io", "cpu"]
Model = Literal["asyncio", "threads", "processes"]


@dataclass
class ConcurrencyProbe:
    """Track active and peak work on one asyncio event loop."""

    active: int = 0
    peak: int = 0

    @asynccontextmanager
    async def activity(self) -> AsyncIterator[None]:
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            yield
        finally:
            self.active -= 1


@dataclass(frozen=True)
class BoundedRun(Generic[R]):
    """Ordered values and observable bounds from an async run."""

    values: tuple[R, ...]
    worker_count: int
    queue_capacity: int
    peak_active: int


def choose_execution_model(
    workload: Workload,
    *,
    async_api_available: bool,
) -> Model:
    """Choose a useful starting model from workload behavior."""

    if workload == "cpu":
        if async_api_available:
            raise ValueError("a pure-Python CPU workload does not have an async API")
        return "processes"
    if workload == "async-io":
        if not async_api_available:
            raise ValueError("async-io requires an awaitable API")
        return "asyncio"
    if async_api_available:
        raise ValueError("blocking-io should not be labeled as an async API")
    return "threads"


async def bounded_map(
    items: Sequence[T],
    worker: Callable[[T], Awaitable[R]],
    *,
    worker_count: int,
    queue_capacity: int,
    item_timeout: float | None = None,
    probe: ConcurrencyProbe | None = None,
) -> BoundedRun[R]:
    """Map async work through a bounded queue and structured task group."""

    if worker_count < 1:
        raise ValueError("worker_count must be at least 1")
    if queue_capacity < 1:
        raise ValueError("queue_capacity must be at least 1")
    if item_timeout is not None and item_timeout <= 0:
        raise ValueError("item_timeout must be positive")

    sentinel = object()
    queue: asyncio.Queue[tuple[int, T] | object] = asyncio.Queue(maxsize=queue_capacity)
    results: dict[int, R] = {}
    activity_probe = probe if probe is not None else ConcurrencyProbe()

    async def produce() -> None:
        for index, item in enumerate(items):
            await queue.put((index, item))
        for _ in range(worker_count):
            await queue.put(sentinel)

    async def consume() -> None:
        while True:
            entry = await queue.get()
            try:
                if entry is sentinel:
                    return
                index, item = cast(tuple[int, T], entry)
                async with activity_probe.activity():
                    if item_timeout is None:
                        result = await worker(item)
                    else:
                        async with asyncio.timeout(item_timeout):
                            result = await worker(item)
                results[index] = result
            finally:
                queue.task_done()

    async with asyncio.TaskGroup() as group:
        group.create_task(produce(), name="bounded-producer")
        for number in range(worker_count):
            group.create_task(consume(), name=f"bounded-consumer-{number}")

    if len(results) != len(items):
        raise RuntimeError("structured run finished without one result per input")
    return BoundedRun(
        values=tuple(results[index] for index in range(len(items))),
        worker_count=worker_count,
        queue_capacity=queue_capacity,
        peak_active=activity_probe.peak,
    )


async def delayed_square(value: int, *, delay: float = 0.01) -> int:
    """Represent cooperative local I/O with a deterministic result."""

    await asyncio.sleep(delay)
    return value * value


def _blocking_wait(job: tuple[int, float]) -> int:
    """Represent a library call that blocks its thread."""

    value, delay = job
    time.sleep(delay)
    return value * value


def run_blocking_io_in_threads(
    jobs: Sequence[tuple[int, float]],
    *,
    max_workers: int,
) -> tuple[int, ...]:
    """Run independent blocking waits in a bounded thread pool."""

    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")
    with ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix="ds60-io",
    ) as executor:
        return tuple(executor.map(_blocking_wait, jobs))


def cpu_checksum(limit: int) -> int:
    """Perform deterministic pure-Python CPU work in a picklable function."""

    if limit < 0:
        raise ValueError("limit must be non-negative")
    return sum((number * number) % 97 for number in range(limit))


def run_cpu_work_in_processes(
    limits: Sequence[int],
    *,
    max_workers: int,
) -> tuple[int, ...]:
    """Use spawned processes so the example matches Windows behavior."""

    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(
        max_workers=max_workers,
        mp_context=context,
    ) as executor:
        return tuple(executor.map(cpu_checksum, limits))


def deterministic_lost_update(initial: int = 0) -> tuple[int, int]:
    """Return unsafe and serialized results for two increments."""

    first_snapshot = initial
    second_snapshot = initial
    unsafe_value = first_snapshot + 1
    unsafe_value = second_snapshot + 1

    serialized_value = initial
    serialized_value += 1
    serialized_value += 1
    return unsafe_value, serialized_value


def _flatten_exceptions(
    group: BaseExceptionGroup[BaseException],
) -> tuple[BaseException, ...]:
    """Flatten a nested task-group exception for concise demonstration output."""

    leaves: list[BaseException] = []
    for exception in group.exceptions:
        if isinstance(exception, BaseExceptionGroup):
            leaves.extend(_flatten_exceptions(exception))
        else:
            leaves.append(exception)
    return tuple(leaves)


async def demonstrate_async_failure() -> str:
    """Show that one failed item cancels sibling work and reaches the caller."""

    async def worker(value: int) -> int:
        await asyncio.sleep(0)
        if value == 2:
            raise RuntimeError("item 2 failed")
        await asyncio.sleep(0.02)
        return value

    try:
        await bounded_map(
            [1, 2, 3],
            worker,
            worker_count=2,
            queue_capacity=1,
        )
    except ExceptionGroup as group:
        leaves = _flatten_exceptions(group)
        return ", ".join(f"{type(exc).__name__}: {exc}" for exc in leaves)
    raise AssertionError("the failure demonstration unexpectedly succeeded")


async def async_demo() -> None:
    """Run bounded work, timeout behavior, and failure propagation."""

    result = await bounded_map(
        [1, 2, 3, 4],
        delayed_square,
        worker_count=2,
        queue_capacity=1,
        item_timeout=0.1,
    )
    print(f"async values: {result.values}; peak active: {result.peak_active}")
    print(f"propagated failure: {await demonstrate_async_failure()}")


def build_parser() -> argparse.ArgumentParser:
    """Create a parser whose process demo is explicit for notebook safety."""

    parser = argparse.ArgumentParser(description="Run deterministic concurrency demos.")
    parser.add_argument(
        "--with-processes",
        action="store_true",
        help="also launch a small Windows-spawn-compatible process pool",
    )
    return parser


def main() -> int:
    """Run local demonstrations behind the required process main guard."""

    args = build_parser().parse_args()
    asyncio.run(async_demo())
    print(
        "thread values:",
        run_blocking_io_in_threads(
            [(1, 0.01), (2, 0.01), (3, 0.01)],
            max_workers=2,
        ),
    )
    print("lost update (unsafe, serialized):", deterministic_lost_update())
    if args.with_processes:
        print(
            "process checksums:",
            run_cpu_work_in_processes([5_000, 5_500], max_workers=2),
        )
    else:
        print("process demo skipped; pass --with-processes to run it")
    return 0


if __name__ == "__main__":
    # Windows and macOS spawn a fresh interpreter. The guard prevents every
    # child from recursively creating another process pool.
    raise SystemExit(main())
