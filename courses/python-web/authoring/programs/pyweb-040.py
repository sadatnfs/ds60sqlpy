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
