# pyweb-055: Django CSRF and session security

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-054`.

## Starting point and result

Django's normal test client relaxes CSRF checks for convenience. That makes it unsuitable for claiming CSRF protection unless enforcement is explicitly enabled. This chapter uses enforce_csrf_checks, obtains a real framework token and verifies both token and origin refusals before a state-changing view runs.

## Mechanism: middleware validates request context

CsrfViewMiddleware applies the framework's protection to relevant unsafe requests. The token flow connects a value supplied by the application with the browser's stored context and submitted form/header. Origin and, in applicable secure contexts, referer checks help constrain the initiating context.

The example obtains its token through get_token and sends it as X-CSRFToken. It keeps the same client so its cookie state is preserved. A token copied from another context or a client that discards the relevant cookie may fail even when the visible token string looks plausible.

The view itself accepts only POST for mutation and records an effect only after middleware has admitted the request. A GET should not silently perform the same state change merely to avoid CSRF enforcement. Safe-method semantics and CSRF policy support each other rather than serving as interchangeable shortcuts.

## Worked case: obtain and submit a valid token

The client first requests the token endpoint. It then submits a protected POST with the returned token header. The request succeeds and the effects list gains one entry. This is actual framework token validation with the test client's CSRF bypass disabled.

The token endpoint is part of this finite fixture's explicit flow. A rendered HTML form commonly embeds the token through Django's template mechanisms instead. JavaScript clients need an equally deliberate way to obtain and submit the framework token while respecting cookie and origin settings.

The successful request does not establish real browser SameSite behavior or TLS. It verifies Django's request processing under controlled inputs. The owned workshop adds actual browser/network observations and must keep those results separate from this in-process evidence.

## Worked case: missing token and wrong origin

A POST without a token receives 403. A later POST with the valid token but an untrusted Origin also receives 403. The final effects list still contains only the one allowed mutation, proving that both refused requests were stopped before the view's effect.

This state assertion matters because a response code alone can hide incorrect side-effect ordering. If a custom integration mutates data before performing its own CSRF check, returning 403 afterward does not repair the unauthorized change.

A trusted-origin setting should name deliberately supported origins, not become a broad list added until tests pass. Scheme, host and port matter. Proxy/TLS configuration must also reflect the actual network boundary so the framework interprets secure requests correctly.

## Failure diagnosis and discussion

**Why did an ordinary client test pass without a token?** The default test client bypasses this protection. Use enforce_csrf_checks for a test whose claim is specifically CSRF behavior.

**Can CORS replace CsrfViewMiddleware?** No. CORS concerns browser access to cross-origin responses and certain request modes; it is not the same state-changing-request defense.

If a legitimate form fails after login, inspect whether its token/session context changed and obtain a fresh token through the supported flow. If only deployment fails, inspect trusted origins and proxy security settings rather than exempting the view. Continue with the admin, where CSRF, authentication and permissions surround a particularly privileged application.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    import tempfile
    from pathlib import Path

    from django.conf import settings

    scratch = tempfile.TemporaryDirectory()
    settings.configure(
        SECRET_KEY="synthetic-local-fixture",
        DEBUG=False,
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=["testserver"],
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(Path(scratch.name) / "db.sqlite3"),
            }
        },
        PASSWORD_HASHERS=["django.contrib.auth.hashers.PBKDF2PasswordHasher"],
    )
    import django

    django.setup()
    from django.core.management import call_command

    call_command("migrate", verbosity=0)
    from django.db import connection
    from django.http import JsonResponse
    from django.middleware.csrf import get_token
    from django.test import Client
    from django.urls import path

    settings.MIDDLEWARE = [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ]
    changes = []

    def token(request):
        return JsonResponse({"csrf": get_token(request)})

    def write(request):
        if request.method != "POST":
            return JsonResponse({"error": "POST required"}, status=405)
        changes.append("saved")
        return JsonResponse({"saved": True})

    global urlpatterns
    urlpatterns = [path("token/", token), path("write/", write)]
    client = Client(enforce_csrf_checks=True)
    assert client.post("/write/").status_code == 403
    csrf = client.get("/token/").json()["csrf"]
    assert client.post("/write/", HTTP_X_CSRFTOKEN=csrf).status_code == 200
    assert (
        client.post(
            "/write/", HTTP_X_CSRFTOKEN=csrf, HTTP_ORIGIN="https://evil.example"
        ).status_code
        == 403
    )
    assert changes == ["saved"]
    connection.close()
    scratch.cleanup()
    return {
        "missing_token": 403,
        "wrong_origin": 403,
        "effects": 1,
        "default_test_client_bypass_avoided": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
