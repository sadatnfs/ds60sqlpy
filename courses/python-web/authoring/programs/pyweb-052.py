"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="synthetic-local-fixture",
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=["testserver"],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "OPTIONS": {
                    "loaders": [
                        (
                            "django.template.loaders.locmem.Loader",
                            {"notes.html": "{% for note in object_list %}{{ note }};{% endfor %}"},
                        )
                    ]
                },
            }
        ],
    )
    import django

    django.setup()
    from django.http import JsonResponse
    from django.test import Client
    from django.urls import path
    from django.views import View
    from django.views.generic import ListView

    class Notes(ListView):
        template_name = "notes.html"
        paginate_by = 2

        def get_queryset(self):
            return ["alpha", "beta", "gamma"]

    class GuardMixin:
        def dispatch(self, request, *args, **kwargs):
            if request.headers.get("X-Fixture-Key") != "allowed":
                return JsonResponse({"error": "forbidden"}, status=403)
            return super().dispatch(request, *args, **kwargs)

    class Guarded(GuardMixin, View):
        def get(self, request):
            return JsonResponse({"allowed": True})

    global urlpatterns
    urlpatterns = [path("notes/", Notes.as_view()), path("guarded/", Guarded.as_view())]
    client = Client()
    assert client.get("/notes/").content == b"alpha;beta;"
    assert client.get("/notes/?page=2").content == b"gamma;"
    assert client.get("/notes/?page=99").status_code == 404
    assert client.get("/guarded/").status_code == 403
    assert client.get("/guarded/", headers={"X-Fixture-Key": "allowed"}).json() == {"allowed": True}
    return {
        "list_pages": 2,
        "mixin_dispatch_guard": True,
        "identity": "synthetic header seam, not authentication",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
