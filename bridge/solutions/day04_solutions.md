# Bridge Day 4 — Solution notes

Try the [learner file](../lessons/day04_transactions_idempotency_retries.py)
first. The executable reference is [day04_solution.py](day04_solution.py).

## Idempotent insert

`create_job_once()` validates a non-blank key and performs one parameterized
insert into `pg_temp.bridge_jobs`. PostgreSQL's unique constraint arbitrates
concurrent requests. `ON CONFLICT ... DO NOTHING RETURNING job_id` returns one
row for an insert and no row for a duplicate.

A prior `SELECT` would be incorrect: another transaction could insert after the
check and before this transaction's insert.

## Transaction and retry scopes

`run_in_transaction()` owns commit or rollback for one operation.
`run_with_retry()` catches only explicitly classified transient exceptions,
limits attempts, and injects `sleep`. Tests can collect delay values instantly.

In a real adapter, a failed PostgreSQL transaction must be rolled back or
discarded before the next attempt. The retried callable should therefore own a
fresh complete transaction, not merely repeat one statement inside an already
aborted transaction.

## Tradeoffs

- Deterministic exponential delays make the lesson testable. Production retries
  often add random jitter so many workers do not retry simultaneously.
- The custom transient exception is a teaching seam. Production code should
  classify specific Psycopg exceptions and SQLSTATE codes, not translate every
  `OperationalError` automatically.
- Returning `None` for a duplicate is compact. Some APIs return a richer result
  such as `Inserted(id)` versus `AlreadyExists`.
- Idempotency keys prevent duplicate logical jobs only while their uniqueness
  records are retained. Retention and key scope are product decisions.

Test the last-attempt failure, zero delay, invalid policy, a permanent error,
duplicate keys, and rollback-before-reraise behavior.


<!-- BEGIN BRIDGE ENRICHMENT: SOLUTION EXAMPLE -->
## Small executable check

An injected sleeper turns retry timing into ordinary deterministic evidence:

```python
from bridge.solutions.day04_solution import (
    RetryPolicy,
    TransientDatabaseError,
    run_with_retry,
)

attempts = 0
delays: list[float] = []


def eventually_succeeds() -> str:
    global attempts
    attempts += 1
    if attempts < 3:
        raise TransientDatabaseError("temporary")
    return "ok"


result = run_with_retry(
    eventually_succeeds,
    policy=RetryPolicy(max_attempts=3, base_delay_seconds=0.1),
    sleep=delays.append,
)
assert result == "ok"
assert delays == [0.1, 0.2]
```
<!-- END BRIDGE ENRICHMENT: SOLUTION EXAMPLE -->

## Exercise solutions

These walkthroughs align one-for-one with the learner and guide. The executable
reference is `bridge/solutions/day04_solution.py`; use it only after an honest attempt.

**Shared failure rule:** Retrying a non-idempotent or ambiguously committed write can duplicate effects even when backoff logic is correct.

### Exercise 1 — Validation

**Prompt:** Validate `RetryPolicy` so attempts are at least one and base delay is finite and
non-negative.

**Approach:** Implement `__post_init__` checks for `max_attempts < 1`, non-finite delay, and
delay below zero, raising clear `ValueError` messages.

**Why this boundary matters:** Reject unusable policy at construction rather than inside a
failing retry loop.

**Verification evidence:** Construct policies at attempts `0/1` and delays `-1/0/inf/nan`; assert only attempts at least one with finite non-negative delay succeed and every invalid case raises `ValueError` immediately.

### Exercise 2 — SQL implementation

**Prompt:** Implement `create_job_once()` with one parameterized `INSERT`, a unique idempotency
key, `ON CONFLICT DO NOTHING`, and `RETURNING job_id`.

**Approach:** Execute one static statement with `(idempotency_key, payload)`. The database
either inserts and returns a row or reports no returned row after the conflict path.

**Why this boundary matters:** Let the uniqueness constraint arbitrate concurrency; do not
pre-read.

**Verification evidence:** Record one cursor call and assert static SQL contains `ON CONFLICT ... DO NOTHING` plus `RETURNING job_id`, while idempotency key and payload appear only in the two-value tuple.

### Exercise 3 — Mapping

**Prompt:** Return the inserted ID when `fetchone()` yields a row and `None` for a duplicate
without issuing a second statement.

**Approach:** Fetch exactly once; return `int(row[0])` when present and `None` otherwise. A
preliminary `SELECT` would add a race window and is unnecessary.

**Why this boundary matters:** Treat `None` as the documented `DO NOTHING` result.

**Verification evidence:** Configure `fetchone()` as `(42,)` then `None`; assert results are `42` and `None` and each case issues exactly one statement.

### Exercise 4 — Transaction

**Prompt:** Implement `run_in_transaction()` so success commits and any operation failure rolls
back before re-raising.

**Approach:** Call the operation in `try`, commit after it returns, and return the value. On
failure, roll back and use bare `raise` so type, traceback, and message are preserved.

**Why this boundary matters:** The wrapper owns the boundary; the operation owns only domain
work.

**Verification evidence:** Assert success events end `operation, commit` with no rollback; failure events end `operation, rollback`, no commit occurs, and the same exception is re-raised.

### Exercise 5 — Retry

**Prompt:** Implement `run_with_retry()` for only `TransientDatabaseError`, stopping at
`max_attempts` with delays `base * 2**(attempt - 1)`.

