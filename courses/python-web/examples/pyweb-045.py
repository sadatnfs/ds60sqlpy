"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="synthetic-local-fixture",
        DEBUG=False,
        ALLOWED_HOSTS=["testserver"],
        ROOT_URLCONF=__name__,
    )
    import django

    django.setup()
    from django.http import JsonResponse
    from django.test import Client
    from django.urls import path, reverse

    def detail(request, identifier):
        return JsonResponse({"identifier": identifier, "method": request.method})

    global urlpatterns
    urlpatterns = [path("notes/<int:identifier>/", detail, name="note-detail")]
    client = Client()
    assert reverse("note-detail", kwargs={"identifier": 7}) == "/notes/7/"
    assert client.get("/notes/7/").json() == {"identifier": 7, "method": "GET"}
    assert client.get("/notes/word/").status_code == 404
    assert client.get("/notes/7/", HTTP_HOST="untrusted.example").status_code == 200
    # A view that never calls get_host does not itself trigger host validation.
    from django.middleware.common import CommonMiddleware

    settings.MIDDLEWARE = ["django.middleware.common.CommonMiddleware"]
    assert CommonMiddleware
    assert Client().get("/notes/7/", HTTP_HOST="untrusted.example").status_code == 400
    return {
        "named_route": reverse("note-detail", kwargs={"identifier": 7}),
        "converter_refusal": 404,
        "host_check_requires_actual_boundary": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
