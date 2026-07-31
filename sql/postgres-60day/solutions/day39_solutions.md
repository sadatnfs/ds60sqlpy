# Day 39 — Solutions: Locks and Deadlocks


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day39_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day39_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Blocking, Deadlock, Advisory lock. Its worked-model focus is:
In two disposable sessions, lock test rows 1 and 2 in opposite orders and inspect the wait before PostgreSQL aborts one participant with 40P01. Roll back, then repeat with both sessions ordering keys ascending to show the cycle cannot form.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

Deadlocks and lock waits require concurrent sessions. A single sequential
solution file cannot fully execute these labs. Use two terminals for the
staged commands and a third terminal when observing a wait.

## Exercise 1 — Reproduce and observe a deadlock

Session A locks order 1:

```text
BEGIN;
SET LOCAL search_path TO training, public;
SELECT order_id FROM orders WHERE order_id = 1 FOR UPDATE;
```

Session B locks order 2:

```text
BEGIN;
SET LOCAL search_path TO training, public;
SELECT order_id FROM orders WHERE order_id = 2 FOR UPDATE;
```

Session A now waits for B:

```text
UPDATE training.orders
SET total_amount = total_amount
WHERE order_id = 2;
```

Before completing the cycle, run this safe diagnostic in a third session:

```sql
SELECT a.pid,
       a.state,
       l.locktype,
       l.relation::regclass AS relation,
       l.mode,
       l.granted,
       pg_blocking_pids(a.pid) AS blocking_pids
FROM pg_stat_activity a
JOIN pg_locks l ON l.pid = a.pid
WHERE cardinality(pg_blocking_pids(a.pid)) > 0
   OR NOT l.granted
ORDER BY a.pid, l.granted, l.locktype;
```

Then Session B completes the cycle:

```text
UPDATE training.orders
SET total_amount = total_amount
WHERE order_id = 1;
```

PostgreSQL detects the cycle and aborts one transaction with
`deadlock detected`; roll back both sessions afterward. The detector normally
resolves the deadlock quickly, so the diagnostic captures the lock wait before
the final cycle edge rather than promising to freeze a deadlock.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 1, read the target keys from `orders`, and `pg_locks` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-39 Exercise 1, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`.
- **Independent verification:** For sql-39 Exercise 1, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `pg_locks` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
- **Intermediate relation check:** For sql-39 Exercise 1, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `pg_locks` again and prove rollback or idempotent retry.
- **Clause check:** For sql-39 Exercise 1, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, and `pg_locks`, preserve one row per `order_id`, and finish with `order_id`.
- **Alternative/trade-off:** For sql-39 Exercise 1, the chosen form is justified by this lesson-specific rationale: Session A locks order 1: Session B locks order 2: Session A now waits for B: Before completing the cycle, run this safe diagnostic in a third session: Then Session B completes the cycle: PostgreSQL detects the. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `order_id` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.

## Exercise 2 — Prevent the deadlock with consistent ordering

Every worker must acquire the same set of row locks in the same order:

```sql
BEGIN;
SET LOCAL search_path TO training, public;
SET LOCAL lock_timeout = '5s';

SELECT order_id,
       total_amount
FROM orders
WHERE order_id IN (1, 2)
ORDER BY order_id
FOR UPDATE;

ROLLBACK;
```

Run the same transaction in both sessions. One may wait, but neither can hold
order 2 while requesting order 1, so this pair does not form a cycle.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 2, read the target keys from `orders` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-39 Exercise 2, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`, and `total_amount`. The final order is `order_id FOR UPDATE`.
- **Independent verification:** For sql-39 Exercise 2, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
- **Intermediate relation check:** For sql-39 Exercise 2, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders` again and prove rollback or idempotent retry.
- **Clause check:** For sql-39 Exercise 2, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, and `total_amount` ordered by `order_id FOR UPDATE`.
- **Alternative/trade-off:** For sql-39 Exercise 2, the chosen form is justified by this lesson-specific rationale: Every worker must acquire the same set of row locks in the same order: Run the same transaction in both sessions. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `order_id` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.

## Exercise 3 — Job-queue claiming with `SKIP LOCKED`

```sql
BEGIN;
SET LOCAL search_path TO training, public;

SELECT order_id,
       order_date,
       status
FROM orders
WHERE status = 'placed'
ORDER BY order_id
LIMIT 5
FOR UPDATE SKIP LOCKED;

ROLLBACK;
```

To see queue behavior, keep the first session open before `ROLLBACK` and run the
same `SELECT` in Session B. B skips A's locked rows and can claim a different
batch.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 3, read the target keys from `orders`, and `SKIP` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-39 Exercise 3, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`, `order_date`, and `status`. The final order is `order_id`.
- **Independent verification:** For sql-39 Exercise 3, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `SKIP` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
- **Intermediate relation check:** For sql-39 Exercise 3, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `SKIP` again and prove rollback or idempotent retry.
- **Clause check:** For sql-39 Exercise 3, the solution actually uses `FROM`, `WHERE`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, and `SKIP`, preserve one row per `order_id`, and finish with `order_id`, `order_date`, and `status` ordered by `order_id`.
- **Alternative/trade-off:** For sql-39 Exercise 3, the chosen form is justified by this lesson-specific rationale: To see queue behavior, keep the first session open before `ROLLBACK` and run the same `SELECT` in Session B. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `order_id` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.

