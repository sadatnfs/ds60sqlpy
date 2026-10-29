"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="synthetic-local-fixture",
        DEBUG=False,
        ALLOWED_HOSTS=["testserver"],
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[__name__ + ".outer", __name__ + ".inner"],
    )
    import django

    django.setup()
    from django.http import JsonResponse
    from django.test import Client
    from django.urls import path

    trace = []

    def factory(label):
        def middleware(get_response):
            def call(request):
                trace.append(label + ":before")
                response = get_response(request)
                trace.append(label + ":after")
                response["X-" + label] = "observed"
                return response

            return call

        return middleware

    global outer, inner, urlpatterns
    outer, inner = factory("Outer"), factory("Inner")

    def view(request):
        trace.append("view")
        return JsonResponse({"ok": True})

    def fail(request):
        raise ValueError("private fixture detail")

    urlpatterns = [path("ok/", view), path("fail/", fail)]
    client = Client(raise_request_exception=False)
    assert client.get("/ok/").status_code == 200
    assert trace == ["Outer:before", "Inner:before", "view", "Inner:after", "Outer:after"]
    trace.clear()
    response = client.get("/fail/")
    assert response.status_code == 500 and b"private fixture detail" not in response.content
    assert trace == ["Outer:before", "Inner:before", "Inner:after", "Outer:after"]
    return {"exception_converted_inside_chain": True, "failure_trace": trace}


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
