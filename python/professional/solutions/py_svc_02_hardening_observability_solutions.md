# Service hardening and observability solution reasoning

Attempt `python-svc-02` before opening
[`py_svc_02_hardening_observability_solution.py`](py_svc_02_hardening_observability_solution.py).

Health answers whether the process can answer diagnostics; readiness answers
whether it should receive new work. A failed dependency, unverified artifact,
or draining state makes readiness false while health can remain true for
investigation and graceful shutdown.

Authentication establishes identity; authorization checks that identity's role
for one action. The local static authenticator is an injected test double, not a
production credential system. Tokens never enter logs. Structured events carry
request IDs and bounded fields; metrics use low-cardinality names rather than
user or request IDs as labels.

The token bucket has an injected clock, and the concurrency gate rejects excess
work immediately. Those controls protect one process. Internet-facing systems
also need shared/distributed limits, queue budgets, upstream timeouts, TLS,
secret rotation, network policy, and abuse monitoring.

Artifact bytes are hashed before JSON is trusted. The loader deliberately
rejects pickle and nested arbitrary objects. The incident drill turns a
dependency probe false, observes readiness fail, verifies new work receives
503, and checks logs and metrics retain enough context.

Edge cases include double lease release, clock movement, rate keys with
unbounded cardinality, health checks that perform expensive dependency calls,
logs containing request bodies, metrics labeled by user, authorization policy
drift, artifact replacement after verification, and a readiness dependency
that flaps.


---

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Reasoning before implementation

A fixed admission sequence and injected policy components make overload, auth, trust, telemetry, and incident behavior deterministic under tests.

1. **startup validation + artifact verification:** fails before traffic when capacity, policy, or trusted model bytes are invalid.
2. **admission chain:** checks readiness, identity/role, rate, and concurrency before expensive work.
3. **structured log + metrics:** records bounded diagnostic context and aggregate outcomes without secrets or unbounded labels.
4. **Prove the failure boundary:** Exercise one normal case, one boundary case, and one injected failure without relying on hidden state.

**Alternative:** A reverse proxy/service mesh can provide some limits, TLS, and telemetry, but application authorization, artifact trust, and semantic readiness remain.

**Trade-off:** Fail-closed controls reduce unsafe service at the cost of availability; fail-open requires explicit bounded risk and ownership.

**Failure boundary:** Multi-process limits, cancellation, credential rotation, trace injection, slow telemetry exporters, circuit half-open probes, and graceful drain need policy.

**Verification:** Run the fault matrix, prove permits/tokens release, distinguish 401/403/429/503, tamper artifacts, audit log redaction/metric labels, and rehearse drain/recovery.

### Verification micro-example

Run this small, deterministic case before adapting the reference to a
larger system. It gives the reasoning above an executable anchor:

```python
def status(*, running, dependencies, artifact_verified, draining):
    return {
        "healthy": running,
        "ready": (
            running and bool(dependencies) and all(dependencies)
            and artifact_verified and not draining
        ),
    }

outage = status(
    running=True, dependencies=[True, False],
    artifact_verified=True, draining=False
)
print(outage)
assert outage == {"healthy": True, "ready": False}
```

**Expected observation:** A dependency outage removes traffic readiness while avoiding a harmful restart loop.

The reference implementation is one defensible contract, not a license
to copy internal steps into every system. Preserve the observable
guarantees and repeat the failure tests when adapting it.

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reference

Use this map after an honest attempt. The executable implementation remains
[`py_svc_02_hardening_observability_solution.py`](py_svc_02_hardening_observability_solution.py); this section explains the
contract, evidence, alternatives, and edge cases behind every numbered task.

### Exercise 1 — Validate startup configuration

**Prompt recap:** Parse maximum concurrency, rate capacity, and refill rate. Reject zero, negative, blank, or nonnumeric values before constructing the service. Keep credential retrieval outside dataclass representations and logs.

