# Reliable HTTP clients and external-service boundaries

**Stable ID:** `python-svc-01`

**Level:** advanced

**Estimated time:** 180–240 minutes

## Level and prerequisites

- **Catalog prerequisite:** `python-15`
- Python Days 1–15, including exceptions, dataclasses, logging, testing, and CLI
  configuration
- HTTP method/status vocabulary from Python Day 44 is helpful
- No API key, public service, HTTP package, or network connection

The lesson uses a `Transport` protocol and scripted local responses. A future
adapter may use `httpx`, `requests`, or the standard library, but policy tests
must remain transport-independent.

## Learning objectives

By the end, you can:

1. Put an explicit timeout on every request attempt.
2. Classify success, retryable failures, and permanent failures.
3. Retry only replay-safe operations with bounded backoff and jitter.
4. Respect a numeric `Retry-After` value for rate limiting.
5. Preserve one correlation and idempotency identity across attempts.
6. Consume cursor pagination with loop and page-count guards.
7. Read authentication from runtime configuration.
8. Produce diagnostic logs without exposing credentials.
9. Test the complete policy with an injected deterministic transport.

### Motivation

A one-line HTTP call works on the happy path but leaves important questions
unanswered: How long may it wait? Can an operation be replayed? Does a 400 mean
the same thing as a 503? What prevents infinite pagination? Which identifiers
help operators connect attempts without putting a credential into logs?

The reliable unit is not a library call. It is a policy boundary whose behavior
can be proved without relying on a real service.

## Vocabulary and concepts

- **Attempt:** one transport call.
- **Logical request:** the user operation, possibly made of several attempts.
- **Timeout:** maximum time allowed for an attempt before it fails.
- **Transient failure:** a condition likely to succeed later, such as 503.
- **Permanent failure:** a condition retry policy should return immediately,
  such as most validation-related 4xx responses.
- **Idempotent:** repeating an operation has the same intended effect as doing
  it once.
- **Idempotency key:** a client-generated operation identity that a cooperating
  server uses to deduplicate replays.
- **Exponential backoff:** waits that grow after repeated failures.
- **Jitter:** bounded randomness added so many clients do not retry together.
- **Rate limit:** a service-imposed request budget, commonly reported with 429.
- **Correlation ID:** an identifier connecting logs and attempts.
- **Pagination cursor:** an opaque continuation value supplied by a service.
- **Transport:** the mechanism that sends bytes; it does not own retry policy.
- **Redaction:** replacement of sensitive material before logging.

## Worked example / walkthrough

### Classify a local script

Open
[`lessons/py_svc_01_reliable_http_clients.py`](../lessons/py_svc_01_reliable_http_clients.py).
It contains two local responses: 503 followed by 200. Predict the
classification, then run it.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\lessons\py_svc_01_reliable_http_clients.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_svc_01_reliable_http_clients.py
```

Status classification alone does not authorize a replay. The request method
and idempotency contract must also permit it.

### Follow one logical request

The reference client prepares timeout, auth, correlation ID, and optional
idempotency key once. Each attempt uses the same prepared request:

```text
logical request
    |
    +-- attempt 1 -> 503 -> bounded delay
    |
    +-- attempt 2 -> 200 -> return response
```

The retry counter is bounded. A failure after the final attempt includes the
attempt count and correlation ID, not the authorization value.

Run the offline demo:

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe python\professional\solutions\py_svc_01_reliable_http_clients_solution.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/solutions/py_svc_01_reliable_http_clients_solution.py
```

Inspect the printed first log event. Its authorization value must be
`<redacted>`.

## Exercises

### Exercise 1 — classify status

Implement `classify_status`. Treat 2xx as success and
408/425/429/500/502/503/504 as retryable. Other valid statuses are permanent
for this course policy. Reject impossible values.

Classification is configurable in real systems. For example, a particular 409
may be retryable only when the API contract says so.

### Exercise 2 — authorize replay

