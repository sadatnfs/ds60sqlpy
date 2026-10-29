# pyweb-015: Flask request context, application context and cleanup

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-014`.

## Starting point and result

Flask exposes convenient context-local proxies such as `request`, `g` and `current_app`. Their values belong to active contexts, not ordinary module globals. This chapter allocates a tiny request resource, closes it after success and failure, and demonstrates that an application context alone does not create a request.

## Mechanism: context ownership determines lifetime

The application context makes application-related state available. The request context adds information about a particular request. A normal request pushes the relevant contexts, which is why `g` is often used for resources associated with that request. More precisely, `g` belongs to the application context; manually retaining an application context can give it a different lifetime.

The before-request hook creates a resource with an ID. The teardown hook removes it using `g.pop` and records whether an exception occurred. Popping makes the cleanup idempotent for this fixture: repeated cleanup cannot close the same stored resource twice. Real resources such as database sessions need similarly clear ownership and appropriate close/rollback behavior.

The test deliberately uses clients without a surrounding preserved-request context. This makes each request's teardown boundary easy to inspect. Preserving contexts can be useful in tests, but then assertions about exactly when teardown occurs need to reflect that test configuration.

## Worked case: successful request cleanup

The `/ok` route reads its resource ID and request path. The response reports the first ID, and teardown records a successful close. The resource was made available through the context rather than passed as a global object shared by every request.

This pattern can avoid repeatedly opening the same resource within one request. It does not justify keeping an unbounded set of resources in `g` or using context-local state as persistent domain storage. Once its owning context ends, the resource should have an explicit retirement path.

## Worked case: failure and a missing request context

The `/fail` route raises a deliberate RuntimeError. Testing mode propagates that exception to the caller, which catches the expected error. Teardown still runs and records the second resource as closed after a failure. The program checks the complete close record rather than assuming exceptions automatically clean up every library object.

A separate application context allows access to `current_app`, but accessing `request.path` raises because there is no active request context. This makes the two boundaries observable. A background worker cannot safely reach back into a completed request by using the same proxy names; pass the necessary validated data explicitly.

## Failure diagnosis

“Working outside of application context” or “request context” usually signals a lifecycle mismatch. Adding an arbitrary global context around all code may hide the error while extending resource lifetimes incorrectly. Identify which operation actually needs the context and who should own it.

If cleanup runs twice in a test, inspect context preservation and teardown registration before removing cleanup altogether. If cleanup itself raises, it may obscure the original error. Keep cleanup small, deliberate and safe for partially initialized resources.

## Interview discussion

**Is `g` a global shared dictionary?** Its name is convenient, but its value is context-local. Typical request handling creates the relevant context automatically; manual contexts can change its lifetime.

**Should a background task retain `request`?** Pass explicit data such as an authenticated user ID or validated command. The original request context and its resources may already be gone when the task runs.

## Next step

Apply explicit ownership to a real database transaction, then prove that a failed batch does not leave partially committed rows.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    from itertools import count

    from flask import Flask, current_app, g, request

    app = Flask(__name__)
    app.config["TESTING"] = True
    identifiers, closed = count(1), []

    @app.before_request
    def open_resource():
        g.resource = {"id": next(identifiers)}

    @app.teardown_request
    def close_resource(error):
        resource = g.pop("resource", None)
        if resource is not None:
            closed.append({"id": resource["id"], "failed": error is not None})

    @app.get("/ok")
    def ok():
        return {"id": g.resource["id"], "path": request.path}

    @app.get("/fail")
    def fail():
        raise RuntimeError("intentional fixture failure")

    client = app.test_client()
    assert client.get("/ok").json == {"id": 1, "path": "/ok"}
    try:
        client.get("/fail")
    except RuntimeError as error:
        assert str(error) == "intentional fixture failure"
    else:
        raise AssertionError("Testing must propagate this intentional exception")
    assert closed == [{"id": 1, "failed": False}, {"id": 2, "failed": True}]
    with app.app_context():
        assert current_app is not None
        try:
            _ = request.path
        except RuntimeError:
            no_request = True
        else:
            no_request = False
    assert no_request
    return {"closed_resources": closed, "application_context_is_not_request_context": no_request}


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