**Reference reasoning:** A hardened service validates startup, separates identity/policy, bounds work, trusts artifacts narrowly, and emits privacy-safe evidence for health and incidents. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `Validate startup configuration`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 2 — Complete health/readiness policy

**Prompt recap:** Health remains true for a running process. Readiness requires at least one configured dependency, all probes ready, verified artifact, and no draining state. Return named reasons so an operator can diagnose 503 without exposing secrets. Do not make a liveness endpoint perform slow dependency calls; repeated restarts can amplify an external outage.

**Reference reasoning:** A hardened service validates startup, separates identity/policy, bounds work, trusts artifacts narrowly, and emits privacy-safe evidence for health and incidents. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `Complete health/readiness policy`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 3 — Design structured events

**Prompt recap:** Emit request started/completed/failed/rejected with request ID, action, bounded reason, and error type. Redact token, authorization, password, secret, and API key fields case-insensitively. Do not log request bodies by default.

**Reference reasoning:** A hardened service validates startup, separates identity/policy, bounds work, trusts artifacts narrowly, and emits privacy-safe evidence for health and incidents. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `Design structured events`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 4 — Design metrics

**Prompt recap:** Count success, failure, unauthenticated, forbidden, rate-limited, saturated, and not-ready outcomes. Observe duration values. Do not put user, token, request ID, or arbitrary URL into metric labels.

**Reference reasoning:** A hardened service validates startup, separates identity/policy, bounds work, trusts artifacts narrowly, and emits privacy-safe evidence for health and incidents. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `Design metrics`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 5 — Bound concurrency

**Prompt recap:** Acquire a `BoundedSemaphore` without blocking. Return a lease that always releases in `__exit__`, including exceptions. With capacity one, hold a lease and verify a second attempt returns busy immediately.

**Reference reasoning:** A hardened service validates startup, separates identity/policy, bounds work, trusts artifacts narrowly, and emits privacy-safe evidence for health and incidents. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `Bound concurrency`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 6 — Rate limit with injected time

**Prompt recap:** Consume two tokens, reject the third request, advance a fake clock one second, and accept one refill. State that this in-process bucket is not sufficient across multiple service instances.

**Reference reasoning:** A hardened service validates startup, separates identity/policy, bounds work, trusts artifacts narrowly, and emits privacy-safe evidence for health and incidents. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `Rate limit with injected time`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 7 — Separate authentication and authorization

**Prompt recap:** The local static authenticator maps placeholder test tokens to principals. Readers may predict; operators may predict and reload. Prove unknown identity returns 401 while an authenticated but unauthorized action returns 403. Production identity requires a reviewed provider, token verification/expiry, key rotation, transport security, and audit policy.

**Reference reasoning:** A hardened service validates startup, separates identity/policy, bounds work, trusts artifacts narrowly, and emits privacy-safe evidence for health and incidents. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `Separate authentication and authorization`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 8 — Trust an artifact narrowly

**Prompt recap:** Compute expected SHA-256 before startup, verify exact bytes, then parse a flat JSON object. Tamper with the file and confirm verification fails. Do not use pickle for untrusted service artifacts.

**Reference reasoning:** A hardened service validates startup, separates identity/policy, bounds work, trusts artifacts narrowly, and emits privacy-safe evidence for health and incidents. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `Trust an artifact narrowly`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 9 — Run the incident drill

**Prompt recap:** Set a dependency probe false: 1. readiness reports its name, 2. health remains true, 3. new work receives 503, 4. the not-ready metric increments, and 5. a request-rejected log carries the request ID and bounded reason. Then restore the dependency and confirm readiness recovers.

**Reference reasoning:** A hardened service validates startup, separates identity/policy, bounds work, trusts artifacts narrowly, and emits privacy-safe evidence for health and incidents. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `Run the incident drill`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 10 — Draw the Internet-facing boundary

