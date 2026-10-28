"""Executable references for python-lang-04 using only local awaitables."""

from __future__ import annotations

import asyncio
import math
from collections.abc import Awaitable, Callable
from contextvars import ContextVar

REQUEST_ID: ContextVar[str] = ContextVar("request_id", default="outside")


# Exercise 1: Return ordered structured results.
async def ordered_group(
    values: tuple[int, ...], operation: Callable[[int], Awaitable[int]]
) -> tuple[int, ...]:
    async def run(value: int) -> int:
        return await operation(value)

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(run(value)) for value in values]
    return tuple(task.result() for task in tasks)


# Exercise 2: Limit active work with cleanup.
async def limited_group(
    values: tuple[int, ...],
    operation: Callable[[int], Awaitable[int]],
    limit: int,
    events: list[tuple[str, int]],
) -> tuple[int, ...]:
    if type(limit) is not int or limit <= 0:
        raise ValueError("Expected a positive integer limit")
    gate = asyncio.Semaphore(limit)

    async def run(value: int) -> int:
        async with gate:
            events.append(("start", value))
            try:
                return await operation(value)
            finally:
                events.append(("finish", value))

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(run(value)) for value in values]
    return tuple(task.result() for task in tasks)


# Exercise 3: Put a deadline around owned work.
async def with_deadline(operation: Callable[[], Awaitable[int]], seconds: float) -> int:
    if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("Expected a finite positive deadline")
    async with asyncio.timeout(seconds):
        return await operation()


# Exercise 4: Make cancellation cleanup observable.
async def cancellable_wait(ready: asyncio.Event, release: asyncio.Event, events: list[str]) -> str:
    events.append("acquired")
    try:
        ready.set()
        await release.wait()
        return "released"
    finally:
        events.append("closed")


# Exercise 5: Inspect every grouped failure.
def describe_failures(group: ExceptionGroup) -> tuple[tuple[str, ...], tuple[str, ...]]:
    values: list[str] = []
    others: list[str] = []

    def visit(error: Exception) -> None:
        if isinstance(error, ExceptionGroup):
            for child in error.exceptions:
                visit(child)
        elif isinstance(error, ValueError):
            values.append(str(error))
        else:
            others.append(str(error))

    visit(group)
    return tuple(values), tuple(others)


# Exercise 6: Restore task-local request context.
async def scoped_request(value: str, operation: Callable[[], Awaitable[str]]) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("Expected a nonempty request label")
    token = REQUEST_ID.set(value)
    try:
        return await operation()
    finally:
        REQUEST_ID.reset(token)


async def _verify_async() -> None:
    async def calculate(value: int) -> int:
        await asyncio.sleep(0)
        return value * 10

    assert await ordered_group((3, 1, 2), calculate) == (30, 10, 20)
    assert await ordered_group((), calculate) == ()
    ready = asyncio.Event()
    closed: list[int] = []

    async def failing(value: int) -> int:
        try:
            if value == 0:
                ready.set()
                await asyncio.Event().wait()
            await ready.wait()
            raise ValueError("bad child")
        finally:
            closed.append(value)

    try:
        await ordered_group((0, 1), failing)
    except ExceptionGroup as errors:
        assert describe_failures(errors) == (("bad child",), ())
    else:
        raise AssertionError("A task failure was hidden")
    assert sorted(closed) == [0, 1]
    events: list[tuple[str, int]] = []

    async def square(value: int) -> int:
        await asyncio.sleep(0)
        return value * value

    assert await limited_group(tuple(range(6)), square, 2, events) == (0, 1, 4, 9, 16, 25)
    active = peak = 0
    for event, _ in events:
        active += 1 if event == "start" else -1
        assert 0 <= active <= 2
        peak = max(peak, active)
    assert active == 0 and peak == 2
    for invalid in (0, -1, True):
        try:
            await limited_group((), square, invalid, [])
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid limit accepted")

    async def immediate() -> int:
        return 7

    assert await with_deadline(immediate, 1) == 7
    timeout_events: list[str] = []

    async def blocked() -> int:
        try:
            await asyncio.Event().wait()
            return 0
        finally:
            timeout_events.append("closed")

    try:
        await with_deadline(blocked, 0.02)
    except TimeoutError:
        assert timeout_events == ["closed"]
    else:
        raise AssertionError("Deadline did not expire")
    for invalid_deadline in (0, -1, True, math.inf, math.nan):
        try:
            await with_deadline(immediate, invalid_deadline)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid deadline accepted")
    started, release = asyncio.Event(), asyncio.Event()
    cancel_events: list[str] = []
    task = asyncio.create_task(cancellable_wait(started, release, cancel_events))
    await started.wait()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("Cancellation was hidden")
    assert task.cancelled() and cancel_events == ["acquired", "closed"]
    release.set()
    success_events: list[str] = []
    assert await cancellable_wait(asyncio.Event(), release, success_events) == "released"
    assert success_events == ["acquired", "closed"]

    async def read_label() -> str:
        before = REQUEST_ID.get()
        await asyncio.sleep(0)

        async def read_child() -> str:
            await asyncio.sleep(0)
            return REQUEST_ID.get()

        child = await asyncio.create_task(read_child())
        assert before == REQUEST_ID.get() == child
        return before

    assert tuple(
        await asyncio.gather(
            scoped_request("north", read_label), scoped_request("south", read_label)
        )
    ) == ("north", "south")
    assert REQUEST_ID.get() == "outside"

    async def bad_label() -> str:
        assert REQUEST_ID.get() == "broken"
        raise ValueError("broken operation")

    try:
        await scoped_request("broken", bad_label)
    except ValueError as error:
        assert str(error) == "broken operation"
    else:
        raise AssertionError("Request failure was hidden")
    assert REQUEST_ID.get() == "outside"
    cancellation_ready = asyncio.Event()
    restored: list[str] = []

    async def waiting_label() -> str:
        assert REQUEST_ID.get() == "cancelled"
        cancellation_ready.set()
        await asyncio.Event().wait()
        return "unreachable"

    async def owned_request() -> None:
        try:
            await scoped_request("cancelled", waiting_label)
        finally:
            restored.append(REQUEST_ID.get())

    request = asyncio.create_task(owned_request())
    await cancellation_ready.wait()
    request.cancel()
    try:
        await request
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("Request cancellation was hidden")
    assert restored == ["outside"] and REQUEST_ID.get() == "outside"
    assert len(asyncio.all_tasks()) == 1


def verify_examples() -> None:
    nested = ExceptionGroup(
        "outer",
        [ValueError("bad"), ExceptionGroup("inner", [RuntimeError("disk"), ValueError("bad")])],
    )
    assert describe_failures(nested) == (("bad", "bad"), ("disk",))
    assert describe_failures(ExceptionGroup("other", [TypeError("wrong")])) == ((), ("wrong",))
    asyncio.run(_verify_async())
    print("All six structured asyncio, cancellation, and context contracts passed.")


if __name__ == "__main__":
    verify_examples()
