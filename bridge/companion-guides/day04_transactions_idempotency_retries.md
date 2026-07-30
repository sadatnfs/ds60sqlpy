# Bridge Day 4 — Transactions, idempotency, and retries

**Level:** Intermediate  
**Prerequisite:** [Bridge Day 3](day03_safe_psycopg_queries.md)

## Why this matters

A transaction defines which changes succeed or fail as one unit. A retry repeats
that unit, so retrying safely requires both a narrow transient-failure
classification and idempotent behavior. Retrying every exception can duplicate
data, hide programming bugs, and overload a struggling database.

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

## Run the starter

```powershell
.\.venv\Scripts\python.exe bridge\lessons\day04_transactions_idempotency_retries.py
```

```bash
.venv/bin/python bridge/lessons/day04_transactions_idempotency_retries.py
```

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
2. **SQL implementation:** Implement `create_job_once()` with one parameterized `INSERT`, a
   unique idempotency key, `ON CONFLICT DO NOTHING`, and `RETURNING job_id`.
   - **Progressive hint:** Let the uniqueness constraint arbitrate concurrency; do not pre-read.
3. **Mapping:** Return the inserted ID when `fetchone()` yields a row and `None` for a duplicate
   without issuing a second statement.
   - **Progressive hint:** Treat `None` as the documented `DO NOTHING` result.
4. **Transaction:** Implement `run_in_transaction()` so success commits and any operation
   failure rolls back before re-raising.
   - **Progressive hint:** The wrapper owns the boundary; the operation owns only domain work.
5. **Retry:** Implement `run_with_retry()` for only `TransientDatabaseError`, stopping at
   `max_attempts` with delays `base * 2**(attempt - 1)`.
   - **Progressive hint:** Never sleep after the last failed attempt and never catch permanent
     errors.
6. **Testing:** Test two transient failures followed by success with a list append sleeper, plus
   a permanent `ValueError` that escapes immediately.
   - **Progressive hint:** Assert result, call count, and the complete delay sequence.
7. **Design:** Decide whether retry owns a statement, a complete transaction attempt, or an
   entire command and justify the chosen scope.
   - **Progressive hint:** A failed PostgreSQL transaction cannot safely continue; retry needs
     fresh state.
8. **Composition:** Compose retry with transaction ownership so every attempt receives fresh
   connection state and cleanup happens before delay.
   - **Progressive hint:** The retry operation should create and finish one complete transaction
     attempt.
9. **Extension:** Add optional jitter through an injected function while keeping tests
   deterministic and delays bounded.
   - **Progressive hint:** Randomness is another effect boundary and should be injected.
10. **Failure analysis:** Explain how a connection loss during commit creates an uncertain
   outcome and how the idempotency key resolves the next attempt.
   - **Progressive hint:** The client may not know whether the server committed.
11. **Input validation:** Define and test boundaries for blank idempotency keys and oversized
   payloads before opening a transaction.
   - **Progressive hint:** Fast local validation avoids obviously invalid database work but does
     not replace constraints.
12. **Concurrency:** Model two workers racing on the same idempotency key and identify which
   outcome the unique constraint guarantees.
   - **Progressive hint:** A read-then-insert sequence cannot provide the same atomic guarantee.
13. **Observability:** Design retry metrics with low-cardinality tags and no payload, key,
   exception message, or request ID.
   - **Progressive hint:** Dimensions should describe bounded classes, not individual events.
14. **Interruption:** Decide how cancellation or `KeyboardInterrupt` crosses transaction and
   retry layers without being mistaken for a transient database error.
   - **Progressive hint:** Cleanup may be broad, but retry classification should remain narrow.

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

## Next step

[Day 5](day05_db_testing_fixtures_doubles.md) separates fast contract tests from
small PostgreSQL integration tests. After your attempt, review
[the Day 4 solution notes](../solutions/day04_solutions.md).
