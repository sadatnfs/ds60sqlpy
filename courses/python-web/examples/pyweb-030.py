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
