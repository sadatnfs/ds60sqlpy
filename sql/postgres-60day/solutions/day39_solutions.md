# Day 39: Solutions: Locks and Deadlocks


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day39_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Blocking, Deadlock, Advisory lock. Its worked-model focus is:
In two disposable sessions, lock test rows 1 and 2 in opposite orders and inspect the wait before PostgreSQL aborts one participant with `40P01`. Roll back, then repeat with both sessions ordering keys ascending to show the cycle cannot form.

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

## Exercise 1: Reproduce and observe a deadlock

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
SELECT
  a.pid,
  a.state,
  l.locktype,
  l.relation::regclass AS relation,
  l.mode,
  l.granted,
  pg_blocking_pids (a.pid) AS blocking_pids
FROM
  pg_stat_activity a
  JOIN pg_locks l ON l.pid = a.pid
WHERE
  cardinality(pg_blocking_pids (a.pid)) > 0
  OR NOT l.granted
ORDER BY
  a.pid,
  l.granted,
  l.locktype;
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

- **Inputs/evidence:** For sql-39 Exercise 1, use two terminals on the seeded `training.orders` rows with `order_id` 1 and 2: Session A locks row 1 then row 2, Session B locks row 2 then row 1 (with `SELECT ... FOR UPDATE` or a no-op `UPDATE ... SET total_amount = total_amount`), and a third terminal reads `pg_locks` while a session waits.
- **Expected result/shape:** For sql-39 Exercise 1, expected output: while Session A's second lock request waits, the third terminal shows one ungranted `transactionid` row (`mode = ShareLock`, `granted = false`) for Session A's `pid`; when Session B's second lock request closes the cycle, about one second later (`deadlock_timeout`) Session B fails with SQLSTATE `40P01` (`deadlock detected`) and Session A's waiting statement completes.
- **Independent verification:** For sql-39 Exercise 1, record each session's `pg_backend_pid()`, the waiting `pid` from `pg_locks`, and the two `DETAIL` lines (`Process ... waits for ShareLock on transaction ...`); end both transactions with `ROLLBACK` and confirm that `SELECT order_id, status, total_amount FROM training.orders WHERE order_id IN (1, 2) ORDER BY order_id` returns the same values as before the experiment.
- **Intermediate relation check:** For sql-39 Exercise 1, query `pg_locks` once after both first locks: each session holds its own `transactionid` lock (`ExclusiveLock`, granted) and nothing waits yet.
- **Clause check:** For sql-39 Exercise 1, each session runs `BEGIN`, a `SELECT ... FOR UPDATE` on one key, a no-op `UPDATE` on the other key, and `ROLLBACK`; the observer runs a read-only `SELECT` over `pg_stat_activity` and `pg_locks`.
- **Alternative/trade-off:** For sql-39 Exercise 1, `SET lock_timeout` bounds ordinary waits with SQLSTATE `55P03`, but it does not remove the cycle: with the default one-second `deadlock_timeout`, the deadlock detector still aborts one session unless `lock_timeout` is shorter. Only a consistent lock order (Exercise 2) prevents the cycle.
- **Edge case:** If Session B issues its second `UPDATE` first, the roles swap: the session whose wait closes the cycle normally receives `40P01`, so record which statement actually failed.

## Exercise 2: Prevent the deadlock with consistent ordering

Every worker must acquire the same set of row locks in the same order:

```sql
BEGIN;
SET LOCAL search_path TO training, public;

SET LOCAL lock_timeout = '5s';

SELECT
  order_id,
  total_amount
FROM
  orders
WHERE
  order_id IN (1, 2)
ORDER BY
  order_id
FOR UPDATE;

ROLLBACK;
```

