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
