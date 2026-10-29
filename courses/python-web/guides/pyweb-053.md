# pyweb-053: Django authentication, passwords and sessions

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-052`.

## Starting point and result

Authentication combines credential verification with a session that identifies later requests. Django supplies password hashing, authentication backends and session integration, but the application must still connect those pieces correctly. This chapter runs a real password check, login, authenticated request and logout against migrated temporary tables.

## Mechanism: verify a credential, then establish session identity

Create_user hashes the password using the configured password hasher. The stored value is not the original password. Authenticate asks the configured backend to verify the submitted credentials and return a user when allowed. Login records the authenticated user in the session; AuthenticationMiddleware reconstructs request.user on later requests.

SessionMiddleware must run before AuthenticationMiddleware in this standard setup. The database-backed session table is created by actual migrations. A successful password check without a session write would not make an unrelated later request authenticated.

The fixture uses one synthetic password and a temporary database. Its login/logout views are intentionally focused on the authentication mechanism. CSRF enforcement is treated explicitly in chapter 055 and combined in the later walkthrough; this chapter does not claim that a default test client has validated CSRF protections.

## Worked case: authenticate and carry identity across requests

The program creates the user and checks both that the stored password differs from the submitted password and that check_password accepts the original. A client initially receives 401 from the protected me endpoint. Submitting correct credentials to login establishes the session, and the next request returns the expected username.

The same client matters because it retains cookies between calls. Constructing an unrelated client for the second request would omit the session continuity being tested. This is similar to a browser's cookie jar at the framework level, although the test does not establish real browser cookie policy or network transport.

A production login flow also needs account policy, abuse controls, secure transport and safe error messages. Those additions should preserve the core distinction between verifying a password and authorizing a later resource operation.

## Worked case: wrong credentials and logout

A wrong password returns a generic authentication refusal and does not establish identity. After a later successful login, logout removes the authenticated session state. A subsequent protected request again receives 401. The program checks the complete transition sequence rather than only the login response.

A response saying logged out is insufficient if the server still accepts the old session context. Conversely, clearing only a display variable in the frontend does not revoke the server session. The relevant boundary is the framework's session state and how later requests are interpreted.

Password hashing is deliberately computationally costly. Do not replace it with a plain hash or plaintext comparison for production performance. Test fixtures can choose controlled settings, but should clearly distinguish those settings from the deployed security policy.

## Failure diagnosis and discussion

**Why is force_login not used here?** It intentionally bypasses credential verification and is useful for testing authorized views. This chapter specifically needs to test actual authentication, so it exercises authenticate and login.

**Does request.user being authenticated imply access to every record?** No. Permissions and ownership still restrict operations and data. The next chapter demonstrates those separate checks.

If login returns success but later requests are anonymous, inspect cookie continuity, session backend configuration and middleware order. If passwords appear in logs, fix diagnostic handling immediately rather than masking only the response. Continue with groups and object access to apply an established identity safely.

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
    from django.contrib.auth import get_user_model
    from django.db import connection
    from django.http import JsonResponse
    from django.test import Client
    from django.urls import path

    User = get_user_model()

    from django.contrib.auth import authenticate, login, logout

    user = User.objects.create_user(username="learner", password="synthetic password")
    assert user.password != "synthetic password" and user.check_password("synthetic password")

    def enter(request):
        principal = authenticate(
            request, username=request.POST.get("username"), password=request.POST.get("password")
        )
        if principal is None:
            return JsonResponse({"error": "invalid credentials"}, status=401)
        login(request, principal)
        return JsonResponse({"authenticated": True})

    def me(request):
        return (
            JsonResponse({"username": request.user.get_username()})
            if request.user.is_authenticated
            else JsonResponse({"error": "login required"}, status=401)
        )

    def leave(request):
        logout(request)
        return JsonResponse({"logged_out": True})

    global urlpatterns
    urlpatterns = [path("login/", enter), path("me/", me), path("logout/", leave)]
    client = Client()
    assert client.get("/me/").status_code == 401
    assert client.post("/login/", {"username": "learner", "password": "wrong"}).status_code == 401
    assert (
        client.post(
            "/login/", {"username": "learner", "password": "synthetic password"}
        ).status_code
        == 200
    )
    assert client.get("/me/").json() == {"username": "learner"}
    assert client.post("/logout/").status_code == 200
    assert client.get("/me/").status_code == 401
    connection.close()
    scratch.cleanup()
    return {
        "password_hash_verified": True,
        "session_login_logout": True,
        "csrf": "separately exercised in pyweb-055",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
