"""python-pro-02 learner lab: concurrency and parallelism.

The worked example measures a sequential local wait. Complete the TODO
functions before comparing your design with the reference implementation.
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

    for label, call in (
        (
            "execution-model choice",
            lambda: choose_execution_model("blocking-io", async_api_available=False),
        ),
        ("lost-update model", deterministic_lost_update),
    ):
        try:
            value = call()
        except NotImplementedError:
            print(f"TODO: {label}")
        else:
            print(f"Completed: {label} -> {value!r}")


if __name__ == "__main__":
    asyncio.run(worked_example())
