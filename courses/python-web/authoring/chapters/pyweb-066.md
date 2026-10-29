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
