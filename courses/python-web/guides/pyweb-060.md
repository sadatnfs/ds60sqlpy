# pyweb-060: Django caching, email and task interfaces

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-059`.

## Starting point and result

Framework interfaces often stay the same while their backends change the operational meaning. A cache can live in one process or a shared service; email can be captured in memory or delivered through a server; a task can execute eagerly or through a durable worker. This chapter makes those backend distinctions explicit.

## Key terms

- **Cache backend:** The configured storage behind Django's cache API; the local-memory backend is private to one process and is not persistent.
- **Cache key:** The name a value is stored under, which must include every dimension that changes the value, such as tenant or version.
- **Email backend:** The component that receives messages from `send_mail`; the locmem backend stores them in `mail.outbox` instead of sending them.
- **Tasks framework:** Django's `django.tasks` interface in which `enqueue()` returns a TaskResult; the default ImmediateBackend runs the task at once in-process.
- **Durable worker:** A separate process that runs queued tasks from persistent storage, which none of these development backends provide.

## Mechanism: interface success has a scope

Django's cache API provides get, set and delete over a configured backend. A key should include the dimensions that affect its value, such as tenant, user or schema version. The local-memory backend is useful for finite tests but does not provide cross-process coordination or persistence.

The locmem email backend appends messages to an in-process outbox. Send_mail can therefore succeed without sending anything to an external address. This is desirable in a classroom fixture, but it proves message construction and backend acceptance rather than actual SMTP delivery.

Django 6.0 added a built-in Tasks framework in `django.tasks`. The `TASKS` setting names a backend, `task()` turns a module-level function into a `Task`, and `enqueue()` returns a `TaskResult` whose `status` and `return_value` you can inspect. Django ships only development backends: `ImmediateBackend`, the default, runs the task synchronously in the calling process, and `DummyBackend` stores results without running anything. Durable background execution needs a third-party backend and its own worker process. The framework still enforces two worker-facing rules: the task function must be defined at module level so a worker can import it by path, and arguments must be JSON-compatible values.

Celery eager mode runs a registered task synchronously in the local process. Its task API remains real, yet no independent worker or durable broker is involved. The program prints those limitations directly to prevent a successful method call from being mistaken for service qualification.

## Worked case: cache a value and invalidate it

The program stores a small summary under a versioned user-specific key and retrieves the expected value. It then deletes the key and confirms a cache miss. This checks actual backend behavior and the application's intended invalidation operation.

A cached representation can become stale when underlying data changes. Deleting or versioning the key is part of the write/read contract, not an optional performance detail. A cache keyed only by a global name can also leak one user's result to another if identity affects the value.

The fixture does not claim a distributed cache. If several server processes use separate local-memory backends, each can retain a different value. A correct shared-state design must choose an appropriate backend and define consistency expectations.

## Worked case: inspect email and execute an eager task

Send_mail builds one synthetic message and the test inspects the in-memory outbox's subject and count. The address uses an invalid example domain, and no network mail is sent. The same summary function then runs twice. As a Django task under `ImmediateBackend`, `enqueue([2, 4])` returns a result whose status is `SUCCESSFUL` and whose return value matches the expected dictionary; enqueueing a Python set fails with `TypeError` because a set is not JSON-compatible, and wrapping a function nested inside `run_cases` raises `InvalidTask`. As a Celery task in eager mode, its result is checked against the same independent expected dictionary.

These tests are valuable because message content and task logic can be wrong before any network integration is involved. They are incomplete for delivery and recovery. Actual email acceptance would require a controlled mail service, while durable task acceptance would require broker/worker lifecycle and duplicate-effect checks.

A task should receive serializable values or stable record identities. Passing request objects, database sessions or open files assumes a shared process lifetime that a real worker does not have. The later outbox and workshop chapters use durable identities to cross that boundary.

## Worked example: bumping a cache version instead of deleting keys

```python
store = {}


def make_key(key, key_prefix="", version=1):
    return f"{key_prefix}:{version}:{key}"


store[make_key("summary:user-1")] = {"count": 3}
print(list(store))
print(store.get(make_key("summary:user-1", version=2)))
```

Expected output:

```text
[':1:summary:user-1']
None
```

`make_key` matches Django's default key function, so every `cache.set` really stores `prefix:version:key`. Reading with `version=2` misses the old entry without a delete, which lets a deploy that changes the cached summary's shape stop reading stale values at once. The lesson's explicit `cache.delete` remains the right tool for one user's data after a write.

## Failure diagnosis and discussion

**Why did an email test pass but no message arrive?** The configured backend may capture messages locally, or the test may only prove server acceptance rather than final delivery. Identify the actual backend and observation point.

**Why does a task work eagerly but fail in a worker?** Serialization, imports, environment, process ownership and external dependencies differ. Eager execution bypasses those boundaries.

If cache results cross user boundaries, inspect key design before adding more invalidation. If tasks disappear on restart, inspect durable acceptance and unfinished-work discovery. Continue with deployment checks, which identify configuration risks but likewise need careful interpretation of what they do and do not establish.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python isolated
"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def summarize_values(values):
    """Task body; django.tasks accepts only module-level functions."""
    return {"count": len(values), "total": sum(values)}


def run_cases():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="synthetic-local-fixture",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        TASKS={"default": {"BACKEND": "django.tasks.backends.immediate.ImmediateBackend"}},
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
    from django.tasks import TaskResultStatus, task
    from django.tasks.exceptions import InvalidTask

    summarize_task = task(summarize_values)
    result = summarize_task.enqueue([2, 4])
    assert result.status == TaskResultStatus.SUCCESSFUL
    assert result.return_value == {"count": 2, "total": 6}
    try:
        summarize_task.enqueue({2, 4})
    except TypeError:
        rejected_set_argument = True
    else:
        rejected_set_argument = False
    assert rejected_set_argument

    def nested(values):
        return values

    try:
        task(nested)
    except InvalidTask:
        rejected_nested_function = True
    else:
        rejected_nested_function = False
    assert rejected_nested_function
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
        "django_task": {
            "backend": "ImmediateBackend, runs in this process",
            "status": str(result.status),
            "rejected_set_argument": rejected_set_argument,
            "rejected_nested_function": rejected_nested_function,
        },
        "task": "eager test, no durable worker",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)
