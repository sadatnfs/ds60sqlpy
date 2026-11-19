# docker-037: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-037.md`.

## Exercise 1: Distinguish TLS and application authorization.

**Expected answer:** Encrypted authenticated transport versus permission for an action.

**Why:** A correctly encrypted request can still be unauthorized. The application must decide who may read or change its data.

## Exercise 2: Predict the effect of a certificate name mismatch.

**Expected answer:** The client cannot validate the requested server name normally.

**Why:** Do not disable verification as the default fix. Correct the intended hostname and certificate relationship.

## Exercise 3: Draw proxy and upstream trust boundaries.

**Expected answer:** Explicit client-facing and internal hops with identities and timeouts.

**Why:** The drawing should show where TLS terminates and which component validates each request or header.

## Exercise 4: Diagnose a proxy 502 separately from an app 404.

**Expected answer:** Upstream failure versus a completed app route response.

**Why:** Use logs and direct owned upstream observations to locate the first failing hop without exposing new ports unnecessarily.

## Exercise 5: Explain forwarded-header spoofing.

**Expected answer:** Untrusted clients can send headers unless the proxy boundary sanitizes them.

**Why:** Treat those values as claims, not facts. Trust only the configured proxy chain and document how original client identity is derived.

## Exercise 6: State what would be required before public exposure.

**Expected evidence:** A separate deployment design covering access, TLS, limits, operations and data.

**Why:** The local fixture’s simplicity is intentional. Do not advertise a loopback teaching app as public production hosting merely by changing the bind address.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
