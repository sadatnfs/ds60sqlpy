# pyweb-062: Django application walkthrough

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-061`.

## Starting point and result

The Django branch culminates in a small authenticated notes flow using real models, ModelForms, sessions and CSRF middleware. The program tests successful creation, owner-scoped listing and refused writes, then inspects the actual row count. It keeps password verification and deployment acceptance as separately identified evidence.

## Mechanism: use trusted identity throughout the write

The model stores a title and a foreign key to the user. The ModelForm exposes only title. The view requires an authenticated user, rejects unexpected POST keys, validates the form, constructs the object with commit=False and assigns request.user as owner before saving.

The list path filters by the same authenticated owner. This keeps collection visibility aligned with creation semantics. A real application also needs equivalent detail/update/delete scoping and a transaction design for operations involving several models.

Clients use enforce_csrf_checks so the test does not bypass the middleware. They use force_login to establish known principals because password verification has its own complete chapter. These choices make the claim precise: this test qualifies composed authorization, CSRF and persistence behavior under established identities.

## Worked case: create a note and list it as the owner

Alice's client obtains a real CSRF token and posts a valid title. The view saves one row owned by Alice and returns 201. Alice's subsequent list contains that row, while Bob's list is empty.

The database relationship is real, and the model table is prepared inside an explicitly disposable fixture. The program also runs the framework migrations needed by authentication and sessions. It does not pretend that the compact schema setup for the teaching model is a reviewed production migration history.

The successful sequence demonstrates that the token, cookie session, request.user and database owner agree. Testing those pieces only in isolation could miss an integration mistake such as using an anonymous identity after session setup or assigning owner from the submitted form.

## Worked case: missing CSRF and attempted owner assignment

A POST without the token is refused with 403 before mutation. Another POST includes owner as an unexpected field and is refused with 400. The final database count remains one, so neither refused request created a hidden row.

The explicit unknown-key check complements ModelForm's writable-field list. ModelForms normally ignore undeclared keys; this endpoint chooses a stricter API-like policy and tests it. The title field remains validated by the form rather than by a separate inconsistent string check.

Bob's empty list also illustrates collection authorization. A detail route that checks ownership is insufficient if the collection endpoint returns all rows. Authorization must be consistent across each way of reading or modifying the resource.

## Failure diagnosis and discussion

**Why is there both a fields list and an unexpected-key check?** They express different contracts. The fields list limits what the form can write; the key check makes attempts to supply other fields visibly invalid for this endpoint.

**Why inspect the database after refused requests?** It verifies the absence of unauthorized side effects. Correct response codes alone cannot establish that storage remained unchanged.

If a valid POST fails after login, inspect token freshness and client cookie continuity. If the wrong owner is stored, inspect where request.user is obtained and assigned. If restart loses data, inspect database placement relative to the container rather than changing form code.

Continue with the shared engineering chapters. They address deadlines, retries, outboxes, database contention, observability and deployment across all three frameworks, using the same distinction between a declared contract and its actual runtime evidence.

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

    from django import forms
    from django.db import models
    from django.middleware.csrf import get_token

    settings.MIDDLEWARE = [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ]

    class Note(models.Model):
        title = models.CharField(max_length=40)
        owner = models.ForeignKey(User, on_delete=models.CASCADE)

        class Meta:
            app_label = "webfixture"

    class Form(forms.ModelForm):
        class Meta:
            model = Note
            fields = ["title"]

    with connection.schema_editor() as editor:
        editor.create_model(Note)
    alice = User.objects.create_user(username="alice")
    bob = User.objects.create_user(username="bob")

    def token(request):
        return JsonResponse({"csrf": get_token(request)})

    def notes(request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "login required"}, status=401)
        if request.method == "POST":
            if set(request.POST) != {"title"}:
                return JsonResponse({"error": "unexpected fields"}, status=400)
            form = Form(request.POST)
            if not form.is_valid():
                return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
            note = form.save(commit=False)
            note.owner = request.user
            note.save()
            return JsonResponse({"id": note.pk, "title": note.title}, status=201)
        return JsonResponse(
            {
                "notes": list(
                    Note.objects.filter(owner=request.user).values("id", "title").order_by("id")
                )
            }
        )

    global urlpatterns
    urlpatterns = [path("token/", token), path("notes/", notes)]
    a, b = Client(enforce_csrf_checks=True), Client(enforce_csrf_checks=True)
    a.force_login(alice)
    b.force_login(bob)
    csrf = a.get("/token/").json()["csrf"]
    assert a.post("/notes/", {"title": "Private"}, HTTP_X_CSRFTOKEN=csrf).status_code == 201
    assert a.post("/notes/", {"title": "Missing token"}).status_code == 403
    assert (
        a.post(
            "/notes/", {"title": "Wrong owner", "owner": str(bob.pk)}, HTTP_X_CSRFTOKEN=csrf
        ).status_code
        == 400
    )
    assert len(a.get("/notes/").json()["notes"]) == 1 and b.get("/notes/").json() == {"notes": []}
    assert Note.objects.count() == 1
    connection.close()
    scratch.cleanup()
    return {
        "model_form_csrf_and_owner_filter": True,
        "stored_rows": 1,
        "login": "force_login seam; passwords covered separately",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
