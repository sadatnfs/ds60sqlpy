"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from flask import Flask, session

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="test-only-cookie-fixture",
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    @app.get("/remember")
    def remember():
        session["visits"] = 1
        return {"remembered": True}

    @app.get("/state")
    def state():
        return {"visits": session.get("visits", 0)}

    with app.test_client() as client:
        response = client.get("/remember", base_url="https://localhost")
        cookie_header = response.headers["Set-Cookie"]
        assert all(flag in cookie_header for flag in ("Secure", "HttpOnly", "SameSite=Lax"))
        assert client.get("/state", base_url="https://localhost").json == {"visits": 1}
        cookie = client.get_cookie("session")
        assert cookie is not None
        client.set_cookie("session", cookie.value + "tampered", secure=True)
        assert client.get("/state", base_url="https://localhost").json == {"visits": 0}
    return {
        "valid_signature_restored_state": True,
        "tampered_cookie_reset_to_anonymous_state": True,
        "declared_cookie_flags": ["Secure", "HttpOnly", "SameSite=Lax"],
        "browser_cookie_policy_executed": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
