# docker-037: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

TLS authenticates a server identity and encrypts traffic in transit under its certificate trust model. A reverse proxy receives client requests and forwards them to an upstream application. It can terminate TLS, route hostnames and paths, apply limits and emit access logs. It does not automatically make the upstream application authorized or safe for public use.

The study app is intentionally host-loopback only and uses HTTP for local teaching. Publishing it to the internet would create new requirements: identity, access control, TLS certificates, input limits, abuse handling, patching and operational ownership. This chapter designs that boundary without exposing your machine.

Proxy headers such as a forwarded client address are claims from the proxy chain. An application should trust them only from known proxies under an explicit configuration. Accepting arbitrary client-supplied forwarding headers can break rate limits or audit attribution.

Draw the full request path before configuring a proxy: client name resolution, public endpoint, TLS handshake, proxy routing, upstream connection and application response. Each hop has its own timeout and identity. A certificate for one hostname does not validate a different name merely because both resolve to the same IP.

Use a synthetic configuration review and diagrams here. The course does not register a domain, request certificates or open firewall ports. A production configuration must use the chosen proxy’s actual documentation and a separate deployment review.

## Exercise 1: Distinguish TLS and application authorization.

A correctly encrypted request can still be unauthorized. The application must decide who may read or change its data.

**Expected:** Encrypted authenticated transport versus permission for an action.

## Exercise 2: Predict the effect of a certificate name mismatch.

Do not disable verification as the default fix. Correct the intended hostname and certificate relationship.

**Expected:** The client cannot validate the requested server name normally.

## Exercise 3: Draw proxy and upstream trust boundaries.

The drawing should show where TLS terminates and which component validates each request or header.

**Expected:** Explicit client-facing and internal hops with identities and timeouts.

## Exercise 4: Diagnose a proxy 502 separately from an app 404.

Use logs and direct owned upstream observations to locate the first failing hop without exposing new ports unnecessarily.

**Expected:** Upstream failure versus a completed app route response.

## Exercise 5: Explain forwarded-header spoofing.

Treat those values as claims, not facts. Trust only the configured proxy chain and document how original client identity is derived.

**Expected:** Untrusted clients can send headers unless the proxy boundary sanitizes them.

## Exercise 6: State what would be required before public exposure.

The local fixture’s simplicity is intentional. Do not advertise a loopback teaching app as public production hosting merely by changing the bind address.

**Expected:** A separate deployment design covering access, TLS, limits, operations and data.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
