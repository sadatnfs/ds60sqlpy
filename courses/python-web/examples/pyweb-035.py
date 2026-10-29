"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from fastapi import FastAPI, Request
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, Field

    class Input(BaseModel):
        amount: int = Field(ge=1)

    class Conflict(Exception):
        pass

    app = FastAPI(docs_url=None, redoc_url=None)

    def problem(request, status, kind, title, **extra):
        return JSONResponse(
            {
                "type": "urn:example:problem:" + kind,
                "title": title,
                "status": status,
                "instance": request.url.path,
                **extra,
            },
            status_code=status,
            media_type="application/problem+json",
        )

    @app.exception_handler(Conflict)
    async def conflict(request: Request, error: Conflict):
        return problem(request, 409, "conflict", "Resource conflict")

    @app.exception_handler(RequestValidationError)
    async def invalid(request: Request, error: RequestValidationError):
        fields = [{"location": list(item["loc"]), "code": item["type"]} for item in error.errors()]
        return problem(request, 422, "validation", "Invalid request", errors=fields)

    @app.exception_handler(Exception)
    async def unexpected(request: Request, error: Exception):
        return problem(request, 500, "internal", "Internal server error")

    @app.post("/reserve")
    def reserve(payload: Input):
        if payload.amount > 3:
            raise Conflict()
        return {"reserved": payload.amount}

    @app.get("/unexpected")
    def fail():
        raise RuntimeError("private diagnostic fixture")

    with TestClient(app, raise_server_exceptions=False) as client:
        assert client.post("/reserve", json={"amount": 2}).json() == {"reserved": 2}
        failures = [
            client.post("/reserve", json={"amount": 4}),
            client.post("/reserve", json={"amount": 0}),
            client.get("/unexpected"),
        ]
        assert [response.status_code for response in failures] == [409, 422, 500]
        assert all(
            response.headers["content-type"] == "application/problem+json"
            and response.json()["status"] == response.status_code
            for response in failures
        )
        assert "private diagnostic" not in failures[-1].text
    return {
        "problem_types": [r.json()["type"] for r in failures],
        "statuses": [409, 422, 500],
        "internal_exception_not_exposed": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
