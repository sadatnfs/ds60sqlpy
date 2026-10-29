"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    import asyncio
    from contextlib import suppress

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI(docs_url=None, redoc_url=None)

    @app.get("/cooperate")
    async def cooperate():
        active = 0
        maximum = 0

        async def work(number):
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            await asyncio.sleep(0)
            active -= 1
            return number

        sequential = [await work(2), await work(3)]
        sequential_max = maximum
        maximum = 0
        concurrent = await asyncio.gather(work(2), work(3))
        return {
            "sequential_sum": sum(sequential),
            "concurrent_sum": sum(concurrent),
            "sequential_overlap": sequential_max,
            "concurrent_overlap": maximum,
        }

    @app.get("/cancel")
    async def cancel():
        entered = asyncio.Event()
        closed = []

        async def owned():
            try:
                entered.set()
                await asyncio.Future()
            finally:
                closed.append("released")

        task = asyncio.create_task(owned())
        await entered.wait()
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        return {"cleanup": closed, "cancelled": task.cancelled()}

    with TestClient(app) as client:
        coordination = client.get("/cooperate").json()
        assert coordination == {
            "sequential_sum": 5,
            "concurrent_sum": 5,
            "sequential_overlap": 1,
            "concurrent_overlap": 2,
        }
        cancellation = client.get("/cancel").json()
        assert cancellation == {"cleanup": ["released"], "cancelled": True}
    return {
        "coordination": coordination,
        "cancellation": cancellation,
        "throughput_benchmark": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
