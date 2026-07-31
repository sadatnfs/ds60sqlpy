# Service hardening and observability

**Stable ID:** `python-svc-02`

**Level:** advanced

**Estimated time:** 240–300 minutes

## Level and prerequisites

- **Catalog prerequisites:** `python-55`, `bridge-08`, `python-svc-01`, and
  `python-ml-01`
- Python Days 44, 54, and 55
- Bridge Day 8
- `python-svc-01` retry/identity boundaries
- `python-ml-01` trusted manifest and artifact concepts

This is a deterministic local policy lab. It does not start a server or claim
to be an Internet-ready deployment.

## Learning objectives

You will be able to:

1. Validate concurrency and rate configuration before startup.
2. Distinguish process health from traffic readiness.
3. Keep request IDs in structured logs without logging credentials.
4. Emit low-cardinality counters and duration observations.
5. Bound concurrent work without waiting indefinitely.
6. Apply a testable token-bucket policy with an injected clock.
7. Separate authentication from role authorization.
8. Verify a JSON artifact hash before trusting content.
9. Run a local dependency incident drill and inspect evidence.
10. State what an Internet-facing deployment still requires.

## Vocabulary and concepts

- **Health/liveness:** whether a process is running and can answer diagnostics.
- **Readiness:** whether the instance should receive new work.
- **Draining:** refusing new work while finishing or stopping existing work.
- **Structured log:** named event plus bounded machine-readable fields.
- **Metric cardinality:** number of distinct label combinations; request/user IDs
  are dangerous metric labels.
- **Saturation:** all permitted concurrent capacity is in use.
- **Bulkhead:** isolation that limits one workload's resource consumption.
- **Token bucket:** capacity that is consumed by requests and refilled over
  time.
- **Authentication:** establishing identity.
- **Authorization:** allowing an identified principal to perform an action.
- **Trusted artifact:** content whose identity and format were verified before
  use.
- **Incident drill:** controlled failure used to prove detection and response.

## Worked example / walkthrough

The learner file asks three policy questions: role authorization, readiness,
and redaction.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_svc_02_hardening_observability.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_svc_02_hardening_observability.py
```

The reference service has injected boundaries:

```text
request -> readiness probes
        -> Authenticator -> Principal -> role authorization
        -> TokenBucket(Clock)
        -> ConcurrencyGate
        -> injected work
        -> StructuredLog + Metrics

startup -> SHA-256 verification -> constrained JSON artifact
```

Its main function serves one local request, flips a dependency probe, and shows
readiness fail while health stays available.

<!-- BEGIN PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

Work from the repository root. First run the answer-free learner
module named in this guide's original walkthrough. Read each TODO as a
contract: record the input, returned value, raised exception, and side
effect before implementing it. Then run the focused test command in
**Self-check**. Keep exploratory changes in a copy or a new test; the
checked-in solution remains a comparison artifact.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_svc_02_hardening_observability.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_svc_02_hardening_observability.py
```

The focused test command is shown in **Self-check** below. The learner
module is intentionally answer-free, so `TODO` output is the expected
starting state rather than a setup failure.

## Mechanism lab — two small examples before the full system

### Boundary and mental model

Service hardening turns assumptions into admission and evidence policy.
Liveness says the process can run; readiness says it should receive
traffic given dependencies, verified artifacts, and draining state.
A bulkhead bounds concurrent work and a rate limiter bounds arrival
over time.

Authentication establishes identity; authorization checks allowed
actions. Structured logs may carry one bounded correlation ID but never
credentials or full request bodies. Metrics use low-cardinality labels;
request/user IDs belong in logs/traces, not metric dimensions.

- **startup validation + artifact verification:** fails before traffic when capacity, policy, or trusted model bytes are invalid.
- **admission chain:** checks readiness, identity/role, rate, and concurrency before expensive work.
- **structured log + metrics:** records bounded diagnostic context and aggregate outcomes without secrets or unbounded labels.

### Micro-example A — keep liveness and readiness independent

```python
def status(*, running, dependencies, artifact_verified, draining):
    return {
        "healthy": running,
        "ready": (
            running
            and bool(dependencies)
            and all(dependencies)
            and artifact_verified
            and not draining
        ),
    }


outage = status(running=True, dependencies=[True, False], artifact_verified=True, draining=False)
print(outage)
assert outage == {"healthy": True, "ready": False}
```

**Expected observation:** A dependency outage removes traffic readiness while avoiding a harmful restart loop.

