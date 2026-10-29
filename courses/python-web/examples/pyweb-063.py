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