Run the same transaction in both sessions. One may wait, but neither can hold
order 2 while requesting order 1, so this pair does not form a cycle.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 2, repeat the Exercise 1 schedule, but let both sessions lock `order_id` 1 and 2 in ascending order with one statement such as `SELECT order_id FROM training.orders WHERE order_id IN (1, 2) ORDER BY order_id FOR UPDATE`.
- **Expected result/shape:** For sql-39 Exercise 2, expected output: Session A's locking `SELECT` returns two rows, `order_id` 1 and 2; Session B's identical statement waits instead of deadlocking and returns the same two rows after Session A ends. No session receives SQLSTATE `40P01`.
- **Independent verification:** For sql-39 Exercise 2, while Session B waits, confirm in a third terminal that `SELECT locktype, mode FROM pg_locks WHERE NOT granted` returns exactly one row, a `transactionid` `ShareLock`; then rerun the opposite-order schedule from Exercise 1 to show that only the lock order changed.
- **Intermediate relation check:** For sql-39 Exercise 2, run the locking `SELECT` alone in one session and list `SELECT order_id FROM training.orders WHERE order_id IN (1, 2) ORDER BY order_id` first, so you know the two keys it must lock.
- **Clause check:** For sql-39 Exercise 2, the executable solution selects the first two `order_id` values in a `keys` CTE, joins them to `orders`, and keeps `ORDER BY o.order_id` in the locking `SELECT ... FOR UPDATE OF o`.
- **Alternative/trade-off:** For sql-39 Exercise 2, `pg_advisory_xact_lock` on a business key serializes the two workers without locking any row, but it works only if every writer takes the same advisory key first.
- **Edge case:** Add a third key to only one session's list: ascending order still prevents a cycle, because every session acquires shared keys in the same global order.

## Exercise 3: Job-queue claiming with `SKIP LOCKED`

```sql
CREATE TEMP TABLE solution_jobs (
  job_id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  payload text NOT NULL,
  processed_at timestamptz
);

INSERT INTO solution_jobs (payload)
VALUES
  ('first'),
  ('second'),
  ('third'),
  ('fourth');

SELECT
  job_id,
  payload
FROM
  solution_jobs
WHERE
  processed_at IS NULL
ORDER BY
  job_id
FOR UPDATE
  SKIP LOCKED
LIMIT 2;
```

The claim returns `(1, first)` and `(2, second)` and keeps them locked until the
transaction ends. To see queue behavior, create the same queue as a committed
disposable table, keep Session A open after its claim, and run the same `SELECT`
in Session B: B skips A's locked rows and returns jobs 3 and 4 at once. A
temporary table cannot demonstrate this, because only its creating session can
read it.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 3, create the temporary `solution_jobs` queue with four unprocessed jobs (`first` to `fourth`), then select the oldest two unprocessed jobs with `ORDER BY job_id FOR UPDATE SKIP LOCKED LIMIT 2`.
- **Expected result/shape:** For sql-39 Exercise 3, expected output: two rows with columns `job_id` and `payload`: `(1, first)` and `(2, second)`, now locked by this transaction.
- **Independent verification:** For sql-39 Exercise 3, recreate the queue as a committed disposable table, run the same claim in a second session while the first session still holds its locks, and confirm that the second session returns jobs `3` and `4` immediately instead of waiting; a temporary table cannot show this, because only its creating session can read it.
- **Intermediate relation check:** For sql-39 Exercise 3, count the unprocessed jobs (`4`) before claiming, so the two claimed rows can be reconciled with the two that remain free.
- **Clause check:** For sql-39 Exercise 3, the solution uses `CREATE TEMP TABLE`, one multi-row `INSERT`, and a `SELECT ... WHERE processed_at IS NULL ORDER BY job_id FOR UPDATE SKIP LOCKED LIMIT 2`.
- **Alternative/trade-off:** For sql-39 Exercise 3, plain `FOR UPDATE` makes every worker wait for the same first rows; `SKIP LOCKED` spreads workers over different rows but gives an intentionally incomplete view, so it is wrong for reports.
- **Edge case:** With every job locked by other workers, the claim returns zero rows at once; the worker should treat that as an empty queue, not as an error.

## Pitfalls

- `SKIP LOCKED` intentionally returns an inconsistent view and is appropriate
  for queues, not ordinary reports.
- `NOWAIT` fails immediately; `lock_timeout` bounds a wait; neither prevents a
  badly ordered locking design.
