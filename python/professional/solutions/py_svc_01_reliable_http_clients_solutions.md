# Reliable HTTP client solution reasoning

Attempt `python-svc-01` before opening
[`py_svc_01_reliable_http_clients_solution.py`](py_svc_01_reliable_http_clients_solution.py).

## Separate mechanism from policy

`Transport` has one method: send a prepared request or raise a known timeout.
It does not decide whether to retry. `ReliableClient` owns classification,
replay eligibility, identity, delay, pagination, and safe diagnostics. A real
HTTP-library adapter can replace `ScriptedTransport` without rewriting policy
tests.

This structural protocol is intentional gradual typing: any adapter with the
right method satisfies it without inheriting from a framework base class.

## Status and replay are two gates

A 503 is transient, but replay is allowed only if the operation is safe. GET,
HEAD, PUT, DELETE, and OPTIONS use their idempotent semantics. POST and PATCH
require a non-empty idempotency key. The key remains identical across attempts.

If a non-replayable POST receives 503, the client raises immediately. The
caller must reconcile the operation instead of guessing whether a side effect
occurred.

## Retry timing

The policy uses one-based attempts and computes exponential delay plus injected
jitter. It caps every delay. For the supported numeric `Retry-After` form, it
takes the larger of local backoff and the server request, then applies the cap.

Both `sleep` and `jitter` are injected. Tests can assert exact values without
waiting or depending on randomness. Production code would inject a real random
source; deterministic tests remain unchanged.

## Timeout and diagnostic boundary

`timeout_seconds` is part of every prepared request, forcing a concrete adapter
to receive it. Exhaustion errors expose attempt count and correlation ID.
Authorization is never included.

`ClientConfig` reads credentials from an environment mapping and hides the token
from dataclass representation. Request logs copy and redact sensitive headers,
and the displayed URL redacts common query credential keys. Logging response
bodies is deliberately absent because bodies may contain personal or secret
data.

## Pagination

The page method validates the container and each item, treats cursors as opaque,
detects repeats, and enforces a page ceiling. A null cursor is the only normal
stop signal. These guards convert malformed service behavior into bounded,
diagnosable errors.

Each page is a separate logical GET and gets its own correlation ID in a real
configuration. Retries *within* a page preserve that page's correlation ID.

## Alternatives and edge cases

- HTTP-date `Retry-After` needs clock injection and date parsing. This lab
  deliberately supports only numeric seconds and documents that boundary.
- Streaming responses need separate connect/read/write/pool timeouts and a
  close/cancellation contract.
- OAuth refresh should live in a credential provider with redacted tests, not
  inside generic retry handling.
- Circuit breakers, concurrency rate limiters, and bulkheads address broader
  failure pressure. They do not replace per-request timeouts.
- PUT and DELETE are idempotent by specification, but a particular service may
  violate or narrow that contract. The service API remains authoritative.
- An idempotency key needs server-side retention and conflict semantics.

## Expected results

Tests prove that only permitted failures replay, attempts and delays are
bounded, 429 delay is honored, identities are stable, timeout errors retain
context, pagination terminates or fails safely, and no test credential reaches
logs. All behavior is local and deterministic.


---

## Exercise-by-exercise reference

Use this map after an honest attempt. The executable implementation remains
[`py_svc_01_reliable_http_clients_solution.py`](py_svc_01_reliable_http_clients_solution.py); this section explains the
contract, evidence, alternatives, and edge cases behind every numbered task.

### Exercise 1 — classify status

**Prompt recap:** Implement `classify_status`. Treat 2xx as success and 408/425/429/500/502/503/504 as retryable. Other valid statuses are permanent for this course policy. Reject impossible values. Classification is configurable in real systems. For example, a particular 409 may be retryable only when the API contract says so.

**Reference reasoning:** Reliable clients separate transport mechanism from bounded retry, replay, identity, pagination, configuration, and diagnostic policy. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 2 — authorize replay

