# Bridge Day 4 — Transactions, idempotency, and retries

**Level:** Intermediate  
**Prerequisite:** [Bridge Day 3](day03_safe_psycopg_queries.md)

## Why this matters

A transaction defines which changes succeed or fail as one unit. A retry repeats
that unit, so retrying safely requires both a narrow transient-failure
classification and idempotent behavior. Retrying every exception can duplicate
data, hide programming bugs, and overload a struggling database.


<!-- BEGIN BRIDGE ENRICHMENT: HOW TO RUN -->
## How to run this lesson

Start at the repository root. The answer-free starter is deliberately safe to
run: it prints orientation text and does not call unfinished functions or
contact PostgreSQL.

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\lessons\day04_transactions_idempotency_retries.py
.\.venv\Scripts\python.exe -m pytest bridge\tests -q
```

```bash
# macOS/Linux
.venv/bin/python bridge/lessons/day04_transactions_idempotency_retries.py
.venv/bin/python -m pytest bridge/tests -q
```

Read this guide first, implement one boundary at a time in
`bridge/lessons/day04_transactions_idempotency_retries.py`, and use small fakes or recording doubles for the
default evidence path. Any PostgreSQL step is optional, explicitly gated, and restricted to `DS60_DATABASE_URL` plus the disposable `advanced_sql_training` database. Never place a credential in source, notebook output, test fixtures, or logs.
<!-- END BRIDGE ENRICHMENT: HOW TO RUN -->

## Objectives

By the end, you can:

- define an explicit transaction boundary around one operation;
- roll back before propagating failures;
- use a unique idempotency key with PostgreSQL `ON CONFLICT`;
- retry only classified transient failures;
- inject a sleeper to test exponential delays without waiting.

## Vocabulary

| Term | Meaning |
|---|---|
| transaction | A group of database changes that commits or rolls back as one unit |
| atomicity | The all-or-nothing property of a transaction |
| idempotent | Safe to repeat without creating an additional logical effect |
| idempotency key | A stable request identity protected by a uniqueness constraint |
| transient failure | A condition that may succeed later, such as a brief connection interruption |
| exponential backoff | Delays that grow between attempts |


## Worked example: retry is a policy, not a blanket `except`

```python
for attempt in range(max_attempts):
    try:
        return operation()
    except KnownTransientError:
        if attempt + 1 == max_attempts:
            raise
        sleeper(delay_for(attempt))
```

The retry loop does not catch `Exception`. A syntax error, failed validation, or
constraint violation needs investigation, not repetition. In production,
Psycopg exception classes and SQLSTATE codes provide the classification; this
exercise uses a deterministic custom exception.

For idempotency, the database must enforce uniqueness. An application-side
“check then insert” has a race between the two statements.


<!-- BEGIN BRIDGE ENRICHMENT: DEEP DIVE -->
## Mental model: three policies that must agree

Transactions, idempotency, and retries solve different failure problems. A
transaction defines which effects commit together. Idempotency defines what a
repeated logical request means. Retry policy defines which failures may be
attempted again, how often, and after what delay. Reliable code requires all
three policies to agree; adding exponential backoff to an unsafe write only
makes duplication slower.

For this lesson, the database unique constraint is the concurrency authority.
`INSERT ... ON CONFLICT DO NOTHING RETURNING ...` lets one statement decide
whether a logical job was created. A prior `SELECT` followed by `INSERT` has a
race between the two statements. The idempotency key also needs a product
scope: which requests share it, how long it is retained, and whether the same
key with different payloads is rejected.

Retry behavior should be deterministic under test. Inject the sleeper and
record requested delays instead of waiting:

```python
delays: list[float] = []


def fake_sleep(seconds: float) -> None:
    delays.append(seconds)


for attempt in range(2):
    fake_sleep(0.25 * (2**attempt))

