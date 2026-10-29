# pyweb-037: Cookies, CSRF, CORS and browser origins

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-036`.

## Starting point and result

Cookies, CSRF protections and CORS address different browser behaviors. Confusing them can leave a state-changing route exposed even when a preflight request looks restricted. This chapter combines a synthetic session cookie with an unpredictable session-bound CSRF token and an explicit origin check.

## Mechanism: browser policy and application authorization differ

A browser may attach cookies automatically to requests according to cookie attributes and its origin/site rules. A CSRF defense protects an authenticated state-changing action from requests initiated through an untrusted context. CORS controls whether browser JavaScript from another origin may access particular cross-origin responses and request modes. It is not general authentication and does not stop every request from being sent.

The fixture sets Secure, HttpOnly and SameSite attributes on the session cookie. It stores a random CSRF token against that session and compares the submitted header with constant-time comparison. The state-changing route also requires the expected origin. These application checks run even if a caller bypasses browser CORS enforcement entirely.

The session-creation endpoint is explicitly a fixture convenience, not a password login flow. A real system would establish its authenticated session after a reviewed login and account policy. Tests use an HTTPS base URL to exercise cookie handling, but no real TLS connection is established by TestClient.

## Worked case: an allowed protected change

The client obtains a session cookie and its CSRF token, then sends a POST with the allowed Origin and token header. The application accepts the action and the CORS middleware supplies the expected allow-origin response header.

The test asserts both application success and the header. These are distinct observations: the route's decision proves its own checks, while the header describes what a conforming browser may expose to the initiating JavaScript. One observation cannot substitute for the other.

An explicit origin allowlist is important when credentials are involved. Reflecting arbitrary origins while allowing credentials would defeat the intended boundary. The exact scheme, host and port define an origin; similar-looking names are not automatically equivalent.

## Worked case: a missing token and an untrusted origin

A request with the correct session but no CSRF token is refused. Another request supplies the token from an untrusted origin and is also refused. A disallowed preflight receives a separate refusal from CORS middleware.

The application-level refusals are useful because a nonbrowser client can send headers directly and because some browser request forms do not require the same preflight path. The security claim should be about the actual state-changing operation, not merely about a successful OPTIONS test.

SameSite cookies can reduce some cross-site request risks, but site and origin are different concepts and browser behavior has exceptions. They should not be presented as a universal replacement for a framework's CSRF protections. The Django and Flask branches show their established CSRF integrations as well.

## Failure diagnosis and discussion

**Why does a request work in an API client but fail in the browser?** The browser may enforce CORS or cookie policy that the client does not. Inspect the preflight, credentials mode, cookie attributes and exact origin separately.

**Why is a CSRF token not an API bearer token?** It normally proves continuity with a browser session and its request context. A bearer credential independently authorizes whoever possesses it under the API's authentication policy.

This finite test checks server decisions and declared headers, not a real browser's cookie or CORS enforcement. The owned workshop's browser acceptance covers that additional surface. Continue with scopes and ownership so an authenticated request is limited to its permitted data.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