**Why it matters:** Liveness performs only a fast local process check and does not call slow external systems.

### Micro-example B — reject high-cardinality metric labels

```python
allowed_metric_labels = {"route", "method", "outcome", "error_class"}
proposed = {
    "route": "/predict",
    "outcome": "success",
    "request_id": "r-123",
    "user_id": "u-9",
}
forbidden = set(proposed) - allowed_metric_labels
print({"forbidden_metric_labels": sorted(forbidden)})
assert forbidden == {"request_id", "user_id"}
```

**Expected observation:** Per-request and per-user identities are rejected from metrics, preventing unbounded series growth and privacy leakage.

**Why it matters:** Route values are templated/bounded rather than raw URLs with arbitrary IDs.

### Debugging and transfer

**Common mistake:** Making liveness depend on every dependency or attaching request/user/token values to metrics.

**Diagnostic:** Inject dependency, auth, limiter, saturation, artifact, handler, and telemetry failures; assert status, cleanup, bounded log event, and metric outcome.

**Transfer question:** How should admission and telemetry behave while a process drains existing work during a deploy?

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercises

### 1. Validate startup configuration

Parse maximum concurrency, rate capacity, and refill rate. Reject zero,
negative, blank, or nonnumeric values before constructing the service. Keep
credential retrieval outside dataclass representations and logs.

**Verify:** Validate startup configuration — parse maximum concurrency, rate capacity, and refill rate; reject zero, negative, blank, or nonnumeric values before constructing the service; keep credential retrieval outside dataclass representations and logs.

### 2. Complete health/readiness policy

Health remains true for a running process. Readiness requires at least one
configured dependency, all probes ready, verified artifact, and no draining
state. Return named reasons so an operator can diagnose 503 without exposing
secrets.

Do not make a liveness endpoint perform slow dependency calls; repeated restarts
can amplify an external outage.

**Verify:** Complete health/readiness policy — health remains true for a running process; readiness requires at least one configured dependency, all probes ready, verified artifact, and no draining state; return named reasons so an operator can diagnose 503 without exposing secrets.

### 3. Design structured events

Emit request started/completed/failed/rejected with request ID, action, bounded
reason, and error type. Redact token, authorization, password, secret, and API
key fields case-insensitively. Do not log request bodies by default.

**Verify:** Design structured events — emit request started/completed/failed/rejected with request ID, action, bounded reason, and error type; redact token, authorization, password, secret, and API key fields case-insensitively; do not log request bodies by default.

### 4. Design metrics

Count success, failure, unauthenticated, forbidden, rate-limited, saturated, and
not-ready outcomes. Observe duration values. Do not put user, token, request ID,
or arbitrary URL into metric labels.

**Verify:** Design metrics — count success, failure, unauthenticated, forbidden, rate-limited, saturated, and not-ready outcomes; observe duration values; do not put user, token, request ID, or arbitrary URL into metric labels.

### 5. Bound concurrency

Acquire a `BoundedSemaphore` without blocking. Return a lease that always
releases in `__exit__`, including exceptions. With capacity one, hold a lease
and verify a second attempt returns busy immediately.

**Verify:** Bound concurrency — acquire a BoundedSemaphore without blocking; return a lease that always releases in exit , including exceptions; with capacity one, hold a lease and verify a second attempt returns busy immediately.

### 6. Rate limit with injected time

Consume two tokens, reject the third request, advance a fake clock one second,
and accept one refill. State that this in-process bucket is not sufficient
across multiple service instances.

**Verify:** Rate limit with injected time — consume two tokens, reject the third request, advance a fake clock one second, and accept one refill; state that this in-process bucket is not sufficient across multiple service instances.

### 7. Separate authentication and authorization

The local static authenticator maps placeholder test tokens to principals.
Readers may predict; operators may predict and reload. Prove unknown identity
returns 401 while an authenticated but unauthorized action returns 403.

Production identity requires a reviewed provider, token verification/expiry,
key rotation, transport security, and audit policy.

**Verify:** Separate authentication and authorization — the local static authenticator maps placeholder test tokens to principals; readers may predict; operators may predict and reload; prove unknown identity returns 401 while an authenticated but unauthorized action returns 403.

### 8. Trust an artifact narrowly

Compute expected SHA-256 before startup, verify exact bytes, then parse a flat
JSON object. Tamper with the file and confirm verification fails. Do not use
pickle for untrusted service artifacts.

