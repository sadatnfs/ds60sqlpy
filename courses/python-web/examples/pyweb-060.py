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