**Prompt recap:** Implement `method_can_retry`: - GET, HEAD, PUT, DELETE, and OPTIONS are replayable by HTTP semantics. - POST and PATCH require a non-empty idempotency key in this lesson. An idempotency header helps only if the server documents and enforces it. Never invent safety solely on the client side.

**Reference reasoning:** Reliable clients separate transport mechanism from bounded retry, replay, identity, pagination, configuration, and diagnostic policy. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 3 — add bounded backoff

**Prompt recap:** For one-based failed attempt `n`, start with `base_delay * 2 ** (n - 1) + base_delay * jitter_fraction`, then cap the result. Inject jitter and sleep so tests record delays without waiting. For 429 with numeric `Retry-After`, honor at least the server value without exceeding policy.

**Reference reasoning:** Reliable clients separate transport mechanism from bounded retry, replay, identity, pagination, configuration, and diagnostic policy. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 4 — keep identities stable

**Prompt recap:** Generate one correlation ID before the attempt loop. Generate or accept one idempotency key per logical mutation. Assert every scripted attempt sees the same values. Do not create a new idempotency key inside a retry loop; the server would see each replay as a new operation.

**Reference reasoning:** Reliable clients separate transport mechanism from bounded retry, replay, identity, pagination, configuration, and diagnostic policy. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 5 — paginate defensively

**Prompt recap:** Collect `items` until `next_cursor` is null. Require a list of objects, reject blank cursors, remember seen cursors, and enforce a maximum page count. Treat the cursor as opaque. URL-encode it rather than parsing or concatenating it manually.

**Reference reasoning:** Reliable clients separate transport mechanism from bounded retry, replay, identity, pagination, configuration, and diagnostic policy. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 6 — configure and redact auth

**Prompt recap:** Read `DS60_API_TOKEN`, `DS60_API_BASE_URL`, and a numeric timeout from an injected environment mapping. Make the token field `repr=False`. Implement case-insensitive redaction for authorization, cookies, proxy authorization, and API-key headers. Redact common query credential keys before logging URLs. Do not log bodies by default.

**Reference reasoning:** Reliable clients separate transport mechanism from bounded retry, replay, identity, pagination, configuration, and diagnostic policy. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 7 — prove policy with scripts

**Prompt recap:** Create deterministic scripts for: 1. 503 then 200 for GET, 2. 400 for GET, 3. 503 for POST without a key, 4. 503 then 200 for POST with a key, 5. 429 with `Retry-After`, 6. three transport timeouts, 7. two valid pages, and 8. a repeated cursor. Assert request count, delays, identities, timeout propagation, returned items, and redacted logs.

**Reference reasoning:** Reliable clients separate transport mechanism from bounded retry, replay, identity, pagination, configuration, and diagnostic policy. The executable module and
the focused discussion earlier in this file implement this original
exercise. Verify every acceptance condition from the prompt with a
normal case, a boundary case, and the documented failure behavior.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 8 — allocate an end-to-end timeout budget

**Prompt recap:** Given a 2-second caller deadline, allocate connect, read, pool, retry sleep, and parsing budgets across at most three attempts. Reject a retry when the remaining budget cannot support another useful attempt.

**Reasoning path:** Use an injected monotonic clock and compute a deadline once per logical request. Per-attempt timeouts must shrink with remaining time.

Create `deadline = now + total_budget` before the attempt loop. Before sleeping
or sending, compute remaining time and stop when it cannot cover the minimum
attempt budget. Pass bounded connect/read/pool values to the transport rather
than one unexamined global timeout.

The final error should preserve attempts, correlation ID, and whether the
deadline or retry count ended the request. Wall-clock time is unsuitable
because clock adjustment can move it backward.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 9 — support Retry-After dates safely

**Prompt recap:** Extend policy reasoning from numeric Retry-After seconds to an HTTP-date. Inject wall and monotonic clocks, handle a past date, malformed text, clock skew, and the local delay cap.

**Reasoning path:** HTTP-date parsing needs wall time; sleeping and deadline accounting need monotonic time. Invalid server guidance falls back to local backoff.

