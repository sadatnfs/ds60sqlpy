# pyweb-005: Input schemas and explicit validation errors

Tutorial mode. Stage: beginner. Direct prerequisites: `pyweb-004`, `python-12`.

## Starting point and result

Parsing JSON produces Python values, but it does not establish that those values describe a valid order. A schema states required fields, supported types, bounds and the treatment of unknown fields. The example uses a real Pydantic model within a Flask endpoint so the validation mechanism is visible independently of any framework's automatic integration.

## Mechanism: make coercion and extra fields deliberate

The `Order` model requires a nonempty bounded item name and an integer quantity from one through ten. `ConfigDict(strict=True, extra="forbid")` rejects coercions and fields outside that model. The handler calls `model_validate`, catches `ValidationError`, and returns a bounded error representation containing field paths and error types.

Strictness is a contract choice. Some interfaces deliberately accept a numeric string from a form or query, where transport values naturally arrive as text. A JSON command can instead require an actual JSON number. The problem is silent inconsistency: a caller should not have to discover by accident which strings, booleans or floats are accepted.

Python booleans deserve special attention because `bool` is a subclass of `int`. A manual `isinstance(value, int)` check can therefore accept `True` as a quantity. The strict model rejects that case. Extra-field rejection also prevents the handler from blindly assigning an unexpected field such as `approved` to internal state.

## Worked case: a valid bounded command

The request `{"item": "book", "quantity": 2}` satisfies the contract. The handler returns its validated serialization with status 201. The response is derived from the model rather than from an unexamined copy of the original request body.

Validation gives subsequent code useful assumptions: the quantity is an integer in range, and the name satisfies the stated length limits. It does not prove that the item exists, stock is available, the caller is authorized or a concurrent request will not consume the last unit. Those checks belong to domain logic, authorization and transaction design.

## Worked case: three plausible but invalid requests

The program sends quantity `"2"`, quantity `True`, and an otherwise valid order with an extra `approved` field. All return 422. It specifically checks the extra-field error type, which makes the refusal observable rather than merely relying on a generic failure status.

A public error document should reveal enough for a client to repair its request without exposing sensitive internal details. The example selects error locations and types instead of serializing every exception object. Custom validation context can contain values or objects unsuitable for a public response; copying an entire internal exception is not a stable API design.

## Failure diagnosis

If validation unexpectedly accepts an input, inspect the configured coercion rules and the exact field type. If an endpoint returns a model successfully but later fails in the database, distinguish schema validation from database constraints. If a new client breaks after adding a field, consider compatibility and versioning rather than casually disabling all validation.

Schema validation also differs from sanitization. A valid string may contain HTML-sensitive characters, and a valid integer may identify someone else's object. Use parameterized SQL, context-aware escaping and ownership checks at the relevant boundaries.

## Interview discussion

**Should every API use strict validation?** Choose intentionally for its transport and compatibility needs. Strict JSON commands and explicitly parsed query strings can coexist in one well-documented API.

**Does rejecting extra fields solve authorization?** It prevents one class of accidental assignment. The server must still derive trusted identity and verify permission to perform the operation.

## Next step

Render validated and unvalidated text into HTML and observe the separate responsibility of output escaping.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, request
    from pydantic import BaseModel, ConfigDict, Field, ValidationError

    class Order(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        item: str = Field(min_length=1, max_length=30)
        quantity: int = Field(ge=1, le=10)

    app = Flask(__name__)

    @app.post("/orders")
    def create():
        try:
            value = Order.model_validate(request.get_json(silent=True))
        except ValidationError as error:
            problems = [
                {"path": list(item["loc"]), "type": item["type"]} for item in error.errors()
            ]
            return {"errors": problems}, 422
        return value.model_dump(), 201

    with app.test_client() as client:
        valid = client.post("/orders", json={"item": "book", "quantity": 2})
        invalid = [
            client.post("/orders", json=body)
            for body in (
                {"item": "book", "quantity": "2"},
                {"item": "book", "quantity": True},
                {"item": "book", "quantity": 2, "approved": True},
            )
        ]
        assert valid.status_code == 201 and valid.json["quantity"] == 2
        assert all(response.status_code == 422 for response in invalid)
        assert invalid[2].json["errors"][0]["type"] == "extra_forbidden"
    return {
        "valid": valid.json,
        "invalid_types": [response.json for response in invalid],
        "validation_does_not_replace_authorization": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
