# pyweb-034: FastAPI response filtering and sensitive fields

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-033`.

## Starting point and result

An internal object often contains more information than an API should expose. A database row might include an owner key, private annotation or password hash. This chapter uses a response model to define the public representation, then deliberately returns an invalid value to show that output validation can reveal an application defect.

## Key terms

- **Response model:** The declared public representation FastAPI uses to filter and validate whatever object a route returns.
- **Output filtering:** Leaving fields outside the response model, such as an owner key or password hash, out of the serialized response.
- **Response validation:** Checking returned data against the response model; a failure is a server defect and produces 500, not a client error.
- **Data leakage:** Exposure of sensitive values through any path, including debug logs and exception messages that never pass through the response model.

## Mechanism: output is a separate contract

Request validation protects the input boundary. Response validation protects the representation produced by the application. They are independent: valid input does not guarantee valid output, and a correctly shaped response does not prove that the underlying operation was authorized.

FastAPI uses the declared response model to serialize and validate the returned object. Fields outside the public model are excluded from the representation. This is a useful final boundary, but sensitive data should still be handled carefully before serialization. Debug logs, exception messages and other code paths can expose values that the response model would have removed.

An invalid response is a server defect, not an ordinary client validation mistake. Returning a client-error code for a broken internal representation would mislead callers into changing a request that may already be valid. Tests should make that distinction visible and retain a safe diagnostic path for maintainers.

## Worked case: expose only the declared representation

The successful route returns an internal mapping that contains both public and private fields. Its declared response model includes only the intended public fields. The TestClient response is checked against the exact allowed key set and values.

Checking only that a private field is absent is weaker than checking the whole public contract. An unrelated accidental field could still appear. An exact representation assertion is appropriate for a small stable fixture, while a larger API may use schema compatibility tests to allow documented additive changes.

The public model can also transform values into their serialized representation. That transformation must remain deliberate. A model that silently coerces an unexpected internal value can hide a defect, so choose strictness and validators according to the contract's purpose rather than treating defaults as universally correct.

## Worked case: an invalid return reveals a server error

The second route returns data that cannot satisfy its response model. With the default TestClient behavior, the framework raises a response-validation exception to the test. With server exceptions converted into HTTP responses, the same defect appears as an internal server error.

These are two observation surfaces for one application failure. The exception form is useful while developing because it retains a precise diagnostic. The HTTP form resembles what a remote caller receives and should avoid exposing internal data. Neither should be mistaken for successful execution merely because the handler function returned something.

A production error handler should record a request correlation identifier and safe error classification. It should not copy the entire invalid response or private model into public JSON. The next chapter builds explicit problem responses for expected and unexpected failures.

## Worked example: a response model as an allow list

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class PublicUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class UserRow:
    def __init__(self):
        self.id = 1
        self.name = "Ada"
        self.password_hash = "fixture-must-not-leak"


print(PublicUser.model_validate(UserRow()).model_dump())
print(PublicUser.model_validate({"id": "2", "name": "Lin", "internal_role": "admin"}).model_dump())
try:
    PublicUser.model_validate({"id": "not-an-integer", "name": None})
except ValidationError as error:
    print(error.error_count(), [e["loc"][0] for e in error.errors()])
```

Expected output:

```text
{'id': 1, 'name': 'Ada'}
{'id': 2, 'name': 'Lin'}
2 ['id', 'name']
```

A `response_model` works as an allow list, and these three calls show the pieces FastAPI relies on. The first input is an ordinary object shaped like an ORM row; `from_attributes=True` lets the model read its attributes, and `password_hash` is dropped because the model never declared it. The second input is a dictionary with an extra `internal_role` key, which the default `extra="ignore"` setting discards while the string `"2"` is coerced to an integer. The third input is the server's own mistake, so validation fails on both fields. In the lesson's `/broken` route FastAPI turns that failure into `ResponseValidationError`, which a test sees as an exception and a client sees only as a bare 500. Keeping the public model separate from the storage model is what makes the filtering automatic: adding a sensitive column to the row later cannot leak unless someone also adds it to `PublicUser`.

## Failure diagnosis and discussion

**Why not return ORM objects directly without a response model?** It makes the public contract depend on internal shape and serialization behavior. An explicit output model gives reviewers a concrete boundary and helps catch accidental disclosure.

**Can a response model replace ownership checks?** No. A correctly filtered object can still belong to another user. Authorization chooses which object may be returned; serialization chooses which part of that object is public.

When an endpoint begins returning 500 after a schema change, inspect the actual returned value and the response model together. Do not remove output validation just to make the test pass. Continue with structured errors so clients can distinguish validation, conflict and unexpected failures reliably.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python isolated
"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from fastapi import FastAPI
    from fastapi.exceptions import ResponseValidationError
    from fastapi.testclient import TestClient
    from pydantic import BaseModel

    class PublicUser(BaseModel):
        id: int
        name: str

    app = FastAPI(docs_url=None, redoc_url=None)

    @app.get("/user", response_model=PublicUser)
    def user():
        return {
            "id": 1,
            "name": "Ada",
            "password_hash": "fixture-must-not-leak",
            "internal_role": "admin",
        }

    @app.get("/broken", response_model=PublicUser)
    def broken():
        return {"id": "not-an-integer", "name": None}

    with TestClient(app) as client:
        public = client.get("/user").json()
        assert public == {"id": 1, "name": "Ada"}
        try:
            client.get("/broken")
        except ResponseValidationError:
            diagnosed = True
        else:
            diagnosed = False
    assert diagnosed
    with TestClient(app, raise_server_exceptions=False) as client:
        error = client.get("/broken")
        assert error.status_code == 500 and "not-an-integer" not in error.text
    return {
        "filtered_public_fields": public,
        "response_bug_exposed_to_test": True,
        "public_server_error": 500,
        "response_validation_is_not_client_input_validation": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
