# pyweb-020: Flask authorization and object ownership

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-019`.

## Starting point and result

Authentication identifies a caller; authorization decides what that caller may do. A successful login does not grant access to every row in a table. This chapter uses two real Flask-Login client sessions and verifies ownership rules on both a list endpoint and an individual-object endpoint.

## Mechanism: trusted identity scopes every lookup

The user loader restores a known user from the signed session. The list endpoint filters records using `current_user.id`. The object endpoint checks the requested record's owner before returning it. Neither endpoint accepts a client-supplied owner field as authority.

Object-level authorization matters even when IDs are difficult to guess. A client can obtain an ID from logs, links or another user. Authorization therefore belongs at the data-access boundary, not in an assumption that an identifier will remain secret. A database implementation should incorporate the caller's permitted scope in its query where practical.

The fixture returns the same 404 shape for an absent record and a record outside the caller's scope. That is a deliberate policy to limit disclosure. Some products use a different documented policy, but they still need a consistent ownership check and must avoid leaking the protected representation.

## Worked case: authenticated list scope

Alice and Bob use separate client cookie jars. After login, each sees only the record they own. Alice also sends a query parameter asking for Bob's owner value; the endpoint still derives its scope from the authenticated identity and returns Alice's record.

The query parameter is not an authorization mechanism. This fixture ignores it because it is outside the supported filter contract. A larger API may choose to reject unsupported filters explicitly. In either design, a caller must not broaden their authority by adding a field to the request.

Separate clients matter in the test. Reusing one cookie jar while switching user assumptions can accidentally turn both requests into the same authenticated principal and hide an authorization defect.

## Worked case: individual-object refusal

Alice requests Bob's record directly by ID, and Bob requests Alice's. Both receive 404. The program also confirms that an anonymous list request receives 401. These cases test different layers: no authenticated identity, an authenticated identity with a permitted list, and an authenticated identity requesting a forbidden object.

A list endpoint that filters correctly does not automatically protect a separate detail endpoint. Similarly, a protected GET does not automatically secure update or deletion routes. Review every operation that can read or mutate the object, including bulk actions, exports and background-job submission.

## Failure diagnosis

If changing an ID reveals another user's data, inspect the query/lookup predicate rather than trying to hide IDs more carefully. If a list leaks records while detail views are protected, compare their scope logic. If an authorization test passes unexpectedly, verify which client session actually made the request.

Permissions can also change after login. A long-lived token or cached user object may carry stale roles. Decide which checks need current database state and how revocation works. This small ownership fixture does not claim to solve organization-wide identity lifecycle or distributed cache invalidation.

## Interview discussion

**Is a random UUID an authorization control?** It can reduce easy enumeration, but it does not prove the caller is allowed to access the object. The access check remains necessary.

**Where should tenant filtering live?** Keep it explicit and consistently applied at the relevant data/service boundary. Repeated ad hoc filters scattered across handlers are easier to omit; an abstraction still needs tests proving it cannot accidentally broaden scope.

## Next step

Apply similarly explicit ownership to filesystem downloads. A submitted filename must not become authority to read any path the process can access.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    from dataclasses import dataclass

    from flask import Flask, request
    from flask_login import LoginManager, UserMixin, current_user, login_required, login_user
    from werkzeug.security import check_password_hash, generate_password_hash

    @dataclass
    class User(UserMixin):
        id: str
        password_hash: str

    users = {
        name: User(name, generate_password_hash("fixture-password-" + name))
        for name in ("alice", "bob")
    }
    records = {
        1: {"id": 1, "owner": "alice", "title": "A note"},
        2: {"id": 2, "owner": "bob", "title": "B note"},
    }
    app = Flask(__name__)
    app.config.update(TESTING=True, SECRET_KEY="test-only-owner-fixture")
    manager = LoginManager(app)
    manager.user_loader(lambda key: users.get(key))
    manager.unauthorized_handler(lambda: ({"error": "authentication required"}, 401))

    @app.post("/login")
    def login():
        body = request.get_json(silent=True) or {}
        user = users.get(body.get("name"))
        if (
            user is None
            or not isinstance(body.get("password"), str)
            or not check_password_hash(user.password_hash, body["password"])
        ):
            return {"error": "invalid credentials"}, 401
        login_user(user)
        return {"authenticated": True}

    @app.get("/items")
    @login_required
    def items():
        return {"items": [row for row in records.values() if row["owner"] == current_user.id]}

    @app.get("/items/<int:key>")
    @login_required
    def item(key):
        row = records.get(key)
        if row is None or row["owner"] != current_user.id:
            return {"error": "not found"}, 404
        return row

    first, second = app.test_client(), app.test_client()
    assert first.get("/items").status_code == 401
    assert (
        first.post(
            "/login", json={"name": "alice", "password": "fixture-password-alice"}
        ).status_code
        == 200
    )
    assert (
        second.post("/login", json={"name": "bob", "password": "fixture-password-bob"}).status_code
        == 200
    )
    assert [row["id"] for row in first.get("/items?owner=bob").json["items"]] == [1]
    assert [row["id"] for row in second.get("/items").json["items"]] == [2]
    assert first.get("/items/2").status_code == second.get("/items/1").status_code == 404
    return {
        "list_scope_checked": True,
        "object_scope_checked": True,
        "request_owner_is_not_authority": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