assert delays == [0.25, 0.5]
```

Every retry attempt must own a fresh transaction. Once PostgreSQL marks a
transaction failed, repeating a statement inside that same transaction does
not recover it. The safe order is acquire, perform one complete operation,
commit or roll back, close, and only then wait before the next attempt.
Permanent validation errors must escape immediately.

The hardest case is an uncertain commit: the server may have committed even
though the client received a connection error. An exception is evidence that
the client lacks an answer, not proof that the server rolled back. A retry must
re-check durable idempotency evidence before replaying effects. Metrics should
record bounded outcome and attempt information without payloads or
high-cardinality idempotency keys.
<!-- END BRIDGE ENRICHMENT: DEEP DIVE -->

## Exercises

### Practice contract

- **Focus:** Make writes safe to repeat by combining a database uniqueness boundary, explicit transaction ownership, and narrowly classified retries.
- **Assumptions:** One stable source key identifies one logical job; each retry executes a fresh transaction attempt; fake sleepers keep tests deterministic.
- **Primary failure mode:** Retrying a non-idempotent or ambiguously committed write can duplicate effects even when backoff logic is correct.
- **Evidence loop:** predict the boundary, implement the smallest change,
  verify success and failure with a deterministic fake, then explain which
  behavior still requires an explicitly enabled PostgreSQL integration test.

1. **Validation:** Validate `RetryPolicy` so attempts are at least one and base delay is finite
   and non-negative.
   - **Progressive hint:** Reject unusable policy at construction rather than inside a failing
     retry loop.
   - **Verify:** Construct policies at attempts `0/1` and delays `-1/0/inf/nan`; assert only attempts at least one with finite non-negative delay succeed and every invalid case raises `ValueError` immediately.
2. **SQL implementation:** Implement `create_job_once()` with one parameterized `INSERT`, a
   unique idempotency key, `ON CONFLICT DO NOTHING`, and `RETURNING job_id`.
   - **Progressive hint:** Let the uniqueness constraint arbitrate concurrency; do not pre-read.
   - **Verify:** Record one cursor call and assert static SQL contains `ON CONFLICT ... DO NOTHING` plus `RETURNING job_id`, while idempotency key and payload appear only in the two-value tuple.
3. **Mapping:** Return the inserted ID when `fetchone()` yields a row and `None` for a duplicate
   without issuing a second statement.
   - **Progressive hint:** Treat `None` as the documented `DO NOTHING` result.
   - **Verify:** Configure `fetchone()` as `(42,)` then `None`; assert results are `42` and `None` and each case issues exactly one statement.
4. **Transaction:** Implement `run_in_transaction()` so success commits and any operation
   failure rolls back before re-raising.
   - **Progressive hint:** The wrapper owns the boundary; the operation owns only domain work.
   - **Verify:** Assert success events end `operation, commit` with no rollback; failure events end `operation, rollback`, no commit occurs, and the same exception is re-raised.
5. **Retry:** Implement `run_with_retry()` for only `TransientDatabaseError`, stopping at
   `max_attempts` with delays `base * 2**(attempt - 1)`.
   - **Progressive hint:** Never sleep after the last failed attempt and never catch permanent
     errors.
   - **Verify:** For base delay `0.1` and three attempts, assert delays are `[0.1, 0.2]`; a third transient error is re-raised and a permanent `ValueError` is never retried.
6. **Testing:** Test two transient failures followed by success with a list append sleeper, plus
   a permanent `ValueError` that escapes immediately.
   - **Progressive hint:** Assert result, call count, and the complete delay sequence.
   - **Verify:** Use an operation that fails transiently twice then returns `ok`; assert three calls, delays `[base, base*2]`, result `ok`, and a separate `ValueError` case has one call.
7. **Design:** Decide whether retry owns a statement, a complete transaction attempt, or an
   entire command and justify the chosen scope.
   - **Progressive hint:** A failed PostgreSQL transaction cannot safely continue; retry needs
     fresh state.
   - **Verify:** Produce a scope decision naming the complete transaction attempt as the retry unit and show why retrying only a statement can reuse an aborted transaction.
8. **Composition:** Compose retry with transaction ownership so every attempt receives fresh
   connection state and cleanup happens before delay.
   - **Progressive hint:** The retry operation should create and finish one complete transaction
     attempt.
   - **Verify:** Record resource identities and events across two failures and success; assert each attempt gets a new connection and rollback/close precede the corresponding sleep.
9. **Extension:** Add optional jitter through an injected function while keeping tests
   deterministic and delays bounded.
   - **Progressive hint:** Randomness is another effect boundary and should be injected.
   - **Verify:** Inject fixed jitter values and assert every computed delay stays within the declared bounds; replaying the same jitter sequence must produce identical delays.
10. **Failure analysis:** Explain how a connection loss during commit creates an uncertain
   outcome and how the idempotency key resolves the next attempt.
   - **Progressive hint:** The client may not know whether the server committed.
   - **Verify:** Model a commit that succeeds server-side then raises client-side; assert the next attempt re-checks the idempotency key and reports the existing job without a second effect.
11. **Input validation:** Define and test boundaries for blank idempotency keys and oversized
   payloads before opening a transaction.
   - **Progressive hint:** Fast local validation avoids obviously invalid database work but does
     not replace constraints.
   - **Verify:** Assert blank/whitespace keys and payloads above the declared byte limit fail before the connection factory or cursor is called.
12. **Concurrency:** Model two workers racing on the same idempotency key and identify which
   outcome the unique constraint guarantees.
   - **Progressive hint:** A read-then-insert sequence cannot provide the same atomic guarantee.
   - **Verify:** Run two fake workers against one uniqueness arbiter; assert at most one receives an inserted ID and the other observes the duplicate path rather than a second logical job.
13. **Observability:** Design retry metrics with low-cardinality tags and no payload, key,
   exception message, or request ID.
   - **Progressive hint:** Dimensions should describe bounded classes, not individual events.
   - **Verify:** Inspect emitted metrics: tags are limited to bounded outcome/error-class fields and contain no payload, idempotency key, request ID, or exception message.
14. **Interruption:** Decide how cancellation or `KeyboardInterrupt` crosses transaction and
   retry layers without being mistaken for a transient database error.
   - **Progressive hint:** Cleanup may be broad, but retry classification should remain narrow.
   - **Verify:** Raise `KeyboardInterrupt` through the transaction/retry composition; assert rollback and close occur once and no delay or retry is scheduled.

### Before opening the solution

- State the input/output and ownership boundary in one sentence.
- Show one normal case, one edge case, and one failure case.
- Inspect recorded calls rather than relying on plausible output.
- Confirm no credential, payload, or high-cardinality identifier was emitted.


## Optional live-DB step

Use one disposable connection. Inside it, create:

```sql
CREATE TEMP TABLE bridge_jobs (
    job_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    idempotency_key text NOT NULL UNIQUE,
    payload text NOT NULL
) ON COMMIT DROP;
```

Call your insert twice with the same key and verify that the second result is
`None`. Then explicitly call `rollback()`. The solution targets
`pg_temp.bridge_jobs`, so it cannot accidentally write a persistent table.

Set the URL in the current shell only:

```powershell
$env:DS60_DATABASE_URL = "postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
```

```bash
export DS60_DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/advanced_sql_training"
```

## Self-check

- Is uniqueness enforced by PostgreSQL, not only Python?
- Does a duplicate request create zero additional rows?
- Does rollback occur exactly once on operation failure?
- Are delay values deterministic in tests?
- Does a permanent error escape after one attempt?

## Common pitfalls

- **Retrying inside an aborted transaction:** PostgreSQL rejects later
  statements until that transaction is rolled back.
- **Generating a fresh key for every attempt:** that defeats idempotency.
- **Catching all exceptions:** programming and data errors become slow,
  confusing failures.
- **Unbounded attempts:** a command can hang and amplify an outage.
- **Keeping a transaction open while sleeping:** release the failed transaction
  before backoff.


<!-- BEGIN BRIDGE ENRICHMENT: ASK CODEX -->
## Ask Codex about this lesson

Use the checked-in `guide-ds60sqlpy-learning` skill as a tutor, not as an
answer generator. The direct catalog prerequisites are `bridge-03`. The
prompt below deliberately names exact paths so a new Codex task can orient
itself without guessing.

```text
Tutor me through stable lesson ID bridge-04: Transactions Idempotency Retries.
Direct catalog prerequisites: bridge-03. Assume I completed exactly those
prerequisites, then begin with one short Retrieval question that connects each
prerequisite to this lesson.

