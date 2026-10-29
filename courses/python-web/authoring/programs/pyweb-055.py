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
