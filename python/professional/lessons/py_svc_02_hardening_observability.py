"""python-svc-02 learner lab: service hardening and observability."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Literal

Role = Literal["reader", "operator"]


def is_authorized(role: Role, action: str) -> bool:
    """TODO: readers may predict; operators may predict and reload."""

    raise NotImplementedError("complete is_authorized")


def readiness(
    dependency_checks: Sequence[bool],
    *,
    artifact_verified: bool,
    draining: bool,
) -> bool:
    """TODO: ready only when all dependencies and the artifact are safe."""

    raise NotImplementedError("complete readiness")


def redact_fields(fields: Mapping[str, str]) -> dict[str, str]:
    """TODO: redact token, authorization, password, and secret keys."""

    raise NotImplementedError("complete redact_fields")


def self_check() -> None:
    print("Worked health rule: a running process may be healthy but not ready.")
    checks: tuple[tuple[str, Callable[[], object]], ...] = (
        ("authorization", lambda: is_authorized("reader", "predict")),
        (
            "readiness",
            lambda: readiness([True, True], artifact_verified=True, draining=False),
        ),
        (
            "redaction",
            lambda: redact_fields({"request_id": "r1", "token": "local-value"}),
        ),
    )
    for label, call in checks:
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


# === Numbered professional practice ===
#
# Attempt every exercise before opening solutions. Keep evidence in a copy
# under .learning/ or in tests; do not overwrite the reference solution.
# Full acceptance checks and progressive hints:
# companion-guides/py_svc_02_hardening_observability.md
#
# Exercise 1 — Validate startup configuration
# Prompt: Parse maximum concurrency, rate capacity, and refill rate. Reject zero,
# negative, blank, or nonnumeric values before constructing the service. Keep credential
# retrieval outside dataclass representations and logs.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 2 — Complete health/readiness policy
# Prompt: Health remains true for a running process. Readiness requires at least one
# configured dependency, all probes ready, verified artifact, and no draining state.
# Return named reasons so an operator can diagnose 503 without exposing secrets. Do not
# make a liveness endpoint perform slow dependency calls; repeated restarts can amplify an
# external outage.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 3 — Design structured events
# Prompt: Emit request started/completed/failed/rejected with request ID, action, bounded
# reason, and error type. Redact token, authorization, password, secret, and API key
# fields case-insensitively. Do not log request bodies by default.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 4 — Design metrics
# Prompt: Count success, failure, unauthenticated, forbidden, rate-limited, saturated, and
# not-ready outcomes. Observe duration values. Do not put user, token, request ID, or
# arbitrary URL into metric labels.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 5 — Bound concurrency
# Prompt: Acquire a `BoundedSemaphore` without blocking. Return a lease that always
# releases in `__exit__`, including exceptions. With capacity one, hold a lease and verify
# a second attempt returns busy immediately.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 6 — Rate limit with injected time
# Prompt: Consume two tokens, reject the third request, advance a fake clock one second,
# and accept one refill. State that this in-process bucket is not sufficient across
# multiple service instances.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 7 — Separate authentication and authorization
# Prompt: The local static authenticator maps placeholder test tokens to principals.
# Readers may predict; operators may predict and reload. Prove unknown identity returns
# 401 while an authenticated but unauthorized action returns 403. Production identity
# requires a reviewed provider, token verification/expiry, key rotation, transport
# security, and audit policy.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 8 — Trust an artifact narrowly
# Prompt: Compute expected SHA-256 before startup, verify exact bytes, then parse a flat
# JSON object. Tamper with the file and confirm verification fails. Do not use pickle for
# untrusted service artifacts.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 9 — Run the incident drill
# Prompt: Set a dependency probe false: 1. readiness reports its name, 2. health remains
# true, 3. new work receives 503, 4. the not-ready metric increments, and 5. a request-
# rejected log carries the request ID and bounded reason. Then restore the dependency and
# confirm readiness recovers.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 10 — Draw the Internet-facing boundary
# Prompt: List what this local example does not supply: TLS termination, real identity,
# secret management, distributed limits, reverse-proxy timeouts, network policy, WAF/abuse
# controls, autoscaling, durable telemetry, retention/privacy policy, artifact
# distribution, deployment rollback, and on-call response. Classify which boundary owns
# each omitted control and which local test evidence cannot validate it.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 11 — drain and shut down gracefully
# Prompt: Add a draining transition that makes readiness false, rejects new work, allows
# active leases a bounded grace period, and records unfinished requests before shutdown.
# Make repeated drain calls idempotent.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 12 — add a dependency circuit breaker
# Prompt: Wrap one dependency probe/call in a closed/open/half-open breaker with injected
# time. Define which failures count, one bounded probe, readiness interaction, and
# recovery metrics.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 13 — define distributed limiting semantics
# Prompt: Explain how the local token bucket behaves with four service processes, then
# design a shared limiter contract covering atomicity, key, window/token semantics,
# timeout, fail-open/closed choice, and privacy.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 14 — bound telemetry backpressure
# Prompt: Make the log/metric exporter slow or unavailable. Define a bounded queue,
# drop/coalesce policy, priority for security events, and counters that reveal lost
# telemetry without blocking request handling indefinitely.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 15 — propagate trace context safely
# Prompt: Accept or create a request/trace ID, validate its bounded format, carry it
# through local logs and an outbound fake client, and prove malformed or attacker-sized
# IDs are replaced rather than reflected.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 16 — rehearse credential rotation
# Prompt: Model a credential provider accepting active and previous key versions during a
# bounded overlap. Rotate, verify new requests use the active key, expire the old key, and
# ensure neither value reaches repr/log/metrics.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 17 — compose dependency timeout budgets
# Prompt: For a 750 ms request budget calling two dependencies, allocate local queue,
# dependency, retry, parsing, and response budgets. Propagate a monotonic deadline and
# stop work when useful completion is impossible.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 18 — run a fault-injection matrix
# Prompt: Inject dependency false/exception/latency, artifact tampering, auth outage,
# limiter saturation, log-export failure, handler exception, and drain. For each, predict
# status, readiness/health, cleanup, log, and metric evidence.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 19 — define an SLO and error budget
# Prompt: Define one availability and one latency SLI over eligible requests,
# target/window, exclusions, minimum volume, burn-rate alerts, owner, and release action.
# Use generated local events to compute a small example.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 20 — audit privacy, retention, and cardinality
# Prompt: Inventory every log field, metric label, trace attribute, and local artifact.
# Classify sensitivity, cardinality, purpose, retention, access, redaction, deletion, and
# owner; then test representative forbidden values.
# Evidence: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    self_check()
