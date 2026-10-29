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
