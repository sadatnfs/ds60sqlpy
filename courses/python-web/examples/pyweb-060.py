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