Parse only the documented HTTP-date format with a timezone-aware standard
library parser. Convert the server date to a nonnegative delay from injected
wall time, then combine it with local exponential backoff and cap it by both
policy and caller deadline. A past date contributes zero.

Malformed guidance should be recorded safely and ignored, not crash the client
or produce an unbounded sleep. Tests use fixed clocks and recorded sleep; they
never wait in real time.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 10 — model a circuit breaker

**Prompt recap:** Design closed, open, and half-open states around the existing retrying client. Specify counted failures, threshold, cooldown, one probe, success reset, and concurrency ownership.

**Reasoning path:** A breaker protects a dependency across logical requests; it does not replace per-attempt timeout or retry policy.

In closed state, count only configured dependency failures. Crossing the
threshold opens until an injected monotonic deadline. After cooldown, permit a
bounded probe; success closes and resets, while failure reopens. Concurrent
callers must not all become the half-open probe.

Expose state transitions as low-cardinality metrics/events. Do not count local
validation or caller-cancellation errors as dependency health unless the
contract explicitly says so.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 11 — bound concurrent requests

**Prompt recap:** Add a client-side bulkhead that caps active transport calls and defines whether excess work waits with a deadline or fails immediately. Prove permits release on success, exception, timeout, and cancellation.

**Reasoning path:** The concurrency permit surrounds only the scarce external call. A `finally` block or context manager owns release.

Use an injected semaphore/gate with an explicit acquisition policy and maximum
queue or wait time. Return a distinct saturation error so callers can
distinguish local protection from a remote status. Hold the permit during the
transport call, not during unrelated parsing or caller work.

A bulkhead limits one process; distributed request pressure requires an
upstream/shared policy. Avoid unbounded queues that merely move the overload
into memory and latency.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 12 — close streaming responses

**Prompt recap:** Define a streaming-response protocol with explicit close and cancellation semantics. Test partial consumption, parse failure, caller cancellation, and a body larger than the configured byte limit.

**Reasoning path:** Ownership must say who closes the response. Use a context manager and enforce size while reading chunks, not after buffering everything.

The transport returns an async or synchronous context-managed byte stream.
The client reads bounded chunks, updates a byte count, and closes in `finally`
for normal completion and every failure. Parsing happens after or incrementally
within the same ownership boundary.

Reject oversized or decompression-expanded content before it exhausts memory.
Never retry after an unsafe partial side effect merely because stream parsing
failed.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 13 — inject a credential provider

**Prompt recap:** Replace a static token field with a credential-provider protocol that can refresh once after a documented authentication challenge. Preserve redaction and prevent refresh loops.

**Reasoning path:** Credential acquisition is a separate boundary. Cache/expiry policy and single-flight refresh belong to the provider.

Ask the provider for a credential immediately before preparing an attempt.
After the API's documented expired-token response, invalidate/refresh at most
once for the logical request, then replay only when the operation is otherwise
safe. Keep token values out of dataclass repr, errors, and logs.

Concurrent expired requests should share one refresh where practical.
Authentication failure is not a reason for unbounded general retries.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.

### Exercise 14 — build an adversarial transport contract suite

**Prompt recap:** Extend scripted tests with redirect loops, malformed JSON, wrong content type, repeated/blank cursors, oversized bodies, connection reset after send, and credentials embedded in mixed-case headers or query strings.

**Reasoning path:** Assert bounded attempts, exact request identity, closed resources, typed errors, and the absence of secret material in every diagnostic.

Each script names the expected call count, retry decision, error type, delay,
and log projection. Redirect behavior must be explicit because forwarding
authorization across origins is dangerous. Validate content type and response
shape before using fields.

Use only local fake transports and placeholder credentials. A contract suite
proves client policy independent of any particular HTTP library adapter; each
real adapter still needs a small local integration test.

**Common trap:** Retrying because an error looks transient can duplicate side effects, exceed a caller deadline, leak credentials, or turn a small outage into a retry storm.

**Self-check:** State what the result proves, what assumption it relies on,
and which input would make the policy reject or choose a different path.
