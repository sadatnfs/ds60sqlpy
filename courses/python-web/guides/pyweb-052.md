# pyweb-052: Django class-based views and composition

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-051`, `python-12`.

## Starting point and result

Django class-based views package common request patterns into reusable classes. Their convenience depends on understanding dispatch, inheritance and the methods a generic view calls. This chapter uses a real ListView for pagination and a small mixin that guards a separate view before its handler runs.

## Mechanism: as_view creates the callable boundary

A URL pattern needs a callable. The class's as_view method produces one that creates and dispatches the view for a request. Dispatch selects the method handler, such as get or post. Generic views add hooks for obtaining objects, choosing templates and building context.

A ListView obtains a collection through get_queryset, optionally paginates it and renders a template. Despite the method name, the fixture can return a bounded list so the pagination mechanism is visible without a database. A real QuerySet adds lazy evaluation and query planning considerations from the preceding chapters.

A mixin participates in Python's method resolution order. A guard placed before the base View can check a condition and then call super().dispatch to continue the chain. Failing to call super, or placing classes in an inappropriate order, can bypass expected behavior or prevent the handler from running.

## Worked case: paginate a complete three-item collection

The ListView returns three named items and uses a page size of two. The first page renders two items; the second renders the remaining item. An out-of-range page receives 404. The assertions inspect the actual rendered content and refusal behavior.

The template is loaded from a controlled in-memory loader for this finite program. It uses the object_list context supplied by ListView. A normal application stores the template in its project/application structure, but the generic view's context and pagination behavior are the same mechanisms.

Ordering must be stable when pagination covers database rows. Without a defined order, rows may move between requests even when the page number is unchanged. For frequently changing large datasets, keyset pagination may provide a different and more suitable contract than page-number offsets.

## Worked case: guard dispatch before the handler

The second view combines GuardMixin and View. A request without the synthetic fixture header is refused with 403. A request with the expected value proceeds through super().dispatch and reaches get, returning the successful JSON body.

The header is explicitly a test seam, not authentication. Its purpose is to expose composition order. Real authentication should use Django's established user/session machinery or another reviewed principal boundary, and object permissions still need resource-specific checks.

Mixins should have narrow, documented responsibilities. A class with many overlapping dispatch overrides can become difficult to reason about. Trace the method resolution order and request sequence when behavior is unclear rather than adding another override until tests happen to pass.

## Failure diagnosis and discussion

**Why does a class-based view fail when passed directly to path?** The URL resolver expects the request callable created by as_view, not an uninstantiated class following a different call convention.

**Can a permission mixin replace scoped get_queryset?** Not necessarily. An operation-level permission can admit the view while its queryset still needs to restrict which objects the user can see.

If the wrong template or context appears, inspect the generic view's hook methods and inherited attributes. If a guard never runs, inspect class order and super calls. Continue with actual authentication so the principal consumed by such view composition is established through tested password and session behavior.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
