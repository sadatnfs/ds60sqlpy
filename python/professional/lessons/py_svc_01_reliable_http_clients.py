"""python-svc-01 learner lab: reliable HTTP client boundaries.

This artifact makes no network calls. The worked example feeds local response
objects through a classifier. Complete the TODO policy functions before
opening the reference implementation.

Professional learner deep dive (python-svc-01)
------------------------------------------------

Mental model:
An HTTP transport sends one request and returns one response or raises a transport error. A
reliable client wraps that mechanism with policy: time budgets, status classification, bounded
retries/backoff, replay safety, correlation/idempotency identities, response validation,
pagination bounds, and redacted diagnostics.  Retry decisions need two gates: the failure may be
transient, and the operation must be safe to replay. A POST is not safe merely because a library
can resend it. Deadlines bound the whole logical operation, not each attempt independently.

API/boundary anatomy:
* transport Protocol: isolates request/response mechanics so policy is deterministic under
  scripted failures.
* retry classifier + budget: allows only documented transient failures while respecting
  attempts, delay, and remaining deadline.
* response/schema validation: rejects malformed success bodies before trusted domain code
  consumes them.

Micro-example A — apply both retryability and replay-safety gates::

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
    decisions = [may_retry(method, status, idempotency_key=key)
                 for method, status, key in cases]
    print(decisions)
    assert decisions == [True, False, True, False]

Expected: A transient status is insufficient for an unsafe mutation without a stable idempotency
          identity.

Micro-example B — reject a pagination cursor loop::

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

Expected: The bounded collector fails on the repeated cursor instead of looping forever or
          duplicating items.

Debugging rule: Use a scripted fake to record attempt count, request identities, timeouts,
                delays, response closure, cursor history, and redacted log fields.

The snippets demonstrate mechanics only. They do not complete the
numbered TODOs below; implement those from their stated contracts and
prove normal, boundary, and failure behavior.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal

Method = Literal["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
Outcome = Literal["success", "retryable", "permanent"]


@dataclass(frozen=True)
class Response:
    """Minimal local response used to practise policy."""

    status: int
    headers: Mapping[str, str]


def classify_status(status: int) -> Outcome:
    """Classify an HTTP status without sending a request.

    TODO:
    - 2xx is success
    - 408, 425, 429, 500, 502, 503, and 504 are retryable
    - every other valid status is permanent
    Reject values outside 100..599.
    """

    raise NotImplementedError("complete classify_status")


def method_can_retry(method: Method, idempotency_key: str | None) -> bool:
    """Return whether replaying this logical operation is permitted.

    TODO: safe/idempotent methods may retry. Require a non-empty idempotency key
    before replaying POST or PATCH.
    """

    raise NotImplementedError("complete method_can_retry")


def redact_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Return log-safe headers without changing the caller's mapping.

    TODO: replace Authorization, Cookie, Set-Cookie, and X-API-Key values with
    ``<redacted>`` using case-insensitive header-name matching.
    """

    raise NotImplementedError("complete redact_headers")


def worked_example() -> None:
    """Show a local response sequence and activate completed exercises."""

    script = [
        Response(503, {"Retry-After": "1"}),
        Response(200, {"Content-Type": "application/json"}),
    ]
    print("Local scripted statuses:", [response.status for response in script])
    for response in script:
        try:
            outcome = classify_status(response.status)
        except NotImplementedError:
            print("TODO: status classification")
            break
        else:
            print(f"{response.status} -> {outcome}")

    checks: tuple[tuple[str, Callable[[], object]], ...] = (
        ("POST replay policy", lambda: method_can_retry("POST", "order-1001")),
        (
            "header redaction",
            lambda: redact_headers(
                {"Authorization": "Bearer local-example", "Accept": "application/json"}
            ),
        ),
    )
    for label, call in checks:
        try:
            value = call()
        except NotImplementedError:
            print(f"TODO: {label}")
        else:
            print(f"Completed: {label} -> {value!r}")


