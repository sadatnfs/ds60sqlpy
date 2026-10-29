# pyweb-058: DRF authentication, pagination and throttling

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-057`.

## Starting point and result

An API collection needs a defined authentication policy, a bounded page size and a considered request-rate policy. This chapter exercises DRF session authentication, page-number pagination and a small per-user throttle through actual APIClient requests. It also states why that throttle is not distributed abuse protection.

## Mechanism: permission, pagination and throttling compose

SessionAuthentication uses Django's authenticated session context. IsAuthenticated restricts the view to an established user. PageNumberPagination divides an ordered collection into pages and returns metadata such as count and next links. A throttle uses a key and rate policy to decide whether another request is admitted.

The fixture's SimpleRateThrottle keys on the authenticated user's identity and permits two requests per minute. Its cache is local to the process. A second worker with independent memory would have independent counters, and concurrent updates can have limitations. Production abuse controls need an explicitly shared, suitably atomic design at the relevant boundary.

Authentication failure status can depend on the authentication class's challenge behavior. Under this session-auth configuration, the anonymous request receives 403. That observed result should not be rewritten to match the bearer-token 401 examples from another framework.

## Worked case: retrieve two authenticated pages

The anonymous request is refused. A synthetic user is then logged into the client through force_login, isolating this chapter from password verification. The first page returns two records and a total count of five; the second returns the next two records.

The assertions check exact page contents as well as count. Pagination metadata alone can look correct while row ordering or slicing is wrong. A database-backed API should define deterministic ordering, especially if clients will request successive pages while new rows are added.

Page-number pagination is easy to understand, but offsets can shift under concurrent inserts/deletes. Cursor or keyset pagination offers different guarantees and costs. Choose based on the collection's mutation pattern and the client's navigation needs rather than treating one pagination class as universal.

## Worked case: the third request reaches the throttle

After the two allowed requests, a third receives 429 and a Retry-After header. The test verifies the actual throttle decision rather than checking only configuration strings. It does not wait a minute or claim a timing benchmark.

The result applies to one authenticated identity in one process-local cache. It is not a statement about global quotas across multiple containers, proxy-level connection limits or malicious distributed clients. A rate-limit design should define its identity, window/bucket semantics, atomicity and behavior when the coordination store fails.

Throttling should not be used to hide inefficient queries or unbounded response sizes. Those require their own limits and performance work. A small request rate can still cause severe load if each request performs an expensive uncontrolled operation.

## Failure diagnosis and discussion

**Why do limits reset after restarting a worker?** A local-memory backend has no durable or shared state. The storage choice is part of the rate-limit contract.

**Why is a throttled response not proof of authentication failure?** The caller can be authenticated and authorized but temporarily exceed an operational budget. Clients should handle that condition according to the API's retry policy.

If pages duplicate or skip rows, inspect ordering and mutation semantics. If the throttle never triggers, inspect its key, cache backend and request path. Continue with Django async views to understand how these request layers interact with synchronous and asynchronous database operations.

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
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
