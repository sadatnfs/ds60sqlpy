"""Finite cross-framework engineering investigation with explicit scope."""

import json


def run_cases():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="synthetic-fixture",
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "finite-engineering-cache",
            }
        },
    )
    import django

    django.setup()
    from django.core.cache import cache, caches

    def key(tenant, version):
        return f"summary:{tenant}:v{version}"

    cache.set(key("a", 1), {"total": 3})
    cache.set(key("b", 1), {"total": 9})
    assert cache.get(key("a", 1)) == {"total": 3}
    assert cache.get(key("a", 2)) is None
    assert cache.get(key("b", 1)) == {"total": 9}

    class Bucket:
        def __init__(self):
            self.tokens = 2.0
            self.last = 0.0

        def admit(self, now):
            if now < self.last:
                raise ValueError("Clock must be monotonic")
            self.tokens = min(2.0, self.tokens + (now - self.last))
            self.last = now
            if self.tokens < 1:
                return False
            self.tokens -= 1
            return True

    worker_a, worker_b = Bucket(), Bucket()
    assert [worker_a.admit(0), worker_a.admit(0), worker_a.admit(0), worker_a.admit(1)] == [
        True,
        True,
        False,
        True,
    ]
    assert worker_b.admit(0)
    # Independent process state admits another request, so this is not a global quota.
    caches.close_all()
    return {
        "tenant_and_version_cache_keys": True,
        "single_bucket_decisions": [True, True, False, True],
        "another_worker_has_independent_budget": True,
        "distributed_limit": "requires atomic shared coordination, not this object",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True))