**Approach:** Count attempts from one, return immediately on success, and on a transient failure
either re-raise at the limit or call the injected sleeper with the current exponential delay.

**Why this boundary matters:** Never sleep after the last failed attempt and never catch
permanent errors.

**Verification evidence:** For base delay `0.1` and three attempts, assert delays are `[0.1, 0.2]`; a third transient error is re-raised and a permanent `ValueError` is never retried.

### Exercise 6 — Testing

**Prompt:** Test two transient failures followed by success with a list append sleeper, plus a
permanent `ValueError` that escapes immediately.

**Approach:** The successful scenario makes three calls and records `[base, base * 2]`; the
permanent failure makes one call and adds no delay because it is outside the retry
classification.

**Why this boundary matters:** Assert result, call count, and the complete delay sequence.

**Verification evidence:** Use an operation that fails transiently twice then returns `ok`; assert three calls, delays `[base, base*2]`, result `ok`, and a separate `ValueError` case has one call.

### Exercise 7 — Design

**Prompt:** Decide whether retry owns a statement, a complete transaction attempt, or an entire
command and justify the chosen scope.

**Approach:** Wrap one complete transaction attempt, including acquisition and rollback/close,
while the idempotency key protects replay. Retrying one statement inside an aborted transaction
is invalid, and retrying an overly broad command may repeat unrelated effects.

**Why this boundary matters:** A failed PostgreSQL transaction cannot safely continue; retry
needs fresh state.

**Verification evidence:** Produce a scope decision naming the complete transaction attempt as the retry unit and show why retrying only a statement can reuse an aborted transaction.

### Exercise 8 — Composition

**Prompt:** Compose retry with transaction ownership so every attempt receives fresh connection
state and cleanup happens before delay.

**Approach:** Pass a closure to `run_with_retry` that acquires a fresh connection and calls
`run_in_transaction`. Fake events should show rollback/close from attempt N before the sleeper
and acquisition for attempt N+1.

**Why this boundary matters:** The retry operation should create and finish one complete
transaction attempt.

**Verification evidence:** Record resource identities and events across two failures and success; assert each attempt gets a new connection and rollback/close precede the corresponding sleep.

### Exercise 9 — Extension

**Prompt:** Add optional jitter through an injected function while keeping tests deterministic
and delays bounded.

**Approach:** Compute the exponential base, pass it to an injected jitter function, clamp or
validate the returned delay, and feed a deterministic fake during tests. Keep the
no-sleep-after-final rule.

**Why this boundary matters:** Randomness is another effect boundary and should be injected.

**Verification evidence:** Inject fixed jitter values and assert every computed delay stays within the declared bounds; replaying the same jitter sequence must produce identical delays.

### Exercise 10 — Failure analysis

**Prompt:** Explain how a connection loss during commit creates an uncertain outcome and how the
idempotency key resolves the next attempt.

**Approach:** Retry with the same stable key. If the first commit succeeded, the unique conflict
returns `None`; if it did not, the retry inserts. Application reporting may need a follow-up
lookup when the existing job ID is required.

**Why this boundary matters:** The client may not know whether the server committed.

**Verification evidence:** Model a commit that succeeds server-side then raises client-side; assert the next attempt re-checks the idempotency key and reports the existing job without a second effect.

### Exercise 11 — Input validation

**Prompt:** Define and test boundaries for blank idempotency keys and oversized payloads before
opening a transaction.

**Approach:** Reject blank/whitespace keys and enforce an application payload-size ceiling, then
retain database `NOT NULL`, uniqueness, and size/type constraints as the authoritative
concurrent boundary.

**Why this boundary matters:** Fast local validation avoids obviously invalid database work but
does not replace constraints.

**Verification evidence:** Assert blank/whitespace keys and payloads above the declared byte limit fail before the connection factory or cursor is called.

### Exercise 12 — Concurrency

**Prompt:** Model two workers racing on the same idempotency key and identify which outcome the
unique constraint guarantees.

**Approach:** Exactly one insert can win; the other follows `DO NOTHING`. The order is
nondeterministic, but the number of logical rows is deterministic and no preliminary read is
required.

**Why this boundary matters:** A read-then-insert sequence cannot provide the same atomic
guarantee.

**Verification evidence:** Run two fake workers against one uniqueness arbiter; assert at most one receives an inserted ID and the other observes the duplicate path rather than a second logical job.

### Exercise 13 — Observability

**Prompt:** Design retry metrics with low-cardinality tags and no payload, key, exception
message, or request ID.

**Approach:** Count attempts/success/exhaustion with tags such as operation and exception class
from fixed allowlists; place a correlation ID only in redacted structured logs, never as a
metric tag.

**Why this boundary matters:** Dimensions should describe bounded classes, not individual
events.

**Verification evidence:** Inspect emitted metrics: tags are limited to bounded outcome/error-class fields and contain no payload, idempotency key, request ID, or exception message.

### Exercise 14 — Interruption

**Prompt:** Decide how cancellation or `KeyboardInterrupt` crosses transaction and retry layers
without being mistaken for a transient database error.

**Approach:** The transaction layer should roll back/close during interruption and re-raise. The
retry layer catches only `TransientDatabaseError`, so cancellation and operator interruption
escape immediately with no retry sleep.

**Why this boundary matters:** Cleanup may be broad, but retry classification should remain
narrow.

**Verification evidence:** Raise `KeyboardInterrupt` through the transaction/retry composition; assert rollback and close occur once and no delay or retry is scheduled.
