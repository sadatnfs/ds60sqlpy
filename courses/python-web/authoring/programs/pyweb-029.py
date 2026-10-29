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
