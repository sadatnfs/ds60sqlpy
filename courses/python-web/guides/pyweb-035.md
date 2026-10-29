# pyweb-035: FastAPI errors and problem-details documents

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-034`.

## Starting point and result

Clients need stable error semantics, but an exception's internal text is rarely an appropriate public contract. This chapter defines a small problem-response shape for invalid input, a known resource conflict and an unexpected server failure. It verifies both HTTP status and response content using real FastAPI exception handlers.

## Mechanism: classify failures before serializing them

A problem response contains a type identifier, human-readable title, status and instance. The type identifies a class of problem rather than a particular stack trace. Additional fields can describe safe validation locations or machine-readable codes. The response uses `application/problem+json` so callers can recognize the representation.

The fixture uses original URN identifiers for its small example. A real API should document stable types and avoid changing their meaning casually. Human wording can improve over time, while a programmatic client should branch on stable fields rather than substring matches inside an exception message.

Expected domain failures and unexpected defects deserve different treatment. A capacity conflict can return 409 with a clear public explanation. An invalid request can return 422 with safe field locations. An unhandled internal exception should produce a generic 500 response while detailed diagnostics remain available through controlled internal logging.

## Worked case: classify a valid command and an expected conflict

The reserve endpoint accepts a bounded positive amount. An amount within the fixture's capacity returns a successful reservation. A larger valid amount reaches domain logic and raises the named Conflict exception. Its handler returns the conflict problem type and status 409.

This separates input validity from business availability. The number can be a valid positive integer while the requested operation cannot currently be fulfilled. Collapsing both situations into a generic validation response would hide the distinction from clients deciding whether to correct input or retry later.

The test examines the response media type, status and problem fields. A JSON body saying status 409 with an actual HTTP 200 would be an inconsistent contract, so both layers are asserted. The response does not need to expose the Python exception class to communicate the domain condition.

## Worked case: invalid input and an internal defect

An amount below the schema's lower bound fails request validation. The custom handler extracts safe location and error-code information instead of echoing arbitrary submitted content. A separate endpoint raises an exception containing a private diagnostic phrase; the public 500 response must not include that phrase.

TestClient is configured to observe error responses rather than reraising server exceptions. This is intentional for the public-contract case. Developer tests can also retain the default reraising mode when they need the original traceback. Choosing one observation mode does not make the other behavior disappear.

Validation errors can contain sensitive inputs, especially for passwords, tokens or uploaded metadata. A generic dump of the framework exception may disclose them. Build the public error representation from an explicit allowlist and keep diagnostic collection proportionate to the operational need.

## Failure diagnosis and discussion

**Should every exception be converted to a 409?** No. That would label programming errors and infrastructure failures as expected conflicts and could trigger inappropriate client behavior. Handle only conditions whose semantics are understood.

**Why include an instance field?** It helps connect the problem to the attempted resource or operation. It should avoid sensitive query values or credentials and need not reveal internal file paths.

If a handler produces the right body but the wrong status, inspect the Response construction rather than only the serialized dictionary. If sensitive text appears, inspect error extraction and logging independently. Continue with bearer authentication, where signature checks and claim validation become another explicit boundary before domain code runs.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