Use repository skill guide-ds60sqlpy-learning.
Companion guide: bridge/companion-guides/day04_transactions_idempotency_retries.md
Learner artifact: bridge/lessons/day04_transactions_idempotency_retries.py

Do not open, quote, summarize, or copy anything under solutions/ until I
explicitly say I have finished my attempt and ask to compare.

Use these coaching phases in order:
1. Predict — ask what I expect before I run or change code.
2. Attempt — let me implement or explain one numbered exercise at a time.
3. Hint — give the smallest useful conceptual hint, never a finished answer.
4. Evidence — ask for the exact return value, exception type, recorded calls,
   query plus bound parameters, or written decision required by that exercise.
5. Retrieval — close with two no-notes questions and one transfer problem.

Keep the default path offline and fake-first. If the lesson has an optional
PostgreSQL step, require my explicit opt-in, DS60_DATABASE_URL, and the
disposable advanced_sql_training database; never ask me to paste the URL.

Done when every numbered exercise has its own evidence, normal/edge/failure
behavior is explained in my words, the relevant offline tests pass, and I can
solve the final transfer problem without opening solutions/.
```
<!-- END BRIDGE ENRICHMENT: ASK CODEX -->

## Next step

[Day 5](day05_db_testing_fixtures_doubles.md) separates fast contract tests from
small PostgreSQL integration tests. After your attempt, review
[the Day 4 solution notes](../solutions/day04_solutions.md).