## Pitfalls

- `SKIP LOCKED` intentionally returns an inconsistent view and is appropriate
  for queues, not ordinary reports.
- `NOWAIT` fails immediately; `lock_timeout` bounds a wait; neither prevents a
  badly ordered locking design.
- Row locks are held until transaction end. Keep transactions short and never
  wait for user input while holding them.
- `total_amount = total_amount` is used only to request a write lock without
  changing course data; do not use no-op updates as a production lock pattern.

## Exercise 4 — Predict NOWAIT

`FOR UPDATE NOWAIT` raises SQLSTATE `55P03` immediately when a conflicting lock
already exists. The executable solution explains the two-session check without
blocking automated validation.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 4, run the underlying read-only query over `orders`, and `NOWAIT` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-39 Exercise 4, expected output: one row per `order_id`. The final columns are `order_id`.
- **Independent verification:** For sql-39 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-39 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
- **Clause check:** For sql-39 Exercise 4, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, and `NOWAIT`, preserve one row per `order_id`, and finish with `order_id`.
- **Alternative/trade-off:** For sql-39 Exercise 4, the chosen form is justified by this lesson-specific rationale: `FOR UPDATE NOWAIT` raises SQLSTATE `55P03` immediately when a conflicting lock already exists. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 5 — Claim and update queue rows

The locking CTE selects up to five unprocessed jobs with `SKIP LOCKED`; the
UPDATE joins only those keys and `RETURNING` proves exactly what this worker
claimed.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 5, read the target keys from `solution_jobs`, and `SKIP` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-39 Exercise 5, expected output: up to five unprocessed jobs with `SKIP LOCKED`; the UPDATE joins only those keys and `RETURNING` proves exactly what this worker claimed. The final columns are `returning`.
- **Independent verification:** For sql-39 Exercise 5, materialize the intended `returning` target set first; require the command tag/`RETURNING` set to match it, then query `solution_jobs`, and `SKIP` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `returning` values in both cases.
- **Intermediate relation check:** For sql-39 Exercise 5, run `claimed` one at a time. Record each CTE's row count and `returning` uniqueness before the next stage uses it.
- **Clause check:** For sql-39 Exercise 5, the solution actually uses `WITH`, `FROM`, `WHERE`, `SELECT`, `ORDER BY`, `LIMIT`, and `RETURNING`. Read only those operations: begin at `solution_jobs`, and `SKIP`, preserve one row per `returning`, and finish with `returning`.
- **Alternative/trade-off:** For sql-39 Exercise 5, the chosen form is justified by this lesson-specific rationale: The locking CTE selects up to five unprocessed jobs with `SKIP LOCKED`; the UPDATE joins only those keys and `RETURNING` proves exactly what this worker claimed. Evaluate another form against the concrete expected result (up to five unprocessed jobs with `SKIP LOCKED`; the UPDATE joins only those keys and `RETURNING` proves exactly what this worker claimed) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `returning` values in both cases.

## Exercise 6 — Preserve lock order

Keys and the final locking SELECT both order by the unique `order_id`. Every
writer must share that order for the pattern to prevent cycles.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 6, read the target keys from `orders`, `ordered_keys`, and `OF` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-39 Exercise 6, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`. The final order is `o.order_id FOR UPDATE OF o`.
- **Independent verification:** For sql-39 Exercise 6, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, `ordered_keys`, and `OF` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
- **Intermediate relation check:** For sql-39 Exercise 6, start with the first relation in `orders`, `ordered_keys`, and `OF`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-39 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, `ordered_keys`, and `OF`, preserve one row per `order_id`, and finish with `order_id` ordered by `o.order_id FOR UPDATE OF o`.
- **Alternative/trade-off:** For sql-39 Exercise 6, the chosen form is justified by this lesson-specific rationale: Keys and the final locking SELECT both order by the unique `order_id`. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `order_id` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.

## Exercise 7 — Prefer transaction advisory locks

`pg_try_advisory_xact_lock` is non-blocking and releases automatically when the
transaction ends. It works only if all cooperating applications derive the same
lock key.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 7, read from `pg_try_advisory_xact_lock`. Compute `ROLLBACK` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-39 Exercise 7, expected output: exactly one aggregate summary row. The final columns are `ROLLBACK`.
- **Independent verification:** For sql-39 Exercise 7, evaluate each of `row_count` in a separate control `SELECT` over `pg_try_advisory_xact_lock`; require one final row and compare every value. Add one source row with a new `ROLLBACK`; verify the result gains exactly one row carrying that `ROLLBACK` value.
- **Intermediate relation check:** For sql-39 Exercise 7, select `ROLLBACK` from `pg_try_advisory_xact_lock` before adding derived columns.
- **Clause check:** For sql-39 Exercise 7, the solution actually uses `SELECT`. Read only those operations: begin at `pg_try_advisory_xact_lock`, preserve exactly one summary row, and finish with `ROLLBACK`.
- **Alternative/trade-off:** For sql-39 Exercise 7, the chosen form is justified by this lesson-specific rationale: `pg_try_advisory_xact_lock` is non-blocking and releases automatically when the transaction ends. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add one source row with a new `ROLLBACK`; verify the result gains exactly one row carrying that `ROLLBACK` value.