**Prompt recap:** List what this local example does not supply: TLS termination, real identity, secret management, distributed limits, reverse-proxy timeouts, network policy, WAF/abuse controls, autoscaling, durable telemetry, retention/privacy policy, artifact distribution, deployment rollback, and on-call response.

**Reference reasoning:** A hardened service validates startup, separates identity/policy, bounds work, trusts artifacts narrowly, and emits privacy-safe evidence for health and incidents. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `Draw the Internet-facing boundary`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 11 — drain and shut down gracefully

**Prompt recap:** Add a draining transition that makes readiness false, rejects new work, allows active leases a bounded grace period, and records unfinished requests before shutdown. Make repeated drain calls idempotent.

**Reasoning path:** Stop admission before waiting. Track active work through the existing concurrency gate and use an injected clock/event for deterministic tests.

Set draining atomically, publish readiness false, and reject new handlers with
a bounded retryable response. Wait for active count to reach zero until the
configured deadline, then record remaining count and follow the documented
force/exit policy. Health can remain true during drain for diagnostics.

Do not release another request's lease or wait forever. Tests control worker
completion explicitly and assert telemetry contains request counts, not bodies.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `drain and shut down gracefully`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 12 — add a dependency circuit breaker

**Prompt recap:** Wrap one dependency probe/call in a closed/open/half-open breaker with injected time. Define which failures count, one bounded probe, readiness interaction, and recovery metrics.

**Reasoning path:** The breaker protects request work; readiness may report degraded dependency state without performing the expensive call on every probe.

Count configured dependency timeouts/failures across requests. When open,
reject quickly until cooldown; then allow one half-open probe. Success resets,
failure reopens. Concurrency ownership prevents a herd of probes.

Keep liveness independent. Whether readiness becomes false depends on whether
the dependency is required for all service actions; encode that policy
explicitly rather than coupling it to breaker implementation.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `add a dependency circuit breaker`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 13 — define distributed limiting semantics

**Prompt recap:** Explain how the local token bucket behaves with four service processes, then design a shared limiter contract covering atomicity, key, window/token semantics, timeout, fail-open/closed choice, and privacy.

**Reasoning path:** Four independent buckets multiply effective capacity. A shared backend becomes another dependency with its own failure policy.

Choose the limiting identity (tenant/API key/action) without placing raw
credentials in storage or metrics. Require an atomic consume operation and
return allowed, remaining, and retry-after. Bound backend latency and state
whether unavailable limiting blocks security-sensitive actions or degrades.

Document approximation and clock ownership for distributed algorithms. Local
concurrency limits still protect each process even with a shared rate policy.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `define distributed limiting semantics`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Exercise 14 — bound telemetry backpressure

**Prompt recap:** Make the log/metric exporter slow or unavailable. Define a bounded queue, drop/coalesce policy, priority for security events, and counters that reveal lost telemetry without blocking request handling indefinitely.

**Reasoning path:** Telemetry is work and memory. Producers need a nonblocking or bounded-time contract, and the service needs visibility into dropped events.

Use a bounded queue with an owned exporter worker. Low-priority repetitive
events may be sampled/coalesced; security/audit events follow the reviewed
durability path. On saturation, increment a local low-cardinality dropped count
and emit a bounded fallback signal without recursion.

Never enqueue request bodies or tokens. Shutdown drains within a deadline and
reports unsent counts rather than hanging forever.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `bound telemetry backpressure`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Exercise 15 — propagate trace context safely

**Prompt recap:** Accept or create a request/trace ID, validate its bounded format, carry it through local logs and an outbound fake client, and prove malformed or attacker-sized IDs are replaced rather than reflected.

**Reasoning path:** Correlation identifiers are untrusted input. Keep them out of metric labels and separate from authentication identity.

Allow a conservative length/character format, generate a local opaque ID on
invalid input, and include it as one structured log field plus outbound
diagnostic header where policy permits. Child operations derive or record span
IDs without exposing credentials.

Metrics aggregate by bounded route/outcome, never request ID. Logging systems
must escape values so an ID cannot inject fake lines or fields.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `propagate trace context safely`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 16 — rehearse credential rotation

