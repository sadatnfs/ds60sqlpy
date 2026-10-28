"""python-lang-04: Structured Asyncio, Cancellation, and Context Ownership.

Run two offline worked examples, then implement the six separate task functions.
Each classroom Run starts a fresh process; saved source and notes persist.
The opening examples do not call the unimplemented exercises.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from contextvars import ContextVar

REQUEST_ID: ContextVar[str] = ContextVar("request_id", default="outside")


# Exercise 1: Return ordered structured results.
# Inputs: A small finite tuple of integer values and an asynchronous operation for each value.
# Expected: Create one child per value inside asyncio.TaskGroup, await group exit, and return
# | results in input order regardless of completion order. Empty input returns (). A
# | child Exception must propagate as an ExceptionGroup after sibling cleanup; do not
# | return partial success or leave child tasks running.
# Verify: Operations deliberately released in reverse order for (1, 2, 3) still return (10,
# | 20, 30). An injected child failure cancels a waiting sibling and its finally block
# | runs before the group exits.
async def ordered_group(
    values: tuple[int, ...], operation: Callable[[int], Awaitable[int]]
) -> tuple[int, ...]:
    """Return ordered structured results.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement ordered_group")


# Exercise 2: Limit active work with cleanup.
# Inputs: A small finite tuple, an async operation, an exact positive integer limit, and an
# | event list.
# Expected: Use a TaskGroup plus a Semaphore so at most limit operation calls are active. Record
# | ("start", value) after acquisition and ("finish", value) in finally before releasing
# | the slot. Preserve input result order and propagate group failure/caller
# | cancellation after cleanup. Reject invalid limits with ValueError even for empty
# | input. This bounds active calls, not the number of scheduled tasks.
# Verify: Six yielding operations with limit 2 return their six squares. Walk the event
# | transcript to prove active work never exceeds 2 and ends at zero. Under failure
# | every recorded start has a matching finish.
async def limited_group(
    values: tuple[int, ...],
    operation: Callable[[int], Awaitable[int]],
    limit: int,
    events: list[tuple[str, int]],
) -> tuple[int, ...]:
    """Limit active work with cleanup.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement limited_group")


# Exercise 3: Put a deadline around owned work.
# Inputs: A factory for one awaitable and a finite strictly positive int or float deadline in
# | seconds, excluding bool.
# Expected: Validate the deadline before calling the factory. Use asyncio.timeout to return
# | success or raise TimeoutError after timed-out work has finished its finally cleanup.
# | A cancellation from the caller remains asyncio.CancelledError; an operation
# | ValueError remains ValueError. Do not manufacture fallback values.
# Verify: An immediately completing operation returns 7. A blocked local Event wait times out
# | and records closed before TimeoutError is observed. Reject zero, negative, True,
# | infinity, and NaN without calling the factory.
async def with_deadline(operation: Callable[[], Awaitable[int]], seconds: float) -> int:
    """Put a deadline around owned work.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement with_deadline")


# Exercise 4: Make cancellation cleanup observable.
# Inputs: Two Events in the running loop and an observation list. The ready signal lets a
# | controller know acquisition has happened.
# Expected: Append acquired, set ready, then await release and return released. Append closed in
# | finally on success or cancellation; allow CancelledError to propagate. The
# | controller owns the created task and must await it after cancelling. Do not use
# | sleeps to guess whether acquisition occurred.
# Verify: Wait for ready, cancel the task, await it, and require CancelledError with events
# | ["acquired", "closed"]. With release already set, the result is released and the
# | same balanced event list appears.
async def cancellable_wait(ready: asyncio.Event, release: asyncio.Event, events: list[str]) -> str:
    """Make cancellation cleanup observable.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement cancellable_wait")


# Exercise 5: Inspect every grouped failure.
# Inputs: An ExceptionGroup, possibly containing nested ExceptionGroups and ValueError
# | subclasses alongside other ordinary Exceptions.
# Expected: Return (value_error_messages, other_messages), traversing leaves depth first in
# | their original order within each category. Classify using isinstance(error,
# | ValueError); preserve each leaf message, including duplicates. Do not flatten by
# | stringifying group summary text or classify BaseException control signals as
# | ordinary failures.
# Verify: A nested group containing ValueError("bad"), RuntimeError("disk"), and
# | ValueError("bad") gives (("bad", "bad"), ("disk",)). An all-other group gives an
# | empty first tuple.
def describe_failures(group: ExceptionGroup) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Inspect every grouped failure.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement describe_failures")


# Exercise 6: Restore task-local request context.
# Inputs: A nonempty string request label and an async operation. Use the module ContextVar
# | REQUEST_ID with default outside.
# Expected: Set REQUEST_ID for the operation, return its result, and reset the exact token in
# | finally on success, ordinary failure, or caller cancellation. Child tasks inherit a
# | copy of the current context. Concurrent requests must not overwrite each other;
# | invalid labels raise ValueError before invoking the operation.
# Verify: Concurrent request labels north and south each remain visible across an await and in
# | their own child task. The calling context is outside afterward. Repeat with an
# | injected ValueError and cancellation and inspect restoration in the same task.
async def scoped_request(value: str, operation: Callable[[], Awaitable[str]]) -> str:
    """Restore task-local request context.

    See the explicit input, expected, and verification contract above.
    """
    raise NotImplementedError("Implement scoped_request")


def worked_examples() -> None:
    import asyncio

    async def ordered_demo():
        async def calculate(value):
            await asyncio.sleep(0)
            return value * 10

        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(calculate(value)) for value in (3, 1)]
        result = tuple(task.result() for task in tasks)
        assert result == (30, 10)
        return result

    print("Input-order results:", asyncio.run(ordered_demo()))

    import asyncio

    async def cancellation_demo():
        ready = asyncio.Event()
        never = asyncio.Event()
        events = []

        async def worker():
            events.append("open")
            try:
                ready.set()
                await never.wait()
            finally:
                events.append("close")

        task = asyncio.create_task(worker())
        await ready.wait()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        else:
            raise AssertionError("Cancellation was swallowed")
        assert task.cancelled()
        assert events == ["open", "close"]
        return events

    print("Awaited cancellation:", asyncio.run(cancellation_demo()))


if __name__ == "__main__":
    worked_examples()
    print("Examples passed. Implement and verify the six separate task functions.")
