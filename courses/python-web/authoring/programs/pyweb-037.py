"""Complete finite FastAPI investigation with original bounded fixtures."""

import hmac
import json
import secrets
from typing import Annotated


def run_cases():
    from fastapi import FastAPI, Header, HTTPException, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.testclient import TestClient

    app = FastAPI(docs_url=None, redoc_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://ui.example"],
        allow_credentials=True,
        allow_methods=["POST"],
        allow_headers=["X-CSRF-Token"],
    )
    sessions = {}

    @app.post("/fixture-session")
    def session(response: Response):
        identifier, csrf = secrets.token_urlsafe(24), secrets.token_urlsafe(24)
        sessions[identifier] = csrf
        response.set_cookie("session", identifier, secure=True, httponly=True, samesite="lax")
        return {"csrf": csrf}

    @app.post("/change")
    def change(request: Request, x_csrf_token: Annotated[str | None, Header()] = None):
        expected = sessions.get(request.cookies.get("session"))
        if expected is None:
            raise HTTPException(401, "Session required")
        if (
            request.headers.get("origin") != "https://ui.example"
            or x_csrf_token is None
            or not hmac.compare_digest(expected, x_csrf_token)
        ):
            raise HTTPException(403, "CSRF check failed")
        return {"changed": True}

    with TestClient(app, base_url="https://testserver") as client:
        csrf = client.post("/fixture-session").json()["csrf"]
        headers = {"Origin": "https://ui.example", "X-CSRF-Token": csrf}
        good = client.post("/change", headers=headers)
        assert good.json() == {"changed": True}
        assert good.headers["access-control-allow-origin"] == "https://ui.example"
        assert (
            client.post(
                "/change", headers={"Origin": "https://evil.example", "X-CSRF-Token": csrf}
            ).status_code
            == 403
        )
        assert client.post("/change", headers={"Origin": "https://ui.example"}).status_code == 403
        assert (
            client.options(
                "/change",
                headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
            ).status_code
            == 400
        )
    return {
        "csrf_and_origin_enforced_by_application": True,
        "cookie_flags_declared": True,
        "browser_policy_not_executed": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