**Verify:** Trust an artifact narrowly — compute expected SHA-256 before startup, verify exact bytes, then parse a flat JSON object; tamper with the file and confirm verification fails; do not use pickle for untrusted service artifacts.

### 9. Run the incident drill

Set a dependency probe false:

- readiness reports its name,

- health remains true,

- new work receives 503,

- the not-ready metric increments, and

- a request-rejected log carries the request ID and bounded reason.

Then restore the dependency and confirm readiness recovers.

**Verify:** Run the incident drill — set a dependency probe false: - readiness reports its name, - health remains true, - new work receives 503, - the not-ready metric increments, and - a request-rejected log carries the request ID and bounded reason; then restore the dependency and confirm readiness recovers.

### 10. Draw the Internet-facing boundary

List what this local example does not supply: TLS termination, real identity,
secret management, distributed limits, reverse-proxy timeouts, network policy,
WAF/abuse controls, autoscaling, durable telemetry, retention/privacy policy,
artifact distribution, deployment rollback, and on-call response.

**Verify:** Draw the Internet-facing boundary — list what this local example does not supply: TLS termination, real identity, secret management, distributed limits, reverse-proxy timeouts, network policy, WAF/abuse controls, autoscaling, durable telemetry, retention/privacy policy, artifact distribution, deployment rollback, and on-call response.

### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 11 — drain and shut down gracefully

Add a draining transition that makes readiness false, rejects new work, allows active leases a bounded grace period, and records unfinished requests before shutdown. Make repeated drain calls idempotent.

**Progressive hint:** Stop admission before waiting. Track active work through the existing concurrency gate and use an injected clock/event for deterministic tests.

**Verify:** drain and shut down gracefully — add a draining transition that makes readiness false, rejects new work, allows active leases a bounded grace period, and records unfinished requests before shutdown; make repeated drain calls idempotent.

### Exercise 12 — add a dependency circuit breaker

Wrap one dependency probe/call in a closed/open/half-open breaker with injected time. Define which failures count, one bounded probe, readiness interaction, and recovery metrics.

**Progressive hint:** The breaker protects request work; readiness may report degraded dependency state without performing the expensive call on every probe.

**Verify:** add a dependency circuit breaker — wrap one dependency probe/call in a closed/open/half-open breaker with injected time; define which failures count, one bounded probe, readiness interaction, and recovery metrics.

### Exercise 13 — define distributed limiting semantics

Explain how the local token bucket behaves with four service processes, then design a shared limiter contract covering atomicity, key, window/token semantics, timeout, fail-open/closed choice, and privacy.

**Progressive hint:** Four independent buckets multiply effective capacity. A shared backend becomes another dependency with its own failure policy.

**Verify:** define distributed limiting semantics — explain how the local token bucket behaves with four service processes, then design a shared limiter contract covering atomicity, key, window/token semantics, timeout, fail-open/closed choice, and privacy.

### Exercise 14 — bound telemetry backpressure

Make the log/metric exporter slow or unavailable. Define a bounded queue, drop/coalesce policy, priority for security events, and counters that reveal lost telemetry without blocking request handling indefinitely.

**Progressive hint:** Telemetry is work and memory. Producers need a nonblocking or bounded-time contract, and the service needs visibility into dropped events.

**Verify:** bound telemetry backpressure — make the log/metric exporter slow or unavailable; define a bounded queue, drop/coalesce policy, priority for security events, and counters that reveal lost telemetry without blocking request handling indefinitely.

### Exercise 15 — propagate trace context safely

Accept or create a request/trace ID, validate its bounded format, carry it through local logs and an outbound fake client, and prove malformed or attacker-sized IDs are replaced rather than reflected.

**Progressive hint:** Correlation identifiers are untrusted input. Keep them out of metric labels and separate from authentication identity.

**Verify:** propagate trace context safely — accept or create a request/trace ID, validate its bounded format, carry it through local logs and an outbound fake client, and prove malformed or attacker-sized IDs are replaced rather than reflected.

### Exercise 16 — rehearse credential rotation

Model a credential provider accepting active and previous key versions during a bounded overlap. Rotate, verify new requests use the active key, expire the old key, and ensure neither value reaches repr/log/metrics.

**Progressive hint:** Reference credentials by version/opaque handle. Inject provider and clock; never hard-code lesson secrets.

**Verify:** rehearse credential rotation — model a credential provider accepting active and previous key versions during a bounded overlap; rotate, verify new requests use the active key, expire the old key, and ensure neither value reaches repr/log/metrics.

