# pyweb-025: Flask async views and background-work limits

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-024`.

## Starting point and result

Flask can run async view functions when its async support is installed. The surrounding WSGI execution model still matters. This chapter compares work awaited by a view with a task created and abandoned when that view returns. Both behaviors are observed through actual Flask client requests in the pinned environment.

## Key terms

- **Async view:** A Flask view defined with `async def`, which the WSGI async bridge runs to completion on an event loop created for that request.
- **asyncio.gather:** A function that awaits several awaitables concurrently and returns all their results, so the response can depend on every one of them.
- **asyncio.create_task:** A function that schedules a coroutine to run on its own; under Flask's WSGI bridge a task still pending when the view returns is cancelled.
- **Durable job:** Work recorded in persistent storage and executed by a separate worker, so it survives the request, process restarts and failures.

## Mechanism: the request owns the async view's lifetime

An async function can coordinate awaitable operations. The first route uses `asyncio.gather` to await two small operations and returns their completed sum. Those operations belong to the request's computation, and the response depends on their results.

A background task created with `asyncio.create_task` has a different relationship. Under this ordinary Flask WSGI async bridge, the event loop used for the request completes when the async view returns. Pending tasks are cancelled as that loop is retired. Creating a task does not turn the WSGI process into a durable task service.

The fixture's pending task records startup and records its cancellation in `finally`. It has a long sleep so it remains pending when the view returns, but the test does not wait for that whole sleep. Cancellation is the behavior being observed.

## Worked case: awaited work completes before the result

The awaited route computes two values using coroutines that yield at a scheduling point. Their sum is five, and the client receives that representation. This shows correct coordination of the request's required results.

It does not prove that async is faster for this workload or that the server handles more simultaneous clients. The example is tiny and in process. Real throughput depends on the WSGI server's process/thread model, the libraries called by the handler, connection limits and the workload's I/O/CPU mix.

## Worked case: an abandoned task is cancelled

The second route starts the pending task, yields so it begins, then returns a successful response. By the time the client request finishes under the tested bridge, the event list contains both startup and cancellation. A successful HTTP response therefore did not prove that the requested background work would finish later.

A durable job needs an explicit submission/processing contract. Queues, database-backed work ledgers or an appropriate long-lived async service can provide different lifecycles, but each still needs failure, retry and idempotency design. The owned workshop demonstrates a separate worker and persistent job state; this program deliberately reports that no durable queue ran.

## Worked example: an orphaned task versus an awaited task

```python
import asyncio

events = []


async def background(name):
    try:
        events.append(f"{name} started")
        await asyncio.sleep(0.05)
        events.append(f"{name} finished")
    finally:
        events.append(f"{name} exited")


async def view_fire_and_forget():
    asyncio.create_task(background("orphan"))
    await asyncio.sleep(0)
    return "response sent"


async def view_awaited():
    task = asyncio.create_task(background("owned"))
    await asyncio.sleep(0)
    await task
    return "response sent"


for view in (view_fire_and_forget, view_awaited):
    print(asyncio.run(view()))
print(events)
```

Expected output:

```text
response sent
response sent
['orphan started', 'orphan exited', 'owned started', 'owned finished', 'owned exited']
```

Each `asyncio.run` call here stands in for one Flask request: Flask hands an async view to a fresh event loop through `asgiref`, and that loop is closed once the view returns. Both views report success, yet only the owned task ever printed `finished`. When the first loop shut down, `asyncio.run` cancelled every task still pending, so the orphan ran its `finally` block and vanished halfway through its work. Nothing in the response warns you, which is why the lesson's `/spawned` route returns 200 while its event list proves the background job was cancelled. The rule that follows is narrow: inside a Flask async view, only work you await before returning is guaranteed to run. Email sending, report building and anything that must survive the request belong in a durable queue with its own worker process, not in `create_task`.

## Failure diagnosis

Missing emails, reports or updates after a successful request may come from work whose lifetime ended with the request. Blocking synchronous calls inside an async view can also eliminate the expected concurrency benefits. Inspect the actual adapter and library behavior rather than assuming that an async signature makes all underlying work nonblocking.

Cancellation cleanup should release resources and avoid disguising failure as completion. A `finally` block can record cleanup, but it does not retroactively make an interrupted side effect atomic. Important external effects need their own transactional or idempotent protocol.

## Interview discussion

**Can Flask async views be useful?** Yes, for appropriate awaitable work within the supported request lifecycle. Their usefulness does not imply that unawaited tasks become reliable background jobs.

**Why does a successful response not prove the background operation succeeded?** The response can be produced independently of that task's completion. The application must expose and verify the relevant job state if later completion matters.

## Next step

Combine routing, authentication, CSRF and storage in one finite application investigation before moving to an actual long-running workshop deployment.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python isolated
"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    import asyncio

    from flask import Flask

    events = []
    app = Flask(__name__)

    async def unfinished():
        try:
            events.append("background-started")
            await asyncio.sleep(60)
        finally:
            events.append("background-cancelled")

    @app.get("/awaited")
    async def awaited():
        async def value(number):
            await asyncio.sleep(0)
            return number

        result = await asyncio.gather(value(2), value(3))
        return {"sum": sum(result)}

    @app.get("/spawned")
    async def spawned():
        asyncio.create_task(unfinished())
        await asyncio.sleep(0)
        return {"response": "completed"}

    client = app.test_client()
    assert client.get("/awaited").json == {"sum": 5}
    assert client.get("/spawned").status_code == 200
    assert events == ["background-started", "background-cancelled"]
    return {
        "awaited_work_finished": True,
        "request_attached_task_cancelled": True,
        "durable_queue_executed": False,
        "server_concurrency_benchmarked": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
