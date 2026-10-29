# pyweb-060: Django caching, email and task interfaces

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-059`.

## Starting point and result

Framework interfaces often stay the same while their backends change the operational meaning. A cache can live in one process or a shared service; email can be captured in memory or delivered through a server; a task can execute eagerly or through a durable worker. This chapter makes those backend distinctions explicit.

## Mechanism: interface success has a scope

Django's cache API provides get, set and delete over a configured backend. A key should include the dimensions that affect its value, such as tenant, user or schema version. The local-memory backend is useful for finite tests but does not provide cross-process coordination or persistence.

The locmem email backend appends messages to an in-process outbox. Send_mail can therefore succeed without sending anything to an external address. This is desirable in a classroom fixture, but it proves message construction and backend acceptance rather than actual SMTP delivery.

Celery eager mode runs a registered task synchronously in the local process. Its task API remains real, yet no independent worker or durable broker is involved. The program prints those limitations directly to prevent a successful method call from being mistaken for service qualification.

## Worked case: cache a value and invalidate it

The program stores a small summary under a versioned user-specific key and retrieves the expected value. It then deletes the key and confirms a cache miss. This checks actual backend behavior and the application's intended invalidation operation.

A cached representation can become stale when underlying data changes. Deleting or versioning the key is part of the write/read contract, not an optional performance detail. A cache keyed only by a global name can also leak one user's result to another if identity affects the value.

The fixture does not claim a distributed cache. If several server processes use separate local-memory backends, each can retain a different value. A correct shared-state design must choose an appropriate backend and define consistency expectations.

## Worked case: inspect email and execute an eager task

Send_mail builds one synthetic message and the test inspects the in-memory outbox's subject and count. The address uses an invalid example domain, and no network mail is sent. A Celery task computes a deterministic summary and its eager result is checked against an independent expected dictionary.

These tests are valuable because message content and task logic can be wrong before any network integration is involved. They are incomplete for delivery and recovery. Actual email acceptance would require a controlled mail service, while durable task acceptance would require broker/worker lifecycle and duplicate-effect checks.

A task should receive serializable values or stable record identities. Passing request objects, database sessions or open files assumes a shared process lifetime that a real worker does not have. The later outbox and workshop chapters use durable identities to cross that boundary.

## Failure diagnosis and discussion

**Why did an email test pass but no message arrive?** The configured backend may capture messages locally, or the test may only prove server acceptance rather than final delivery. Identify the actual backend and observation point.

**Why does a task work eagerly but fail in a worker?** Serialization, imports, environment, process ownership and external dependencies differ. Eager execution bypasses those boundaries.

If cache results cross user boundaries, inspect key design before adding more invalidation. If tasks disappear on restart, inspect durable acceptance and unfinished-work discovery. Continue with deployment checks, which identify configuration risks but likewise need careful interpretation of what they do and do not establish.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="synthetic-local-fixture",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "finite-web-lesson",
            }
        },
    )
    import django

    django.setup()
    from django.core import mail
    from django.core.cache import cache, caches
    from django.core.mail import send_mail

    cache.set("summary:v1:user-1", {"count": 3}, timeout=60)
    assert cache.get("summary:v1:user-1") == {"count": 3}
    cache.delete("summary:v1:user-1")
    assert cache.get("summary:v1:user-1") is None
    assert (
        send_mail(
            "Review ready",
            "Synthetic report body",
            "noreply@example.invalid",
            ["learner@example.invalid"],
        )
        == 1
    )
    assert len(mail.outbox) == 1 and mail.outbox[0].subject == "Review ready"
    from celery import Celery

    queue = Celery("django-finite", broker="memory://", backend="cache+memory://", fixups=[])
    queue.conf.update(task_always_eager=True, task_eager_propagates=True)

    @queue.task
    def summarize(values):
        return {"count": len(values), "total": sum(values)}

    assert summarize.delay([2, 4]).get() == {"count": 2, "total": 6}
    caches.close_all()
    return {
        "cache_invalidation": True,
        "email": "in-memory backend, no mail sent",
        "task": "eager test, no durable worker",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