Implement `method_can_retry`:

- GET, HEAD, PUT, DELETE, and OPTIONS are replayable by HTTP semantics.
- POST and PATCH require a non-empty idempotency key in this lesson.

An idempotency header helps only if the server documents and enforces it.
Never invent safety solely on the client side.

### Exercise 3 — add bounded backoff

For a one-based failed attempt `n`, start with:

```text
base_delay * 2 ** (n - 1) + base_delay * jitter_fraction
```

Cap the result. Inject the jitter source and sleep function so tests record
delays without actually waiting. For 429 with numeric `Retry-After`, wait at
least the server value but no longer than the policy cap.

### Exercise 4 — keep identities stable

Generate one correlation ID before the attempt loop. Generate or accept one
idempotency key per logical mutation. Assert every scripted attempt sees the
same values.

Do not create a new idempotency key inside a retry loop; the server would see
each replay as a new operation.

### Exercise 5 — paginate defensively

Collect `items` until `next_cursor` is null. Require a list of objects, reject
blank cursors, remember seen cursors, and enforce a maximum page count.

Treat the cursor as opaque. URL-encode it rather than parsing or concatenating
it manually.

### Exercise 6 — configure and redact auth

Read `DS60_API_TOKEN`, `DS60_API_BASE_URL`, and a numeric timeout from an
injected environment mapping. Make the token field `repr=False`.

Implement case-insensitive redaction for authorization, cookies, proxy
authorization, and API-key headers. Redact common query credential keys before
logging URLs. Do not log bodies by default.

### Exercise 7 — prove policy with scripts

Create deterministic scripts for:

1. 503 then 200 for GET,
2. 400 for GET,
3. 503 for POST without a key,
4. 503 then 200 for POST with a key,
5. 429 with `Retry-After`,
6. three transport timeouts,
7. two valid pages, and
8. a repeated cursor.

Assert request count, delays, identities, timeout propagation, returned items,
and redacted logs.

## Self-check

- Every attempt has a positive timeout.
- Permanent statuses produce exactly one transport call.
- A POST without an idempotency key is never replayed.
- A keyed POST preserves the same key across attempts.
- Backoff grows, is jitterable, and never exceeds its cap.
- 429 honors the supported numeric `Retry-After` form.
- Pagination stops, detects cursor loops, and has a maximum page count.
- Correlation IDs appear in diagnostic errors.
- Authentication, cookies, API keys, and sensitive query values do not appear
  in structured logs or configuration `repr`.
- Tests open no socket and sleep for no real time.

Run the focused suite:

Windows PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m unittest python.professional.tests.test_py_svc_01_reliable_http_clients -v
```

macOS/Linux:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest python.professional.tests.test_py_svc_01_reliable_http_clients -v
```

## Common pitfalls

- **The default client can wait forever:** no explicit connect/read/overall
  timeout reached the concrete transport.
- **Every exception retries:** programming errors, invalid requests, and
  permanent statuses were confused with transient transport failures.
- **POST retries create duplicates:** replay occurred without a server-backed
  idempotency contract.
- **Tests take seconds:** real `sleep` was not injected.
- **All clients retry at once:** exponential backoff lacks jitter.
- **429 loops forever:** retry count or delay cap is missing.
- **Pagination repeats data:** a cursor loop or changing page contract was not
  detected.
- **A token appears in logs:** headers or query parameters were rendered before
  redaction, or a configuration dataclass exposed its field in `repr`.
- **The fake proves the network adapter:** it does not. It proves policy.
  Separately contract-test the chosen adapter's timeout and response mapping.

## Next step

- Add a thin adapter for one HTTP library and keep these policy tests unchanged.
- Combine this lesson with `python-pro-02`, using a bounded queue whose workers
  call the reliable client.
- Continue to Bridge Days 3–4 to compare HTTP value binding, transaction
  boundaries, retry eligibility, and idempotency with database operations.
