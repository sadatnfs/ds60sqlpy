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
    from django.urls import path

    User = get_user_model()

    from rest_framework.authentication import SessionAuthentication
    from rest_framework.pagination import PageNumberPagination
    from rest_framework.permissions import IsAuthenticated
    from rest_framework.test import APIClient
    from rest_framework.throttling import SimpleRateThrottle
    from rest_framework.views import APIView

    class Limited(SimpleRateThrottle):
        rate = "2/min"
        scope = "finite-fixture"

        def get_cache_key(self, request, view):
            return "finite-user:" + str(request.user.pk)

    class Page(PageNumberPagination):
        page_size = 2

    class Notes(APIView):
        authentication_classes = [SessionAuthentication]
        permission_classes = [IsAuthenticated]
        throttle_classes = [Limited]

        def get(self, request):
            paginator = Page()
            page = paginator.paginate_queryset([{"id": i} for i in range(5)], request, view=self)
            return paginator.get_paginated_response(page)

    global urlpatterns
    urlpatterns = [path("notes/", Notes.as_view())]
    client = APIClient()
    assert client.get("/notes/").status_code == 403
    user = User.objects.create_user(username="learner")
    client.force_login(user)
    first = client.get("/notes/").json()
    second = client.get("/notes/?page=2").json()
    assert first["count"] == 5 and first["results"] == [{"id": 0}, {"id": 1}]
    assert second["results"] == [{"id": 2}, {"id": 3}]
    limited = client.get("/notes/")
    assert limited.status_code == 429 and "Retry-After" in limited
    connection.close()
    scratch.cleanup()
    return {
        "pages_checked": 2,
        "throttle_refusal": 429,
        "limit_scope": "single-process cache, not distributed abuse protection",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
