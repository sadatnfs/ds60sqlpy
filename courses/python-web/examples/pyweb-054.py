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

    from django.contrib.auth.models import Group, Permission

    alice = User.objects.create_user(username="alice")
    bob = User.objects.create_user(username="bob")
    group = Group.objects.create(name="Editors")
    permission = Permission.objects.get(codename="change_user", content_type__app_label="auth")
    group.permissions.add(permission)
    alice.groups.add(group)
    assert User.objects.get(pk=alice.pk).has_perm("auth.change_user")
    assert not bob.has_perm("auth.change_user")
    owned = {1: {"owner": alice.pk, "title": "Private"}}

    def detail(request, identifier):
        row = owned.get(identifier)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "login required"}, status=401)
        if row is None or row["owner"] != request.user.pk:
            return JsonResponse({"error": "missing"}, status=404)
        return JsonResponse({"title": row["title"]})

    global urlpatterns
    urlpatterns = [path("notes/<int:identifier>/", detail)]
    a, b = Client(), Client()
    a.force_login(alice)
    b.force_login(bob)
    assert a.get("/notes/1/").status_code == 200 and b.get("/notes/1/").status_code == 404
    assert not alice.has_perm("auth.change_user", bob)
    connection.close()
    scratch.cleanup()
    return {
        "group_permission": True,
        "object_scope_explicit": True,
        "default_backend_object_permission": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
