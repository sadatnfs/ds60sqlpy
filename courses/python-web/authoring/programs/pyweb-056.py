"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    import tempfile
    from pathlib import Path

    from django.conf import settings

    with tempfile.TemporaryDirectory() as directory:
        settings.configure(
            SECRET_KEY="synthetic-local-fixture",
            DEBUG=False,
            ROOT_URLCONF=__name__,
            ALLOWED_HOSTS=["testserver"],
            STATIC_URL="/static/",
            INSTALLED_APPS=[
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.staticfiles",
            ],
            MIDDLEWARE=[
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": str(Path(directory) / "db.sqlite3"),
                }
            },
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ]
                    },
                }
            ],
        )
        import django

        django.setup()
        from django.contrib import admin
        from django.contrib.auth import get_user_model
        from django.core.management import call_command
        from django.db import connection
        from django.test import Client
        from django.urls import path

        call_command("migrate", verbosity=0)
        User = get_user_model()
        ordinary = User.objects.create_user(username="ordinary")
        staff = User.objects.create_user(username="staff", is_staff=True)
        supervisor = User.objects.create_superuser(
            username="supervisor", email="", password="synthetic-only"
        )
        global urlpatterns
        urlpatterns = [path("admin/", admin.site.urls)]
        client = Client()
        client.force_login(ordinary)
        assert client.get("/admin/").status_code == 302
        client.force_login(staff)
        assert client.get("/admin/").status_code == 200
        assert client.get("/admin/auth/user/").status_code == 403
        client.force_login(supervisor)
        response = client.get("/admin/auth/user/")
        assert response.status_code == 200 and b"/static/admin/" in response.content
        connection.close()
    return {
        "staff_is_not_all_permissions": True,
        "superuser_fixture": True,
        "admin_asset_urls": "rendered only; workshop prepares collectstatic",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