- Row locks are held until transaction end. Keep transactions short and never
  wait for user input while holding them.
- `total_amount = total_amount` is used only to request a write lock without
  changing course data; do not use no-op updates as a production lock pattern.

## Exercise 4: Predict NOWAIT

`FOR UPDATE NOWAIT` raises SQLSTATE `55P03` immediately when a conflicting lock
already exists. The executable solution explains the two-session check without
blocking automated validation.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 4, lock `order_id = 1` with `SELECT order_id FROM training.orders WHERE order_id = 1 FOR UPDATE` in Session A, then run the same statement in Session B once without and once with `NOWAIT`; the single-session script only plans the `NOWAIT` form with `EXPLAIN`.
- **Expected result/shape:** For sql-39 Exercise 4, expected output: without `NOWAIT`, Session B waits until Session A ends; with `NOWAIT`, it fails at once with SQLSTATE `55P03` (`could not obtain lock on row in relation "orders"`). The script's `EXPLAIN` shows a `LockRows` node above an index scan on `orders_pkey`.
- **Independent verification:** For sql-39 Exercise 4, record both outcomes and their SQLSTATE; then run `SET lock_timeout = '2s'` in Session B and confirm that the ordinary `FOR UPDATE` fails after about two seconds with SQLSTATE `55P03` (`canceling statement due to lock timeout`).
- **Intermediate relation check:** For sql-39 Exercise 4, run `SELECT order_id FROM training.orders WHERE order_id = 1` without a locking clause first: it returns one row and never waits, because plain reads do not block on row locks.
- **Clause check:** For sql-39 Exercise 4, the runnable statement is `EXPLAIN SELECT order_id FROM orders WHERE order_id = 1 FOR UPDATE NOWAIT`; the two-session part uses the same `SELECT ... FOR UPDATE` with and without `NOWAIT`.
- **Alternative/trade-off:** For sql-39 Exercise 4, `lock_timeout` allows a bounded wait instead of an immediate failure, which suits interactive work that can tolerate a short delay.
- **Edge case:** If Session A has already committed, both forms succeed immediately, so a passing `NOWAIT` test proves nothing unless the conflicting lock is open.

## Exercise 5: Claim and update queue rows

The locking CTE selects up to five unprocessed jobs with `SKIP LOCKED`; the
UPDATE joins only those keys and `RETURNING` proves exactly what this worker
claimed.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 5, claim at most five unprocessed `solution_jobs` rows in one statement: a `claimed` CTE with `ORDER BY job_id FOR UPDATE SKIP LOCKED LIMIT 5`, joined by an `UPDATE` that sets `processed_at` and returns `job_id`, `payload`, and `processed_at`.
- **Expected result/shape:** For sql-39 Exercise 5, expected output: four rows, `job_id` 1 to 4 with their `payload` and a non-NULL `processed_at`, and the command tag `UPDATE 4`. Jobs 1 and 2 are not skipped even though Exercise 3 locked them, because `SKIP LOCKED` skips only rows locked by other transactions.
- **Independent verification:** For sql-39 Exercise 5, count `SELECT COUNT(*) FROM solution_jobs WHERE processed_at IS NULL` before (`4`) and after (`0`) the claim and compare the difference with `UPDATE 4` and the four returned `job_id` values; a second claim in the same transaction returns zero rows.
- **Intermediate relation check:** For sql-39 Exercise 5, run the `claimed` CTE body alone first: it returns the `job_id` values 1 to 4, which the `UPDATE` must then return exactly once each.
- **Clause check:** For sql-39 Exercise 5, the statement is `WITH claimed AS (SELECT ... FOR UPDATE SKIP LOCKED LIMIT 5) UPDATE solution_jobs j SET processed_at = clock_timestamp() FROM claimed c WHERE j.job_id = c.job_id RETURNING ...`.
- **Alternative/trade-off:** For sql-39 Exercise 5, selecting the jobs and updating them in two statements works only inside one transaction that keeps the locks; the single statement makes the claim and the update one atomic step.
- **Edge case:** With fewer than five free jobs, the claim returns only the free ones (here four); with none free, it returns zero rows and `UPDATE 0`.

