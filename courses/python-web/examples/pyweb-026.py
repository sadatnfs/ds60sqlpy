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