# === Numbered professional practice ===
#
# Attempt every exercise before opening solutions. Keep evidence in a copy
# under .learning/ or in tests; do not overwrite the reference solution.
# Full acceptance checks and progressive hints:
# companion-guides/py_svc_01_reliable_http_clients.md
#
# Exercise 1 — classify status
# Prompt: Implement `classify_status`. Treat 2xx as success and
# 408/425/429/500/502/503/504 as retryable. Other valid statuses are permanent for this
# course policy. Reject impossible values. Classification is configurable in real systems.
# For example, a particular 409 may be retryable only when the API contract says so.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 2 — authorize replay
# Prompt: Implement `method_can_retry`: - GET, HEAD, PUT, DELETE, and OPTIONS are
# replayable by HTTP semantics. - POST and PATCH require a non-empty idempotency key in
# this lesson. An idempotency header helps only if the server documents and enforces it.
# Never invent safety solely on the client side.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 3 — add bounded backoff
# Prompt: For one-based failed attempt `n`, start with
# `base_delay * 2 ** (n - 1) + base_delay * jitter_fraction`, then cap the result. Inject
# jitter and sleep so tests record delays without waiting. Bound numeric `Retry-After`.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 4 — keep identities stable
# Prompt: Generate one correlation ID before the attempt loop. Generate or accept one
# idempotency key per logical mutation. Assert every scripted attempt sees the same
# values. Do not create a new idempotency key inside a retry loop; the server would see
# each replay as a new operation.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 5 — paginate defensively
# Prompt: Collect `items` until `next_cursor` is null. Require a list of objects, reject
# blank cursors, remember seen cursors, and enforce a maximum page count. Treat the cursor
# as opaque. URL-encode it rather than parsing or concatenating it manually.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 6 — configure and redact auth
# Prompt: Read `DS60_API_TOKEN`, `DS60_API_BASE_URL`, and a numeric timeout from an
# injected environment mapping. Make the token field `repr=False`. Implement case-
# insensitive redaction for authorization, cookies, proxy authorization, and API-key
# headers. Redact common query credential keys before logging URLs. Do not log bodies by
# default.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 7 — prove policy with scripts
# Prompt: Create deterministic scripts for: 1. 503 then 200 for GET, 2. 400 for GET, 3.
# 503 for POST without a key, 4. 503 then 200 for POST with a key, 5. 429 with `Retry-
# After`, 6. three transport timeouts, 7. two valid pages, and 8. a repeated cursor.
# Assert request count, delays, identities, timeout propagation, returned items, and
# redacted logs.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 8 — allocate an end-to-end timeout budget
# Prompt: Given a 2-second caller deadline, allocate connect, read, pool, retry sleep, and
# parsing budgets across at most three attempts. Reject a retry when the remaining budget
# cannot support another useful attempt.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 9 — support Retry-After dates safely
# Prompt: Extend policy reasoning from numeric Retry-After seconds to an HTTP-date. Inject
# wall and monotonic clocks, handle a past date, malformed text, clock skew, and the local
# delay cap.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 10 — model a circuit breaker
# Prompt: Design closed, open, and half-open states around the existing retrying client.
# Specify counted failures, threshold, cooldown, one probe, success reset, and concurrency
# ownership.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 11 — bound concurrent requests
# Prompt: Add a client-side bulkhead that caps active transport calls and defines whether
# excess work waits with a deadline or fails immediately. Prove permits release on
# success, exception, timeout, and cancellation.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 12 — close streaming responses
# Prompt: Define a streaming-response protocol with explicit close and cancellation
# semantics. Test partial consumption, parse failure, caller cancellation, and a body
# larger than the configured byte limit.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 13 — inject a credential provider
# Prompt: Replace a static token field with a credential-provider protocol that can
# refresh once after a documented authentication challenge. Preserve redaction and prevent
# refresh loops.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 14 — build an adversarial transport contract suite
# Prompt: Extend scripted tests with redirect loops, malformed JSON, wrong content type,
# repeated/blank cursors, oversized bodies, connection reset after send, and credentials
# embedded in mixed-case headers or query strings.
# Verify: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    worked_example()
