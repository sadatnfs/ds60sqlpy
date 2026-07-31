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
.\.venv\Scripts\python.exe python\professional\lessons\py_svc_01_reliable_http_clients.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_svc_01_reliable_http_clients.py
```

The focused test command is shown in **Self-check** below. The learner
module is intentionally answer-free, so `TODO` output is the expected
starting state rather than a setup failure.

## Mechanism lab — two small examples before the full system

### Boundary and mental model

An HTTP transport sends one request and returns one response or raises a
transport error. A reliable client wraps that mechanism with policy:
time budgets, status classification, bounded retries/backoff, replay
safety, correlation/idempotency identities, response validation,
pagination bounds, and redacted diagnostics.

Retry decisions need two gates: the failure may be transient, and the
operation must be safe to replay. A POST is not safe merely because a
library can resend it. Deadlines bound the whole logical operation, not
each attempt independently.

- **transport Protocol:** isolates request/response mechanics so policy is deterministic under scripted failures.
- **retry classifier + budget:** allows only documented transient failures while respecting attempts, delay, and remaining deadline.
- **response/schema validation:** rejects malformed success bodies before trusted domain code consumes them.

### Micro-example A — apply both retryability and replay-safety gates

```python
def may_retry(method, status, *, idempotency_key=None):
    transient = status in {429, 502, 503, 504}
    replay_safe = method in {"GET", "HEAD"} or idempotency_key is not None
    return transient and replay_safe


cases = [
    ("GET", 503, None),
    ("POST", 503, None),
    ("POST", 503, "logical-operation-17"),
    ("GET", 400, None),
]
decisions = [may_retry(method, status, idempotency_key=key) for method, status, key in cases]
print(decisions)
assert decisions == [True, False, True, False]
```

**Expected observation:** A transient status is insufficient for an unsafe mutation without a stable idempotency identity.

**Why it matters:** The server actually enforces the idempotency-key semantics rather than merely accepting the header.

### Micro-example B — reject a pagination cursor loop

```python
pages = {
    None: {"items": [1, 2], "next_cursor": "a"},
    "a": {"items": [3], "next_cursor": "a"},
}
cursor = None
seen = set()
items = []
for _ in range(10):
    if cursor in seen:
        raise RuntimeError(f"repeated cursor: {cursor!r}")
    seen.add(cursor)
    page = pages[cursor]
    items.extend(page["items"])
    cursor = page["next_cursor"]
    if cursor is None:
        break
