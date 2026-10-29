# pyweb-040: Background tasks, queues and durable work

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-039`.

## Starting point and result

Returning 202 means that a request was accepted under the application's contract; it does not prove that a durable worker will finish the requested work. This chapter distinguishes FastAPI BackgroundTasks from a task-queue API and from actual durable job execution.

## Mechanism: locate the owner of unfinished work

BackgroundTasks attaches work to the response lifecycle in the serving process. It is convenient for small bounded follow-up operations, but its memory and execution disappear if that process is lost. A callback scheduled this way is not automatically a durable message, a retry policy or an independently managed worker.

A queue library adds another interface, but its configuration determines what actually happens. Celery's eager test mode executes a task locally and immediately. A memory broker is also process-local. Those settings are valuable for testing task functions, but they do not establish broker persistence, worker recovery or delivery guarantees.

Durable work needs an operation identity and persistent state that another process can reconcile. The owned workshop uses a database-backed job ledger and a separate worker to make those properties explicit. It does not claim that the simple callback in this finite example has the same guarantees.

## Worked case: observe a response-attached callback

The endpoint adds a small record operation to BackgroundTasks and returns an accepted response. TestClient completes the response lifecycle, after which the program observes the recorded effect. The assertion proves the actual framework callback ran in this controlled invocation.

A fresh list remains empty because the original list is ordinary process memory. This simple comparison highlights the storage boundary: no durable record was written and no other process can discover the work from that list. Restarting the application would reconstruct its module state without the previous contents.

Do not rely on the client's observed request duration as a universal background timing guarantee. TestClient intentionally drives the application in process and can wait for work that a real client does not observe in the same way. The lifecycle and storage facts are more useful than an informal label such as asynchronous.

## Worked case: a real Celery task in eager mode

The program registers a task with Celery, submits it through delay and retrieves the expected total. Its configuration explicitly enables eager execution and exception propagation. The result verifies task registration, argument handling and the task function's behavior.

It does not start a worker or contact a durable broker. That absence is printed in the result instead of being hidden behind a successful task identifier. A production queue test would need to observe broker acceptance, worker execution, retries, duplicate delivery handling and state recovery after process replacement.

Task functions should accept stable data or identifiers rather than request objects, live database sessions or open file handles. Those process-bound objects may be invalid by the time another worker runs and are generally unsuitable for serialization.

## Failure diagnosis and discussion

**Can a task run more than once?** In many practical delivery designs, yes. A worker can complete an effect and lose its acknowledgement. Use idempotent operations or a durable effect identity instead of assuming exactly-once execution from a queue name.

**When is BackgroundTasks reasonable?** For small follow-up work whose lifetime and failure policy are compatible with the serving process. Critical or long-running operations need a stronger ownership and recovery design.

If a job disappears after restart, inspect where acceptance was committed and how unfinished work is discovered. Continue with WebSockets, where a long-lived connection still does not provide durable ownership by itself.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from celery import Celery
    from fastapi import BackgroundTasks, FastAPI
    from fastapi.testclient import TestClient

    events = []
    app = FastAPI(docs_url=None, redoc_url=None)

    def record(identifier):
        events.append(identifier)

    @app.post("/notify", status_code=202)
    def notify(tasks: BackgroundTasks):
        tasks.add_task(record, "notification-1")
        return {"accepted": True}

    with TestClient(app) as client:
        assert client.post("/notify").status_code == 202
        assert events == ["notification-1"]
    isolated = []
    assert isolated != events
    queue = Celery("finite-lesson", broker="memory://", backend="cache+memory://", fixups=[])
    queue.conf.update(task_always_eager=True, task_eager_propagates=True)

    @queue.task
    def total(values):
        return sum(values)

    assert total.delay([2, 3, 5]).get() == 10
    return {
        "background_effect_observed": events,
        "celery_eager_result": 10,
        "durable_worker_and_restart": "not exercised; use the owned workshop job ledger",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
