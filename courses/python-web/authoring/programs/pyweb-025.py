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
