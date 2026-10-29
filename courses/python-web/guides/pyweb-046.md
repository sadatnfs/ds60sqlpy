# pyweb-046: Django middleware and request lifecycle

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-045`.

## Starting point and result

Middleware wraps the view with behavior that can inspect requests and responses. Ordering determines which component sees an input first and which sees the response last. This chapter records the real Django middleware sequence for a successful view and for a view that raises an exception.

## Mechanism: nested wrappers form a request pipeline

A middleware factory receives get_response and returns a callable. That callable performs work before invoking the next component, then can inspect or modify the response afterward. With an outer and inner middleware, the request travels outer-to-inner-to-view; the response returns view-to-inner-to-outer.

This nesting is why middleware ordering is part of application behavior. Session middleware must prepare session state before components that use it. Authentication middleware relies on session handling in a standard session-auth configuration. Security headers, compression and caching can also interact according to their positions.

Django places exception-to-response handling around relevant stages. A view exception may therefore be converted into an HTTP response before an outer middleware's after section runs. That is different from assuming every view exception propagates unchanged through all wrapper functions. The example observes the actual behavior instead of relying on a generic decorator analogy.

## Worked case: trace a successful request

The two middleware record before and after markers. The view records its own marker and returns JSON. The expected order is Outer before, Inner before, view, Inner after, Outer after. The program asserts the complete sequence and the successful response.

The middleware also adds response headers, showing that after work can modify the returned representation. In a real application, such headers should have clear ownership to avoid multiple layers overwriting each other unpredictably. A trace test can reveal accidental ordering changes during refactoring.

The list is deliberately local to one finite test. Production request traces need correlation identities and concurrency-safe observation. A shared global list is not a suitable tracing backend for a multi-worker service, and this example does not advertise it as one.

## Worked case: a view failure still yields a response path

The second view raises an exception containing private diagnostic text. The client is configured to observe the resulting HTTP response rather than reraising the exception to the test. It receives 500, and both middleware after markers still appear in the expected reverse order.

The public response does not contain the private diagnostic phrase. That assertion distinguishes safe public handling from internal error visibility. Production logs can retain a controlled traceback and request identity without exposing those details to the caller.

A middleware that needs cleanup regardless of all possible errors should still use appropriate finally/context-manager ownership. The observed view-exception conversion does not justify assuming that every failure inside middleware initialization, streaming iteration or external cleanup will behave identically.

## Failure diagnosis and discussion

**Why did adding middleware change authentication behavior?** Its position may alter when session or user state exists. Read the required ordering of each component and test the actual chain.

**Why might an after hook see 500 instead of catching the original exception?** Django may have converted the downstream exception to a response. Use the framework's documented exception hooks or logging behavior for the diagnostic you need.

When debugging order, record safe stage names and statuses rather than copying request bodies. If a response header disappears, inspect every layer that can replace the response. Continue with templates, where composition has a different structure but similarly requires explicit escaping and asset boundaries.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
