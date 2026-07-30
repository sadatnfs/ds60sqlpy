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

