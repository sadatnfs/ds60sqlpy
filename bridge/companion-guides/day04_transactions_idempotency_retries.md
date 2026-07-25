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

1. Validate `RetryPolicy`: attempts must be at least one and delay non-negative.
2. Implement `create_job_once()` using one parameterized `INSERT`, a unique
   `idempotency_key`, `ON CONFLICT ... DO NOTHING`, and `RETURNING job_id`.
3. Return the new ID when inserted and `None` for a duplicate. Do not run a
   preliminary `SELECT`.
4. Implement `run_in_transaction()`. Commit after the operation returns; on any
   failure, roll back and re-raise.
5. Implement `run_with_retry()`. Retry only `TransientDatabaseError`, stop after
   `max_attempts`, and use delays `base * 2**(attempt - 1)`.
6. Test with a closure that fails twice, a list's `append` method as the fake
   sleeper, and a permanent `ValueError` that must escape immediately.
7. Explain whether the retry should wrap one statement, one transaction, or the
   entire command in your design.

### Progressive hints

1. `fetchone()` returns `None` after `DO NOTHING ... RETURNING`.
2. Do not sleep after the final failed attempt.
3. Run rollback before the exception crosses the transaction boundary.
4. A stable source event ID usually makes a better idempotency key than a random
   ID generated on each attempt.

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
