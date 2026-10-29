# pyweb-063: Structured concurrency and service time budgets

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-009`, `pyweb-012`, `python-lang-04`.

## Starting point and result

A request may depend on several concurrent operations, but those operations need one accountable lifetime. Structured concurrency keeps child tasks inside a parent scope that waits for their completion or cancellation. This chapter uses TaskGroup and an explicit deadline to verify cleanup when one dependency fails.

## Mechanism: task ownership forms a tree

An asyncio TaskGroup owns the tasks created inside its context. If one task fails, the group cancels remaining tasks and waits for them before leaving the context. Related exceptions are represented through an exception group, which the caller can handle with except*. This makes unfinished child work visible at the parent boundary.

A timeout bounds the duration of a waiting operation by cancelling the current task within a controlled context. The timeout exception is observed outside that context after cancellation handling has run. A finally block remains the appropriate place to release a resource owned by the cancelled operation.

A service deadline is broader than one HTTP client's socket timeout. The total request budget must account for queue waiting, dependency calls, retries and serialization. Spending the entire budget on the first dependency can leave no useful time for cleanup or a meaningful response.

## Worked case: one dependency fails and its sibling cleans up

The program starts one task that waits indefinitely and another that waits until the first has begun, then raises a controlled failure. TaskGroup cancels the waiting sibling and waits for its finally block. The program asserts both the expected exception and the cleanup event.

An explicit Event establishes ordering, so the test does not depend on an arbitrary sleep being long enough. The failure occurs only after the sibling is known to have entered its owned scope. That makes the cancellation claim reproducible on a busy learner machine.

The example also runs a successful group and reads its completed task results. Reading result before the group exits would require another completion guarantee. The context boundary provides that guarantee in the intended structure.

## Worked case: a deadline triggers cleanup

A separate operation waits on an event that will not be released. An asyncio timeout expires, the operation's finally block records cleanup and the caller handles TimeoutError. The assertion concerns cleanup and failure classification, not a precise millisecond benchmark.

Cancellation does not undo a committed external effect. A database write or remote payment may have completed before the caller's timeout. The next chapter introduces stable operation identities and transactional outboxes to reconcile that uncertainty.

Work that must survive request cancellation should move into an explicitly durable job system. Detaching a task with create_task and dropping its reference does not provide durable ownership. It merely makes the lifetime harder to observe and can lose work when the process stops.

## Failure diagnosis and discussion

**Why await a cancelled task?** Cancellation is a request delivered cooperatively. Awaiting lets the caller observe termination and gives cleanup a defined completion boundary.

**Why can timeout handling still take time?** The cancelled operation may need to finish cleanup. A timeout is not an instantaneous kill of every external activity, especially threads or processes launched by the coroutine.

If child work continues after a request fails, inspect task ownership and detached tasks. If cancellation is swallowed, inspect broad exception handlers and ensure they preserve the intended cancellation semantics. If latency grows under load, inspect queue capacity and total deadlines rather than adding more unbounded concurrency.

Continue with retries and outboxes. Their central question is what happens when an operation's result is unknown even though its side effect may already exist.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Finite cross-framework engineering investigation with explicit scope."""

import asyncio
import json


async def cases():
    cleaned = asyncio.Event()
    started = asyncio.Event()

    async def waiting():
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaned.set()

    async def failing():
        await started.wait()
        raise ValueError("controlled dependency failure")

    caught = []
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(waiting())
            group.create_task(failing())
    except* ValueError as errors:
        caught.extend(str(error) for error in errors.exceptions)
    assert cleaned.is_set() and caught == ["controlled dependency failure"]
    timed_out_cleanup = []

    async def operation():
        try:
            await asyncio.Event().wait()
        finally:
            timed_out_cleanup.append(True)

    try:
        async with asyncio.timeout(0.02):
            await operation()
    except TimeoutError:
        pass
    else:
        raise AssertionError("Deadline was not applied")
    assert timed_out_cleanup == [True]

    async def value(number):
        await asyncio.sleep(0)
        return number * 2

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(value(n)) for n in (2, 3)]
    assert [task.result() for task in tasks] == [4, 6]
    return {
        "sibling_cancelled_and_awaited": True,
        "deadline_cleanup": True,
        "successful_results": [4, 6],
        "timing": "no throughput claim",
    }


if __name__ == "__main__":
    print(json.dumps(asyncio.run(cases()), sort_keys=True))
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/)