### Exercise 17 — compose dependency timeout budgets

For a 750 ms request budget calling two dependencies, allocate local queue, dependency, retry, parsing, and response budgets. Propagate a monotonic deadline and stop work when useful completion is impossible.

**Progressive hint:** Nested calls cannot each assume the full caller timeout. Reserve cleanup/response time and record which budget exhausted.

**Verify:** compose dependency timeout budgets — for a 750 ms request budget calling two dependencies, allocate local queue, dependency, retry, parsing, and response budgets; propagate a monotonic deadline and stop work when useful completion is impossible.

### Exercise 18 — run a fault-injection matrix

Inject dependency false/exception/latency, artifact tampering, auth outage, limiter saturation, log-export failure, handler exception, and drain. For each, predict status, readiness/health, cleanup, log, and metric evidence.

**Progressive hint:** Faults are local fakes, not destructive infrastructure tests. Assert invariants and recovery after each isolated scenario.

**Verify:** run a fault-injection matrix — inject dependency false/exception/latency, artifact tampering, auth outage, limiter saturation, log-export failure, handler exception, and drain; for each, predict status, readiness/health, cleanup, log, and metric evidence.

### Exercise 19 — define an SLO and error budget

Define one availability and one latency SLI over eligible requests, target/window, exclusions, minimum volume, burn-rate alerts, owner, and release action. Use generated local events to compute a small example.

**Progressive hint:** SLIs need exact numerator/denominator and route/outcome policy. Avoid user/request IDs or arbitrary URLs as labels.

**Verify:** define an SLO and error budget — define one availability and one latency SLI over eligible requests, target/window, exclusions, minimum volume, burn-rate alerts, owner, and release action; use generated local events to compute a small example.

### Exercise 20 — audit privacy, retention, and cardinality

Inventory every log field, metric label, trace attribute, and local artifact. Classify sensitivity, cardinality, purpose, retention, access, redaction, deletion, and owner; then test representative forbidden values.

**Progressive hint:** Use allowlists for structured fields and labels. Counts/opaque IDs often replace raw values; request bodies remain excluded by default.

**Verify:** audit privacy, retention, and cardinality — inventory every log field, metric label, trace attribute, and local artifact; classify sensitivity, cardinality, purpose, retention, access, redaction, deletion, and owner; then test representative forbidden values.

## Self-check

- Unsafe configuration fails before handling requests.
- Health and readiness diverge during dependency failure.
- Logs retain request IDs but not tokens.
- Metrics avoid high-cardinality identities.
- A saturated gate returns immediately and always releases.
- Rate behavior is deterministic under a fake clock.
- 401 and 403 represent distinct identity/policy failures.
- Artifact tampering fails before parsing.
- Incident evidence includes readiness reason, 503, log, and metric.
- The lab is described as local policy, not Internet-ready security.

Windows PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m unittest python.professional.tests.test_py_svc_02_hardening_observability -v
```

macOS/Linux:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest python.professional.tests.test_py_svc_02_hardening_observability -v
```

## Common pitfalls

- **Liveness depends on every external service:** an outage causes restart
  loops.
- **Readiness says only false:** operators receive no bounded reason.
- **Request or user IDs become metric labels:** cardinality grows without
  bound.
- **A semaphore waits forever:** overload consumes all workers and deadlines.
- **Rate limiting trusts wall-clock sleeps in tests:** the clock seam is
  missing.
- **Authentication equals authorization:** any valid identity can perform every
  action.
- **Tokens appear in logs or repr:** redaction happened too late.
- **Hash verification follows deserialization:** unsafe loading already ran.
- **One-process limits are called distributed protection:** deployment topology
  was ignored.
- **A FastAPI development server is called hardened:** TLS, identity, secrets,
  telemetry, deployment, and operations remain unresolved.

## Next step

Wrap these policies in a thin FastAPI adapter from Day 44, preserving injected
tests. Combine with `python-svc-01` for outbound reliability and Bridge Day 8
for database readiness, transaction, and deployment behavior.

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-svc-02` — Service hardening and observability.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize readiness, bounded resources, auth policy, artifact trust, and low-cardinality telemetry. Use exactly these maintained learner materials:
- guide: `python/professional/companion-guides/py_svc_02_hardening_observability.md`
- learner artifact: `python/professional/lessons/py_svc_02_hardening_observability.py`

Treat me as a beginner except for these direct catalog prerequisites:
`python-55`, `bridge-08`, `python-svc-01`, `python-ml-01`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
