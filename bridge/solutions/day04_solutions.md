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

