# pyweb-066: Caching, rate limits and worker coordination

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-065`.

## Starting point and result

Caching and rate limiting both depend on state, but they have different correctness requirements. This chapter demonstrates tenant/version-aware cache keys and a deterministic token bucket, then shows why an independent worker has an independent budget when coordination lives only in process memory.

## Mechanism: key dimensions and coordination scope matter

A cached summary depends on the tenant and the representation version. Those dimensions belong in its key. Omitting tenant can disclose one tenant's value to another; omitting version can return an old representation after the application changes its schema.

A token bucket stores a capacity, current tokens and last observation time. Tokens refill at a configured rate up to capacity. Each admitted request consumes a token. With capacity 2 and refill rate 1 per second, two simultaneous requests can pass, a third cannot, and one token is available after one second.

The refill rule is \(b_{new}=\min(C,b_{old}+r\Delta t)\), where \(C\) is capacity, \(r\) is tokens per second and \(\Delta t\) is elapsed time. Admission requires \(b_{new}\geq 1\) and then subtracts one token. For elapsed-time calculations, a monotonic clock avoids wall-clock adjustments moving time backward. The fixture supplies explicit timestamps so the result is deterministic. A real implementation also needs atomic updates if several threads or processes share the bucket.

## Worked case: separate tenant and version cache entries

The real Django local-memory cache stores different summaries for tenants a and b. Retrieving tenant a's version 1 returns its own total, while requesting version 2 misses. Tenant b retains its separate value. The assertions check those distinctions directly.

Versioned keys can support a deployment transition, but old entries still consume space until eviction or cleanup. Invalidation policy should consider both correctness and storage. A version suffix is not a complete cache-management strategy by itself.

This backend is intentionally process-local. Its successful get/set behavior does not establish a shared Redis or distributed cache. An application with multiple workers must choose whether divergent local caches are acceptable for the particular value and define how stale data is handled.

## Worked case: a local bucket cannot enforce a global quota

One bucket admits two requests at time 0, refuses the third and admits another at time 1. A second independent bucket still admits a request at time 0. The program reports that extra admission as evidence of separate state, not as a bug in the arithmetic.

If each of four workers owns an independent capacity 2 bucket, the aggregate burst can exceed 2. A requirement for a global quota therefore needs shared atomic coordination or a deliberate distribution strategy. Merely using the same class and configuration in every worker does not share its state.

A rate limiter also needs a failure policy for its coordination backend. Failing open preserves availability but can exceed limits; failing closed protects the budget but can deny legitimate work. The choice depends on the operation and must be visible in the system design.

## Failure diagnosis and discussion

**Why can a cache leak data even when the database query is scoped correctly?** A cache hit may bypass that query. The key and cached representation must preserve the same authorization dimensions.

**Why inject the clock into the bucket test?** It makes refill and boundary behavior reproducible without sleeps or dependence on the host's clock. It also exposes the monotonic-time assumption.

If limits vary with worker count, inspect coordination scope. If stale values survive a release, inspect versioning and invalidation. Continue with observability, where labels and recorded data need similarly deliberate dimensions and bounds.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/)
