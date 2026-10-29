# pyweb-030: FastAPI lifespan and resource ownership

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-029`.

## Starting point and result

A web application often needs a pool, model, cache client or other resource before it can serve requests. FastAPI's lifespan interface gives that resource an explicit startup and shutdown boundary. This chapter shows why a TestClient context manager matters and why a request failure should not accidentally destroy a shared application resource.

## Mechanism: process resources surround requests

An asynchronous context manager performs setup, yields control while the application serves, then performs cleanup. The application can store the prepared resource in `app.state`. Route code accesses that resource after startup rather than creating an unrelated copy on every call.

This is a process-local contract. Starting four server workers normally creates four application lifespans and therefore four copies of process-owned state. A list or cache in one worker is not shared with the other workers. A database or external coordination service is needed when the state must be consistent across processes or survive replacement.

Startup failure should prevent the application from claiming readiness. Shutdown should release resources it owns, but should not delete durable learner data. A health check must also distinguish process liveness from readiness to handle a particular dependency-dependent operation. Returning a fixed success body does not establish that the required resource exists.

## Worked case: enter the real lifespan context

The program creates its FastAPI application with a lifespan function. The TestClient context enters startup before the request and exits through shutdown afterward. Assertions inspect the prepared state during the request and the final cleanup observation after the context closes.

The sequence is the key result: setup precedes use, and cleanup follows all use. This avoids tests that pass only because a module-level resource happened to be constructed during import. Importing a module should define application structure; it should not silently connect to production services or start background loops.

A fixture that constructs TestClient without entering its context does not automatically provide the same lifespan evidence. The example deliberately demonstrates the missing-resource behavior under that incorrect setup, then contrasts it with the intended context-managed run.

## Worked case: a failing request does not end application ownership

Inside a running lifespan, one request fails while a later valid request still uses the same prepared resource. The application resource remains available until the whole client context ends. The assertions distinguish request completion from application shutdown.

That distinction informs database design. A shared connection pool may survive request failures, while a request-scoped transaction must roll back and release its borrowed connection. Closing the entire pool inside a request error handler can cause unrelated clients to fail. Conversely, keeping a failed transaction alive for the next request can expose inconsistent state.

The finite example uses a bounded controlled object, so it proves the actual FastAPI/Starlette lifecycle ordering. The owned workshop adds a real server process and checks shutdown, resume and persistent database behavior separately. A client context alone does not establish signal handling or container restart behavior.

## Failure diagnosis and discussion

**Why does the route work under the server but fail in a unit test?** The test may have skipped lifespan startup. Reproduce the intended lifecycle rather than manually assigning the missing state and hiding the integration error.

**Why does adding workers multiply resource use?** Each process has its own memory and startup path. Size connection pools and model copies against total workers, not just the per-process setting.

Next, examine asynchronous request execution. A correct lifespan establishes ownership, but it does not make blocking work cooperative or provide unlimited capacity.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from contextlib import asynccontextmanager

    from fastapi import FastAPI, HTTPException
    from fastapi.testclient import TestClient

    events = []
    resources = []

    @asynccontextmanager
    async def lifespan(app):
        resource = {"open": True, "requests": 0}
        resources.append(resource)
        app.state.resource = resource
        events.append("startup")
        try:
            yield
        finally:
            resource["open"] = False
            events.append("shutdown")

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)

    @app.get("/resource")
    def resource():
        app.state.resource["requests"] += 1
        return app.state.resource

    @app.get("/failure")
    def failure():
        raise HTTPException(status_code=409, detail="intentional fixture conflict")

    without_context = TestClient(app)
    try:
        try:
            without_context.get("/resource")
        except AttributeError:
            missing = True
        else:
            missing = False
    finally:
        without_context.close()
    assert missing and events == []
    with TestClient(app) as client:
        assert client.get("/resource").json() == {"open": True, "requests": 1}
        assert client.get("/failure").status_code == 409
        assert client.get("/resource").json() == {"open": True, "requests": 2}
    assert events == ["startup", "shutdown"] and resources[0] == {"open": False, "requests": 2}
    return {
        "missing_lifespan_detected": True,
        "events": events,
        "shared_resource_survived_request_failure": True,
        "resource_closed_on_application_exit": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
