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

## Exercises

### 1. Validate startup configuration

Parse maximum concurrency, rate capacity, and refill rate. Reject zero,
negative, blank, or nonnumeric values before constructing the service. Keep
credential retrieval outside dataclass representations and logs.

### 2. Complete health/readiness policy

Health remains true for a running process. Readiness requires at least one
configured dependency, all probes ready, verified artifact, and no draining
state. Return named reasons so an operator can diagnose 503 without exposing
secrets.

Do not make a liveness endpoint perform slow dependency calls; repeated restarts
can amplify an external outage.

### 3. Design structured events

Emit request started/completed/failed/rejected with request ID, action, bounded
reason, and error type. Redact token, authorization, password, secret, and API
key fields case-insensitively. Do not log request bodies by default.

### 4. Design metrics

Count success, failure, unauthenticated, forbidden, rate-limited, saturated, and
not-ready outcomes. Observe duration values. Do not put user, token, request ID,
or arbitrary URL into metric labels.

### 5. Bound concurrency

Acquire a `BoundedSemaphore` without blocking. Return a lease that always
releases in `__exit__`, including exceptions. With capacity one, hold a lease
and verify a second attempt returns busy immediately.

### 6. Rate limit with injected time

Consume two tokens, reject the third request, advance a fake clock one second,
and accept one refill. State that this in-process bucket is not sufficient
across multiple service instances.

### 7. Separate authentication and authorization

The local static authenticator maps placeholder test tokens to principals.
Readers may predict; operators may predict and reload. Prove unknown identity
returns 401 while an authenticated but unauthorized action returns 403.

Production identity requires a reviewed provider, token verification/expiry,
key rotation, transport security, and audit policy.

### 8. Trust an artifact narrowly

Compute expected SHA-256 before startup, verify exact bytes, then parse a flat
JSON object. Tamper with the file and confirm verification fails. Do not use
pickle for untrusted service artifacts.

### 9. Run the incident drill

Set a dependency probe false:

1. readiness reports its name,
2. health remains true,
3. new work receives 503,
4. the not-ready metric increments, and
5. a request-rejected log carries the request ID and bounded reason.

Then restore the dependency and confirm readiness recovers.

### 10. Draw the Internet-facing boundary

List what this local example does not supply: TLS termination, real identity,
secret management, distributed limits, reverse-proxy timeouts, network policy,
WAF/abuse controls, autoscaling, durable telemetry, retention/privacy policy,
artifact distribution, deployment rollback, and on-call response.

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
