# pyweb-026: Flask application walkthrough

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-025`.

## Starting point and result

The preceding chapters examined individual mechanisms. This walkthrough combines several in one complete Flask fixture: a login flow, CSRF validation, parameterized SQLite storage and server-assigned ownership. The program uses a temporary database and real client requests, then inspects the final stored rows.

## Mechanism: compose boundaries without weakening them

The application owns its database path and test-only signing key. A CSRF endpoint supplies the framework token. Login verifies a hashed password, clears prior session state and records the authenticated user. The client obtains a fresh token after login because clearing the session changes the token's associated context.

The notes endpoint derives identity from the session. It accepts a bounded title and assigns ownership on the server. SQLite parameters carry both the owner and title as data rather than SQL syntax. A context-managed connection commits a successful insert and closes cleanly.

This fixture has one synthetic account and intentionally small behavior. Its purpose is to verify that the composed mechanisms agree. The owned multi-file workshop adds deployment configuration, persistent service storage, real HTTP and broader lifecycle acceptance.

## Worked case: an authenticated protected write

An anonymous note listing is refused with 401. The client retrieves a CSRF token and submits correct credentials through a protected POST. After login it retrieves a new token, then creates a note with that header. The response is 201, and the subsequent listing returns the intended note.

The program also queries the database after the client context closes. This confirms that the intended owner/title pair was committed to the fixture file. It does not claim that the temporary file will survive the end of the program; its lifecycle is explicitly owned and disposable.

The fresh-token step is meaningful. Tests that bypass CSRF or carry a token from an obsolete session can hide the integration behavior that a browser user will encounter. Here the token is obtained from the real application flow each time its context changes.

## Worked case: missing CSRF and attempted owner assignment

A POST without the CSRF header receives 400 and does not create a note. Another request includes a client-supplied owner field and receives 422 because the write schema accepts only title. The final database still contains only the authorized note.

These checks complement each other. CSRF refusal controls the protected request flow. Schema validation limits writable fields. Authentication provides identity. Server-side ownership assignment scopes stored data. None should be treated as an automatic replacement for the others.

A larger application must also check ownership on individual read/update/delete routes, coordinate concurrent transactions and handle account lifecycle. The prior ownership chapter and the later shared engineering chapters extend those contracts.

## Failure diagnosis

If login succeeds but the next protected POST fails, inspect cookie continuity and whether the session/token context changed. If a rejected request still leaves a row, inspect transaction placement and whether validation occurred before mutation. If user-controlled text changes a query's meaning, inspect parameter binding rather than adding ad hoc string replacements.

Keep test scope explicit. A TestClient run can validate application composition without exercising Gunicorn, network ports, browser assets or TLS. The workshop tests those additional layers and checks persistent state through stop/resume. They should not be inferred from this finite fixture's success.

## Interview discussion

**What does the final database assertion add?** It checks the effect of the request sequence, including that refused writes did not silently mutate storage. Response codes alone can miss incorrect side effects.

**Why clear session state at login?** It provides an intentional transition between anonymous and authenticated context. Any state deliberately carried across that boundary should have a reviewed purpose rather than surviving accidentally.

## Next step

Continue with FastAPI's typed contracts or Django's project conventions. The shared HTTP, authentication and transaction principles remain relevant even when the framework supplies different abstractions.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    import sqlite3
    import tempfile
    from pathlib import Path

    from flask import Flask, request, session
    from flask_wtf.csrf import CSRFProtect, generate_csrf
    from werkzeug.security import check_password_hash, generate_password_hash

    with tempfile.TemporaryDirectory(prefix="pyweb-flask-app-") as directory:
        path = Path(directory) / "app.sqlite3"
        with sqlite3.connect(path) as db:
            db.execute(
                "CREATE TABLE notes "
                "(id INTEGER PRIMARY KEY, owner TEXT NOT NULL, title TEXT NOT NULL)"
            )
        password = generate_password_hash("fixture-password")
        app = Flask(__name__)
        app.config.update(TESTING=True, SECRET_KEY="test-only-integrated-fixture")
        CSRFProtect(app)

        @app.get("/csrf")
        def csrf():
            return {"token": generate_csrf()}

        @app.post("/login")
        def login():
            body = request.get_json(silent=True) or {}
            if (
                body.get("name") != "alice"
                or not isinstance(body.get("password"), str)
                or not check_password_hash(password, body["password"])
            ):
                return {"error": "invalid credentials"}, 401
            session.clear()
            session["user"] = "alice"
            return {"authenticated": True}

        @app.route("/notes", methods=["GET", "POST"])
        def notes():
            user = session.get("user")
            if user is None:
                return {"error": "authentication required"}, 401
            with sqlite3.connect(path) as db:
                if request.method == "POST":
                    body = request.get_json(silent=True)
                    if (
                        not isinstance(body, dict)
                        or set(body) != {"title"}
                        or not isinstance(body["title"], str)
                        or not 1 <= len(body["title"]) <= 80
                    ):
                        return {"error": "bounded title required"}, 422
                    db.execute("INSERT INTO notes(owner,title) VALUES(?,?)", (user, body["title"]))
                    return {"created": True}, 201
                return {
                    "notes": [
                        {"id": row[0], "title": row[1]}
                        for row in db.execute(
                            "SELECT id,title FROM notes WHERE owner=? ORDER BY id", (user,)
                        )
                    ]
                }

        with app.test_client() as client:
            assert client.get("/notes").status_code == 401
            token = client.get("/csrf").json["token"]
            assert (
                client.post(
                    "/login",
                    json={"name": "alice", "password": "fixture-password"},
                    headers={"X-CSRFToken": token},
                ).status_code
                == 200
            )
            token = client.get("/csrf").json["token"]
            assert (
                client.post(
                    "/notes", json={"title": "kept note"}, headers={"X-CSRFToken": token}
                ).status_code
                == 201
            )
            assert client.post("/notes", json={"title": "unprotected"}).status_code == 400
            assert (
                client.post(
                    "/notes", json={"title": "x", "owner": "bob"}, headers={"X-CSRFToken": token}
                ).status_code
                == 422
            )
            assert client.get("/notes").json == {"notes": [{"id": 1, "title": "kept note"}]}
        with sqlite3.connect(path) as db:
            assert db.execute("SELECT owner,title FROM notes").fetchall() == [
                ("alice", "kept note")
            ]
        return {
            "authentication": True,
            "csrf": True,
            "parameterized_storage": True,
            "owner_assignment": True,
            "surface": "finite Flask client and temporary SQLite; deployment is separate",
        }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