## Exercise 6: Preserve lock order

Keys and the final locking SELECT both order by the unique `order_id`. Every
writer must share that order for the pattern to prevent cycles.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 6, compare a locking query whose only `ORDER BY` is inside a CTE with the repaired form that keeps `ORDER BY o.order_id` in the locking `SELECT ... FOR UPDATE OF o`, over orders with `total_amount > 900`.
- **Expected result/shape:** For sql-39 Exercise 6, expected output: five rows with one column, `order_id`: `4`, `8`, `12`, `19`, and `24` on the course seed, returned and locked in ascending order.
- **Independent verification:** For sql-39 Exercise 6, run `EXPLAIN (COSTS OFF)` on both forms: in the repaired form the rows reach `LockRows` already in `order_id` order (on PostgreSQL 17, a nested loop driven by the ordered CTE scan), while the CTE-only form has no outer `ORDER BY`, so its lock order follows whatever join method the planner picks. Confirm that `SELECT COUNT(*) FROM training.orders WHERE total_amount > 900` returns `605`, so the five-row limit is reached.
- **Intermediate relation check:** For sql-39 Exercise 6, run the `ordered_keys` CTE body alone: it returns the same five keys, which the outer locking `SELECT` must lock in that order.
- **Clause check:** For sql-39 Exercise 6, the solution uses a `MATERIALIZED` CTE with `ORDER BY order_id LIMIT 5`, joins it to `orders` with `USING (order_id)`, and ends with `ORDER BY o.order_id FOR UPDATE OF o`.
- **Alternative/trade-off:** For sql-39 Exercise 6, the simplest repair drops the CTE: `SELECT o.order_id FROM orders o WHERE o.total_amount > 900 ORDER BY o.order_id LIMIT 5 FOR UPDATE`, whose plan is `Limit` above `LockRows` above an ordered index scan.
- **Edge case:** Dropping `OF o` changes nothing here, because a locking clause never applies to the rows of a `WITH` query; `OF o` documents which relation is locked. To lock rows inside a CTE, put the locking clause in the CTE body itself.

## Exercise 7: Prefer transaction advisory locks

`pg_try_advisory_xact_lock` is non-blocking and releases automatically when the
transaction ends. It works only if all cooperating applications derive the same
lock key.

### Reasoning and verification

- **Inputs/evidence:** For sql-39 Exercise 7, call `pg_try_advisory_xact_lock(3902)` twice inside the lesson transaction, then once from a second session while the first transaction is still open.
- **Expected result/shape:** For sql-39 Exercise 7, expected output: two one-row results, `first_attempt = true` and `same_owner_attempt = true`, because the owning backend may take the same lock again; the second session's call returns `false` until the first transaction ends.
- **Independent verification:** For sql-39 Exercise 7, while the first transaction is open, `SELECT locktype, objid, mode, granted FROM pg_locks WHERE locktype = 'advisory'` shows one row with `objid = 3902` and `ExclusiveLock`; after `ROLLBACK`, that query returns no row and the second session's call returns `true`, without any `pg_advisory_unlock`.
- **Intermediate relation check:** For sql-39 Exercise 7, run the second session's `pg_try_advisory_xact_lock(3902)` before the first session takes the lock: it returns `true`, which shows that the later `false` is caused by the open transaction.
- **Clause check:** For sql-39 Exercise 7, the solution runs two scalar `SELECT pg_try_advisory_xact_lock(3902)` statements labelled `first_attempt` and `same_owner_attempt`.
- **Alternative/trade-off:** For sql-39 Exercise 7, session-level `pg_try_advisory_lock` survives `COMMIT` and needs an explicit `pg_advisory_unlock`; a forgotten unlock then blocks other workers until the connection closes.
- **Edge case:** `pg_advisory_xact_lock(3902)` (without `try`) waits instead of returning `false`, so it can block a worker indefinitely unless `lock_timeout` is set.
