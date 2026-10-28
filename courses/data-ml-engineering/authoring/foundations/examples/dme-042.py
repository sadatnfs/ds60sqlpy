"""Actual asynchronous ASGI admission, cancellation cleanup and uncertain-effect reconciliation."""

import asyncio
from contextlib import suppress

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field


class Effect(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation_id: str = Field(min_length=1, max_length=30)
    units: int = Field(ge=1, le=100)


def application():
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.active = 0
    app.state.maximum = 0
    app.state.lock = asyncio.Lock()
    app.state.two_entered = asyncio.Event()
    app.state.release = asyncio.Event()
    app.state.effect_written = asyncio.Event()
    app.state.response_release = asyncio.Event()
    app.state.effects = {}

    @app.get("/bounded")
    async def bounded():
        async with app.state.lock:
            if app.state.active >= 2:
                raise HTTPException(429, "The bounded local capacity is full")
            app.state.active += 1
            app.state.maximum = max(app.state.maximum, app.state.active)
            if app.state.active == 2:
                app.state.two_entered.set()
        try:
            await app.state.release.wait()
            return {"accepted": True}
        finally:
            async with app.state.lock:
                app.state.active -= 1

    @app.post("/effect")
    async def effect(request: Effect):
        async with app.state.lock:
            prior = app.state.effects.get(request.operation_id)
            if prior is not None and prior != request.units:
                raise HTTPException(409, "Operation identity has conflicting content")
            outcome = "replayed" if prior is not None else "applied"
            app.state.effects[request.operation_id] = request.units
            app.state.effect_written.set()
        await app.state.response_release.wait()
        return {"outcome": outcome, "accepted_total": sum(app.state.effects.values())}

    return app


async def capacity_case():
    app = application()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://fixture"
    ) as client:
        first = asyncio.create_task(client.get("/bounded"))
        second = asyncio.create_task(client.get("/bounded"))
        try:
            await asyncio.wait_for(app.state.two_entered.wait(), 2)
            rejected = await client.get("/bounded")
            assert rejected.status_code == 429 and app.state.active == 2
            first.cancel()
            with suppress(asyncio.CancelledError):
                await first
            assert app.state.active == 1
            app.state.release.set()
            response = await asyncio.wait_for(second, 2)
            assert response.status_code == 200 and app.state.active == 0
            final = await client.get("/bounded")
            assert final.status_code == 200 and app.state.maximum == 2
            return {
                "third_request_status": 429,
                "maximum_active": 2,
                "active_after_cleanup": 0,
                "scope": "actual in-process ASGI task cancellation, not a proxy or TCP timeout",
            }
        finally:
            app.state.release.set()
            for task in (first, second):
                if not task.done():
                    task.cancel()
            await asyncio.gather(first, second, return_exceptions=True)


async def effect_case():
    app = application()
    payload = {"operation_id": "effect-a", "units": 3}
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://fixture"
    ) as client:
        task = asyncio.create_task(client.post("/effect", json=payload))
        try:
            await asyncio.wait_for(app.state.effect_written.wait(), 2)
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            assert app.state.effects == {"effect-a": 3}
            app.state.response_release.set()
            retry = await client.post("/effect", json=payload)
            conflict = await client.post("/effect", json={**payload, "units": 100})
            assert (
                retry.json() == {"outcome": "replayed", "accepted_total": 3}
                and conflict.status_code == 409
            )
            return {
                "caller_cancelled_after_effect": True,
                "retry": retry.json(),
                "conflicting_retry_status": 409,
                "state_is_in_memory_and_does_not_survive_process_restart": True,
            }
        finally:
            app.state.response_release.set()
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)


def example_one():
    return asyncio.run(capacity_case())


def example_two():
    return asyncio.run(effect_case())


def main():
    print("Bounded admission and cleanup:", example_one())
    print("Cancellation does not reverse an accepted effect:", example_two())


if __name__ == "__main__":
    main()
