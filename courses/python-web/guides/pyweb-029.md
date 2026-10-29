# pyweb-029: FastAPI dependency injection and overrides

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-028`.

## Starting point and result

Dependencies let a FastAPI route request a resource or decision without manually constructing it in every handler. This chapter follows acquisition, use and cleanup through successful and failing requests. It also demonstrates a test override and the importance of removing that override afterward.

## Mechanism: the dependency graph owns lifetimes

A dependency is a callable whose inputs can themselves be dependencies. FastAPI resolves that graph for a request. A generator dependency with `yield` separates acquisition before the yield from cleanup after it. This is suitable for a request-scoped connection or unit of work whose lifetime must end even when the route raises an exception.

The yielded object is not automatically global application state. A reusable HTTP client pool can belong to application lifespan, while a database session belongs to one request. Confusing those lifetimes can leak transactions across users or repeatedly recreate an expensive pool. The dependency graph should express the intended ownership rather than merely reduce typing.

A test override replaces a particular dependency callable. It should be installed for the specific test and removed in a finally block or an equivalent fixture teardown. An override left in a global application can contaminate later tests, allowing them to pass using a fake resource unintentionally.

## Worked case: successful acquisition and cleanup

The complete program records lifecycle events in a bounded list. A successful request acquires its dependency, uses the yielded value and then triggers cleanup. The assertions examine the event order rather than inferring cleanup from a successful response.

This is a useful pattern for resource tests. A fake resource can expose when it closes, but the framework's dependency machinery is real. The evidence therefore concerns actual dependency orchestration with a small controlled object. It does not prove that a particular remote database driver closes sockets correctly under every failure mode.

The response checks the value produced through dependency resolution. That protects against a route accidentally bypassing the dependency and reading a global variable. The test also makes the intended seam obvious to a maintainer: construction happens at the boundary, while the route consumes the supplied capability.

## Worked case: exceptions and temporary overrides

A failing request still enters the cleanup portion of the generator. The program checks that event explicitly. It also installs a controlled override, verifies the changed result and removes the override before the final failure observation.

An exception does not automatically decide whether a transaction should commit. A dependency may manage rollback on failure, but the application must define that policy. Catching an exception inside a handler and returning an error response can look like normal completion to surrounding cleanup code. Transaction ownership must therefore be designed alongside exception handling.

Overrides are especially useful for clocks, outbound clients and authenticated identity in focused tests. They are less useful when they replace the exact behavior the test claims to validate. An authentication test that overrides the authentication dependency proves route behavior under an assumed identity, not password or token verification.

## Failure diagnosis and discussion

**Why can a test pass alone but fail in the suite?** Shared application objects, leaked overrides and unclosed resources are common causes. Check setup and teardown symmetry before adding sleeps or changing expected values.

**Should every dependency be asynchronous?** No. Choose based on actual operations and framework execution rules. Declaring an async function around a blocking call does not make that call nonblocking and can stall unrelated requests.

If cleanup appears missing, confirm that the response body was fully handled and that the relevant lifecycle context was entered. Streaming responses can extend a resource lifetime beyond initial header creation. Continue with application lifespan to separate process-level resource ownership from request-level dependencies.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from typing import Annotated

    from fastapi import Depends, FastAPI, HTTPException
    from fastapi.testclient import TestClient

    events = []

    def repository():
        events.append("open")
        try:
            yield {"value": 7}
        finally:
            events.append("close")

    app = FastAPI(docs_url=None, redoc_url=None)

    @app.get("/value")
    def value(repo: Annotated[dict, Depends(repository)]):
        return repo

    @app.get("/failure")
    def failure(repo: Annotated[dict, Depends(repository)]):
        assert repo["value"] == 7
        raise HTTPException(status_code=409, detail="intentional domain conflict")

    with TestClient(app) as client:
        assert client.get("/value").json() == {"value": 7}
        app.dependency_overrides[repository] = lambda: {"value": 42}
        try:
            assert client.get("/value").json() == {"value": 42}
        finally:
            app.dependency_overrides.clear()
        assert client.get("/failure").status_code == 409
    assert events == ["open", "close", "open", "close"]
    return {
        "resource_lifecycle": events,
        "override_restored": not app.dependency_overrides,
        "database_connection_executed": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
