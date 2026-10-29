"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    from dataclasses import dataclass

    from flask import Flask, request
    from flask_login import (
        LoginManager,
        UserMixin,
        current_user,
        login_required,
        login_user,
        logout_user,
    )
    from werkzeug.security import check_password_hash, generate_password_hash

    @dataclass
    class User(UserMixin):
        id: str
        name: str
        password_hash: str

    user = User("1", "Ada", generate_password_hash("fixture-correct-password"))
    app = Flask(__name__)
    app.config.update(TESTING=True, SECRET_KEY="test-only-login-fixture")
    manager = LoginManager(app)

    @manager.user_loader
    def load(identifier):
        return user if identifier == user.id else None

    @manager.unauthorized_handler
    def unauthorized():
        return {"error": "authentication required"}, 401

    @app.post("/login")
    def login():
        body = request.get_json(silent=True) or {}
        if (
            body.get("name") != user.name
            or not isinstance(body.get("password"), str)
            or not check_password_hash(user.password_hash, body["password"])
        ):
            return {"error": "invalid credentials"}, 401
        login_user(user)
        return {"authenticated": True}

    @app.get("/account")
    @login_required
    def account():
        return {"id": current_user.id, "name": current_user.name}

    @app.post("/logout")
    @login_required
    def logout():
        logout_user()
        return "", 204

    with app.test_client() as client:
        assert client.get("/account").status_code == 401
        assert (
            client.post("/login", json={"name": "Ada", "password": "incorrect"}).status_code == 401
        )
        assert (
            client.post(
                "/login", json={"name": "Ada", "password": "fixture-correct-password"}
            ).status_code
            == 200
        )
        assert client.get("/account").json == {"id": "1", "name": "Ada"}
        assert client.post("/logout").status_code == 204
        assert client.get("/account").status_code == 401
    return {
        "anonymous_denied": True,
        "bad_credentials_denied": True,
        "login_and_logout_checked": True,
        "scope": "authentication fixture; combine CSRF and deployment policies in the workshop",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