**Prompt recap:** Model a credential provider accepting active and previous key versions during a bounded overlap. Rotate, verify new requests use the active key, expire the old key, and ensure neither value reaches repr/log/metrics.

**Reasoning path:** Reference credentials by version/opaque handle. Inject provider and clock; never hard-code lesson secrets.

The service obtains current material at use time or through an explicitly
refreshable cache. During overlap, verification can accept both versions while
issuance uses only active. After deadline, old verification fails and the
event trail records version IDs and actor—not secret bytes.

Rotation failure has a rollback/escalation policy. Tests use placeholder
tokens and scan captured diagnostics for their absence.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `rehearse credential rotation`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 17 — compose dependency timeout budgets

**Prompt recap:** For a 750 ms request budget calling two dependencies, allocate local queue, dependency, retry, parsing, and response budgets. Propagate a monotonic deadline and stop work when useful completion is impossible.

**Reasoning path:** Nested calls cannot each assume the full caller timeout. Reserve cleanup/response time and record which budget exhausted.

Create the deadline once at request admission. Before each dependency call or
retry, derive a timeout from remaining budget and that dependency's cap. Avoid
starting a second call when only cleanup/response reserve remains. Cancellation
releases concurrency leases in `finally`.

Return a typed bounded failure and metric category such as dependency-timeout
without logging payloads. Fixed clocks make the policy deterministic in tests.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `compose dependency timeout budgets`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 18 — run a fault-injection matrix

**Prompt recap:** Inject dependency false/exception/latency, artifact tampering, auth outage, limiter saturation, log-export failure, handler exception, and drain. For each, predict status, readiness/health, cleanup, log, and metric evidence.

**Reasoning path:** Faults are local fakes, not destructive infrastructure tests. Assert invariants and recovery after each isolated scenario.

Build a table of fault, expected external response, state transition, active
lease count, event type, and metric delta. Reset fixtures between cases. Health
stays responsive unless the process itself cannot serve diagnostics; readiness
reflects required dependency/artifact/drain policy.

The matrix exposes missing observability and failure coupling. It does not
claim production chaos readiness without deployed-system validation.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `run a fault-injection matrix`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







### Exercise 19 — define an SLO and error budget

**Prompt recap:** Define one availability and one latency SLI over eligible requests, target/window, exclusions, minimum volume, burn-rate alerts, owner, and release action. Use generated local events to compute a small example.

**Reasoning path:** SLIs need exact numerator/denominator and route/outcome policy. Avoid user/request IDs or arbitrary URLs as labels.

For example, availability is successful eligible requests divided by eligible
requests, with client validation failures handled by a declared policy.
Latency uses a percentile/distribution for successful eligible work. Calculate
consumed bad-event budget over the window and compare short/long burn evidence.

Targets are product policy, not universal constants. Missing telemetry and
low volume are reported, not silently treated as success.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `define an SLO and error budget`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







### Exercise 20 — audit privacy, retention, and cardinality

**Prompt recap:** Inventory every log field, metric label, trace attribute, and local artifact. Classify sensitivity, cardinality, purpose, retention, access, redaction, deletion, and owner; then test representative forbidden values.

**Reasoning path:** Use allowlists for structured fields and labels. Counts/opaque IDs often replace raw values; request bodies remain excluded by default.

Fail tests if placeholder token, password, API key, email, or body text appears
in captured telemetry. Enforce bounded route/action/error enums for metric
labels and measure series count under adversarial IDs. Document retention and
deletion behavior for local files/exporters.

Redaction is defense in depth, not permission to collect unnecessary data.
Remove fields without a justified operational purpose.

**Common trap:** Liveness dependency checks, high-cardinality telemetry, in-process-only limits, logged secrets/bodies, or unverified artifacts can amplify the failure being diagnosed.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

**Verify:** For task `audit privacy, retention, and cardinality`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.