```

**Expected observation:** The bounded collector fails on the repeated cursor instead of looping forever or duplicating items.

**Why it matters:** Cursors are opaque identifiers; blank, repeated, malformed, and excessive pages have declared failures.

### Debugging and transfer

**Common mistake:** Retrying every exception with a fresh idempotency key and a full per-attempt timeout.

**Diagnostic:** Use a scripted fake to record attempt count, request identities, timeouts, delays, response closure, cursor history, and redacted log fields.

**Transfer question:** How would the policy change for a streaming download that may fail after bytes were consumed?

<!-- END PROFESSIONAL PYTHON CONCEPT ENRICHMENT -->

## Exercises

### Exercise 1 — classify status

Implement `classify_status`. Treat 2xx as success and
408/425/429/500/502/503/504 as retryable. Other valid statuses are permanent
for this course policy. Reject impossible values.

Classification is configurable in real systems. For example, a particular 409
may be retryable only when the API contract says so.

**Verify:** classify status — table-test classify_status for representative 2xx success, retryable 429/503, permanent 400/401/403, contract-specific 409, and impossible <100 or >599 values; assert the exact enum/result or ValueError.

### Exercise 2 — authorize replay

Implement `method_can_retry`:

- GET, HEAD, PUT, DELETE, and OPTIONS are replayable by HTTP semantics.
- POST and PATCH require a non-empty idempotency key in this lesson.

An idempotency header helps only if the server documents and enforces it.
Never invent safety solely on the client side.

**Verify:** authorize replay — implement method can retry: - GET, HEAD, PUT, DELETE, and OPTIONS are replayable by HTTP semantics; pOST and PATCH require a non-empty idempotency key in this lesson; an idempotency header helps only if the server documents and enforces it.

### Exercise 3 — add bounded backoff

For a one-based failed attempt `n`, start with:

```text
base_delay * 2 ** (n - 1) + base_delay * jitter_fraction
```

Cap the result. Inject the jitter source and sleep function so tests record
delays without actually waiting. For 429 with numeric `Retry-After`, wait at
least the server value but no longer than the policy cap.

**Verify:** add bounded backoff — with injected jitter/sleep, assert failed attempt n uses capped base_delay * 2**(n-1) plus the declared jitter; numeric Retry-After is honored up to the cap and tests record delays without sleeping.

### Exercise 4 — keep identities stable

Generate one correlation ID before the attempt loop. Generate or accept one
idempotency key per logical mutation. Assert every scripted attempt sees the
same values.

Do not create a new idempotency key inside a retry loop; the server would see
each replay as a new operation.

**Verify:** keep identities stable — generate one correlation ID before the attempt loop; generate or accept one idempotency key per logical mutation; assert every scripted attempt sees the same values.

### Exercise 5 — paginate defensively

Collect `items` until `next_cursor` is null. Require a list of objects, reject
blank cursors, remember seen cursors, and enforce a maximum page count.

Treat the cursor as opaque. URL-encode it rather than parsing or concatenating
it manually.

**Verify:** paginate defensively — collect items until next cursor is null; require a list of objects, reject blank cursors, remember seen cursors, and enforce a maximum page count; treat the cursor as opaque.

### Exercise 6 — configure and redact auth

Read `DS60_API_TOKEN`, `DS60_API_BASE_URL`, and a numeric timeout from an
injected environment mapping. Make the token field `repr=False`.

Implement case-insensitive redaction for authorization, cookies, proxy
authorization, and API-key headers. Redact common query credential keys before
logging URLs. Do not log bodies by default.

**Verify:** configure and redact auth — read DS60 API TOKEN, DS60 API BASE URL, and a numeric timeout from an injected environment mapping; make the token field repr=False; implement case-insensitive redaction for authorization, cookies, proxy authorization, and API-key headers.

### Exercise 7 — prove policy with scripts

Create deterministic scripts for:

- 503 then 200 for GET,

- 400 for GET,

- 503 for POST without a key,

- 503 then 200 for POST with a key,

- 429 with `Retry-After`,

- three transport timeouts,

- two valid pages, and

- a repeated cursor.

Assert request count, delays, identities, timeout propagation, returned items,
and redacted logs.

**Verify:** prove policy with scripts — run scripted transports for 503→200 GET, permanent 400 GET, unsafe POST without key, retryable POST with stable key, 429 Retry-After, three timeouts, two pages, and repeated cursor; assert exact attempts/pages/final outcomes.

### Extended professional practice

These exercises move from prediction and implementation through debugging,
operational trade-offs, and review. Keep the default path deterministic and
offline; optional connected behavior must remain explicit.

### Exercise 8 — allocate an end-to-end timeout budget

Given a 2-second caller deadline, allocate connect, read, pool, retry sleep, and parsing budgets across at most three attempts. Reject a retry when the remaining budget cannot support another useful attempt.

**Progressive hint:** Use an injected monotonic clock and compute a deadline once per logical request. Per-attempt timeouts must shrink with remaining time.

**Verify:** allocate an end-to-end timeout budget — given a 2-second caller deadline, allocate connect, read, pool, retry sleep, and parsing budgets across at most three attempts; reject a retry when the remaining budget cannot support another useful attempt.

### Exercise 9 — support Retry-After dates safely

Extend policy reasoning from numeric Retry-After seconds to an HTTP-date. Inject wall and monotonic clocks, handle a past date, malformed text, clock skew, and the local delay cap.

**Progressive hint:** HTTP-date parsing needs wall time; sleeping and deadline accounting need monotonic time. Invalid server guidance falls back to local backoff.

**Verify:** support Retry-After dates safely — extend policy reasoning from numeric Retry-After seconds to an HTTP-date; inject wall and monotonic clocks, handle a past date, malformed text, clock skew, and the local delay cap.

### Exercise 10 — model a circuit breaker

Design closed, open, and half-open states around the existing retrying client. Specify counted failures, threshold, cooldown, one probe, success reset, and concurrency ownership.

**Progressive hint:** A breaker protects a dependency across logical requests; it does not replace per-attempt timeout or retry policy.

**Verify:** model a circuit breaker — design closed, open, and half-open states around the existing retrying client; specify counted failures, threshold, cooldown, one probe, success reset, and concurrency ownership.

### Exercise 11 — bound concurrent requests

Add a client-side bulkhead that caps active transport calls and defines whether excess work waits with a deadline or fails immediately. Prove permits release on success, exception, timeout, and cancellation.

**Progressive hint:** The concurrency permit surrounds only the scarce external call. A `finally` block or context manager owns release.

**Verify:** bound concurrent requests — add a client-side bulkhead that caps active transport calls and defines whether excess work waits with a deadline or fails immediately; prove permits release on success, exception, timeout, and cancellation.

### Exercise 12 — close streaming responses

Define a streaming-response protocol with explicit close and cancellation semantics. Test partial consumption, parse failure, caller cancellation, and a body larger than the configured byte limit.

**Progressive hint:** Ownership must say who closes the response. Use a context manager and enforce size while reading chunks, not after buffering everything.

**Verify:** close streaming responses — define a streaming-response protocol with explicit close and cancellation semantics; test partial consumption, parse failure, caller cancellation, and a body larger than the configured byte limit.

### Exercise 13 — inject a credential provider

Replace a static token field with a credential-provider protocol that can refresh once after a documented authentication challenge. Preserve redaction and prevent refresh loops.

**Progressive hint:** Credential acquisition is a separate boundary. Cache/expiry policy and single-flight refresh belong to the provider.

**Verify:** inject a credential provider — replace a static token field with a credential-provider protocol that can refresh once after a documented authentication challenge; preserve redaction and prevent refresh loops.

### Exercise 14 — build an adversarial transport contract suite

Extend scripted tests with redirect loops, malformed JSON, wrong content type, repeated/blank cursors, oversized bodies, connection reset after send, and credentials embedded in mixed-case headers or query strings.

**Progressive hint:** Assert bounded attempts, exact request identity, closed resources, typed errors, and the absence of secret material in every diagnostic.

**Verify:** build an adversarial transport contract suite — extend scripted tests with redirect loops, malformed JSON, wrong content type, repeated/blank cursors, oversized bodies, connection reset after send, and credentials embedded in mixed-case headers or query strings.

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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-svc-01` — Reliable HTTP clients and external-service boundaries.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize HTTP mechanism versus retry, timeout, pagination, idempotency, and redaction policy. Use exactly these maintained learner materials:
- guide: `python/professional/companion-guides/py_svc_01_reliable_http_clients.md`
- learner artifact: `python/professional/lessons/py_svc_01_reliable_http_clients.py`

Treat me as a beginner except for these direct catalog prerequisites:
`python-15`. Do not assume knowledge beyond them or skip the
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
