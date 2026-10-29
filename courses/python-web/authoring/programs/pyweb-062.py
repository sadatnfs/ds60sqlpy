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
