# Day 38: Solutions: Transactions and Isolation


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day38_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are MVCC, Isolation level, Serialization failure. Its worked-model focus is:
Open two disposable sessions and write down each statement before running it. Under `READ COMMITTED`, have session A read a count, session B commit a matching insert, and session A read again. Repeat at `REPEATABLE READ` and explain the snapshot difference; clean up the shared disposable table afterward.

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

Isolation anomalies require genuinely concurrent database sessions. They cannot
be proven by running one `.sql` file serially. Open two VS Code terminals, name
them Session A and Session B, and paste each step only when instructed.

The following single-session check is safe to run independently and demonstrates
transaction-local isolation plus savepoint rollback:

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SET LOCAL search_path TO training, public;

SHOW TRANSACTION ISOLATION LEVEL;

CREATE TEMP TABLE savepoint_demo (
  id int PRIMARY KEY,
  qty int NOT NULL
);

INSERT INTO savepoint_demo
  VALUES (1, 10);

SAVEPOINT before_change;

UPDATE
  savepoint_demo
SET
  qty = qty + 100
WHERE
  id = 1;

ROLLBACK TO SAVEPOINT before_change;

SELECT
  id,
  qty
FROM
  savepoint_demo;

ROLLBACK;
```

Expected row: `(1, 10)`.

## Lab setup

Run this once in either terminal. The table is deliberately course-specific,
but it is persistent because temporary tables cannot be shared by two sessions.

```text
SET search_path TO training, public;
DROP TABLE IF EXISTS isolation_lab;
CREATE TABLE isolation_lab (
  id int PRIMARY KEY,
  qty int NOT NULL
);
INSERT INTO isolation_lab VALUES (1, 10), (2, 20);
```

## Exercise 1: Non-repeatable read under `READ COMMITTED`

Session A:

```text
BEGIN ISOLATION LEVEL READ COMMITTED;
SET LOCAL search_path TO training, public;
SELECT qty FROM isolation_lab WHERE id = 1;  -- 10
```

While A remains open, Session B:

```text
BEGIN;
SET LOCAL search_path TO training, public;
UPDATE isolation_lab SET qty = 15 WHERE id = 1;
COMMIT;
```

Back in Session A:

```text
SELECT qty FROM isolation_lab WHERE id = 1;  -- now 15
ROLLBACK;
```

The two reads in A return different committed versions because
`READ COMMITTED` takes a new statement snapshot. Repeat the sequence with
`REPEATABLE READ`; A's second read remains `10` until A ends.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 1, use two terminals and the committed lab table `training.isolation_lab` from the lab setup, seeded with rows `(1, 10)` and `(2, 20)`; Session B changes only the row with `id = 1`.
- **Expected result/shape:** For sql-38 Exercise 1, expected output: under `READ COMMITTED`, Session A's two `SELECT qty FROM training.isolation_lab WHERE id = 1` statements return one row each, `10` and then `15`, because Session B commits `qty = 15` between them; under `REPEATABLE READ` the second read still returns `10`.
- **Independent verification:** For sql-38 Exercise 1, record both `qty` values, the commit order, and each session's level from `SHOW transaction_isolation`; after both sessions end, `SELECT id, qty FROM training.isolation_lab ORDER BY id` returns `(1, 15)` and `(2, 20)`. Reset `id = 1` to `10` before repeating the schedule at `REPEATABLE READ`.
- **Intermediate relation check:** For sql-38 Exercise 1, while Session A waits between its two reads, Session B can run `SELECT pid, state FROM pg_stat_activity WHERE datname = current_database()` and see Session A as `idle in transaction`.
- **Clause check:** For sql-38 Exercise 1, each session uses `BEGIN ISOLATION LEVEL ...`, one statement on the row with `id = 1` (`SELECT qty` in A, `UPDATE` in B), and `COMMIT` or `ROLLBACK`; the result depends on the interleaving, not on query shape.
- **Alternative/trade-off:** For sql-38 Exercise 1, `SELECT qty ... WHERE id = 1 FOR SHARE` in Session A makes Session B's `UPDATE` wait until A ends, so A reads `10` twice even under `READ COMMITTED`; that trades concurrency for a stable value.
- **Edge case:** Run Session B's `UPDATE` without `COMMIT`: Session A's second read still returns `10`, because PostgreSQL never shows uncommitted changes to other sessions (no dirty reads at any level).

## Exercise 2: Phantom rows between two counts

Reset, then start Session A:

```text
DELETE FROM training.isolation_lab WHERE id >= 3;
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT COUNT(*) FROM training.isolation_lab WHERE qty >= 20;  -- 1
```

Session B inserts a new qualifying row:

```text
BEGIN;
INSERT INTO training.isolation_lab(id, qty) VALUES (3, 30);
COMMIT;
```

Back in Session A:

```text
SELECT COUNT(*) FROM training.isolation_lab WHERE qty >= 20;  -- 2
ROLLBACK;
```

The new qualifying row is a phantom. Under `REPEATABLE READ`, Session A would
continue to see its original predicate result.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 2, start from `training.isolation_lab` with no row whose `id >= 3`; Session A counts rows matching `qty >= 20` twice while Session B inserts and commits `(3, 30)` between the two counts.
- **Expected result/shape:** For sql-38 Exercise 2, expected output: under `READ COMMITTED`, Session A's two one-row `count` results are `1` and then `2`, because the committed row `(3, 30)` is a phantom; under `REPEATABLE READ`, both counts are `1` until Session A ends.
- **Independent verification:** For sql-38 Exercise 2, record both `count` values and the commit order at each isolation level; after each run, `SELECT COUNT(*) FROM training.isolation_lab WHERE id = 3` returns `1`, proving Session B's insert was committed. Delete the row with `id = 3` before repeating the schedule.
- **Intermediate relation check:** For sql-38 Exercise 2, run Session A's count once more after Session B's `INSERT` but before its `COMMIT`: it still returns `1`, because the uncommitted row is invisible.
- **Clause check:** For sql-38 Exercise 2, Session A uses `SELECT COUNT(*) ... WHERE qty >= 20` twice and Session B uses one `INSERT ... VALUES (3, 30)` followed by `COMMIT`.
- **Alternative/trade-off:** For sql-38 Exercise 2, `SERIALIZABLE` also hides the phantom from Session A; under `READ COMMITTED`, `LOCK TABLE training.isolation_lab IN SHARE MODE` in Session A would instead make Session B's insert wait.
- **Edge case:** Insert `(3, 19)` instead: the row does not match `qty >= 20`, so both counts stay `1` at every isolation level.

## Exercise 3: Serialization failure under contention

Reset the two rows, then interleave these commands. Both transactions read the
same set before either writes it.

Session A:

```text
UPDATE training.isolation_lab SET qty = 10 WHERE id = 1;
UPDATE training.isolation_lab SET qty = 20 WHERE id = 2;
DELETE FROM training.isolation_lab WHERE id >= 3;
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(qty) FROM training.isolation_lab;
```

Session B:

```text
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(qty) FROM training.isolation_lab;
```

Session A, then Session B:

```text
-- Session A
UPDATE training.isolation_lab SET qty = qty + 1 WHERE id = 1;

-- Session B
UPDATE training.isolation_lab SET qty = qty + 1 WHERE id = 2;

-- Session A
COMMIT;

-- Session B
COMMIT;
```

Each transaction read a row that the other one changed, so the two form a
read/write dependency cycle. PostgreSQL lets Session A commit and then rejects
Session B's `COMMIT` with SQLSTATE `40001`. Real applications retry the entire
transaction, including its reads, not just the final statement.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 3, reset `training.isolation_lab` to `(1, 10)` and `(2, 20)`, then open two `SERIALIZABLE` transactions that both read `SUM(qty)` before Session A updates the row with `id = 1` and Session B updates the row with `id = 2`.
- **Expected result/shape:** For sql-38 Exercise 3, expected output: both sums are `30`; Session A's `COMMIT` succeeds and Session B's `COMMIT` fails with SQLSTATE `40001` (`could not serialize access due to read/write dependencies among transactions`), leaving committed rows `(1, 11)` and `(2, 20)`.
- **Independent verification:** For sql-38 Exercise 3, capture the error text and SQLSTATE (for example after `\set VERBOSITY verbose`), confirm the committed rows with `SELECT id, qty FROM training.isolation_lab ORDER BY id`, then rerun Session B's whole transaction from `BEGIN ISOLATION LEVEL SERIALIZABLE` and confirm the rows `(1, 11)` and `(2, 21)`.
- **Intermediate relation check:** For sql-38 Exercise 3, after both updates and before either commit, `SELECT id, qty FROM training.isolation_lab ORDER BY id` in each session shows only that session's own change.
- **Clause check:** For sql-38 Exercise 3, both sessions use `SELECT SUM(qty)` and one single-row `UPDATE`; the abort comes from the read/write dependency cycle, not from a query error.
- **Alternative/trade-off:** For sql-38 Exercise 3, running the same schedule at `REPEATABLE READ` lets both commits succeed and produces write skew: each transaction validated a sum that the other one changed.
- **Edge case:** If Session B updates the row with `id = 1` instead, its `UPDATE` waits for Session A and then fails with SQLSTATE `40001` (`could not serialize access due to concurrent update`) as soon as A commits.

## Cleanup and cautions

After both sessions have no open transaction, run:

```text
DROP TABLE IF EXISTS training.isolation_lab;
```

Do not leave terminals “idle in transaction.” Results depend on exact
interleaving, and the setup state must be reset between experiments.

## Exercise 4: Reuse and release a savepoint

`ROLLBACK TO` reverses later work but retains the named savepoint. `RELEASE`
then removes it explicitly before the outer transaction continues.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 4, use the temporary `isolation_solution` rows `(1, 10)` and `(2, 20)` inside the lesson transaction; set a savepoint, add `1` to `quantity` for `id = 2`, roll back to the savepoint, then release it.
- **Expected result/shape:** For sql-38 Exercise 4, expected output: `RELEASE SAVEPOINT` succeeds because `ROLLBACK TO SAVEPOINT` keeps the savepoint, and the final `SELECT` returns two rows ordered by `id` with columns `id` and `quantity`: `(1, 10)` and `(2, 20)`.
- **Independent verification:** For sql-38 Exercise 4, compare the row with `id = 2` before the savepoint and after the rollback (both `20`); in a scratch transaction, a second `RELEASE SAVEPOINT reusable_point` fails with SQLSTATE `3B001` (`savepoint "reusable_point" does not exist`), which proves the first `RELEASE` removed it.
- **Intermediate relation check:** For sql-38 Exercise 4, select `id, quantity` between the `UPDATE` and `ROLLBACK TO SAVEPOINT`: the row with `id = 2` shows `21`, then `20` after the rollback.
- **Clause check:** For sql-38 Exercise 4, the statements are `SAVEPOINT`, `UPDATE ... WHERE id = 2`, `ROLLBACK TO SAVEPOINT`, `RELEASE SAVEPOINT`, and a final `SELECT ... ORDER BY id`.
- **Alternative/trade-off:** For sql-38 Exercise 4, when the work after a savepoint succeeds, `RELEASE SAVEPOINT` alone keeps that work and only removes the marker.
- **Edge case:** Roll back to the same savepoint twice before releasing it: both `ROLLBACK TO SAVEPOINT reusable_point` statements succeed while the savepoint exists.

## Exercise 5: Transfer atomically

The solution locks/reads the debit account, rejects insufficient funds, and
updates both balances in one unit. A final SUM proves conservation of money.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 5, create the temporary `transfer_accounts` table with rows `(1, 100.00)` and `(2, 40.00)` and `CHECK (balance >= 0)`; move `25.00` from account 1 to account 2 after locking and checking the debit row.
- **Expected result/shape:** For sql-38 Exercise 5, expected output: one `conserved_total` row equal to `140.00`; the account rows become `(1, 75.00)` and `(2, 65.00)`.
- **Independent verification:** For sql-38 Exercise 5, list `account_id` and `balance` before and after the transfer and compare their sums; then attempt a `200.00` transfer after a savepoint, confirm the `insufficient balance` exception with SQLSTATE `P0001`, roll back to the savepoint, and confirm both balances are unchanged.
- **Intermediate relation check:** For sql-38 Exercise 5, in a scratch run that selects both balances between the two `UPDATE` statements, the total is temporarily `115.00`; no other session can observe that state before commit.
- **Clause check:** For sql-38 Exercise 5, the `DO` block uses `SELECT ... INTO ... FOR UPDATE`, an `IF` guard with `RAISE EXCEPTION`, and two single-row `UPDATE` statements; the check query uses `SUM(balance)`.
- **Alternative/trade-off:** For sql-38 Exercise 5, one `UPDATE ... SET balance = balance + CASE ... END WHERE account_id IN (1, 2)` also changes both rows atomically; the `CHECK (balance >= 0)` constraint would then reject an overdraft with SQLSTATE `23514` instead of the custom message.
- **Edge case:** Transfer exactly `100.00`: the debit balance becomes `0.00`, which both the guard and `CHECK (balance >= 0)` allow.

## Exercise 6: Recover from a constraint error

A PL/pgSQL exception block creates an internal subtransaction. It catches the
expected unique violation and demonstrates that the outer transaction can
still execute a query.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 6, insert a duplicate `id = 1` into the temporary `isolation_solution` table inside a protected PL/pgSQL block (or after a savepoint), so the unique violation with SQLSTATE `23505` is caught or rolled back to the savepoint.
- **Expected result/shape:** For sql-38 Exercise 6, expected output: a notice that the duplicate was rejected, then one `still_usable` row whose value is `2`, the number of rows in `isolation_solution`.
- **Independent verification:** For sql-38 Exercise 6, in a scratch transaction, repeat the duplicate insert without protection and confirm that the next statement fails with SQLSTATE `25P02` (`current transaction is aborted`); the savepoint recovery is what avoids that state.
- **Intermediate relation check:** For sql-38 Exercise 6, `SELECT id, quantity FROM isolation_solution ORDER BY id` after the block shows the two original rows and no duplicate.
- **Clause check:** For sql-38 Exercise 6, the `DO` block wraps one `INSERT` in a nested `BEGIN ... EXCEPTION WHEN unique_violation` block; the check query is `SELECT COUNT(*) AS still_usable FROM isolation_solution`.
- **Alternative/trade-off:** For sql-38 Exercise 6, `SAVEPOINT before_insert` followed by `ROLLBACK TO SAVEPOINT before_insert` gives the same recovery without PL/pgSQL, but an uncaught error stops a script run with `ON_ERROR_STOP`, so the `DO` block keeps the lesson file runnable.
- **Edge case:** A different error, such as a `CHECK` violation, is not caught by `WHEN unique_violation` and still aborts the transaction.

## Exercise 7: Choose isolation for read-only work

Several SELECT statements that must describe one consistent snapshot justify
`REPEATABLE READ`. If per-statement freshness is intended, `READ COMMITTED` may
be correct. “Read-only” does not decide the snapshot contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 7, consider a report that runs two statements over `training.isolation_lab`, a `COUNT(*)` and a `SUM(qty)`, while another session may commit changes between them.
- **Expected result/shape:** For sql-38 Exercise 7, expected output: a short written answer that chooses `REPEATABLE READ` (optionally `READ ONLY`) when both results must describe one snapshot, and `READ COMMITTED` when each statement may show the latest committed data.
- **Independent verification:** For sql-38 Exercise 7, test the claim with the Exercise 2 schedule: under `READ COMMITTED`, a `SUM(qty)` run after Session B commits includes the new row that the earlier `COUNT(*)` did not count; under `REPEATABLE READ`, both values describe the first snapshot.
- **Intermediate relation check:** For sql-38 Exercise 7, write down which snapshot each statement of the report uses before choosing a level.
- **Clause check:** For sql-38 Exercise 7, the answer is a written decision; its evidence is the Exercise 2 schedule rerun with a `COUNT(*)` and a `SUM(qty)` in the same transaction.
- **Alternative/trade-off:** For sql-38 Exercise 7, `BEGIN ISOLATION LEVEL SERIALIZABLE, READ ONLY, DEFERRABLE` waits for a safe snapshot and then can never fail with a serialization error, at the cost of a possible start-up delay.
- **Edge case:** A report made of one statement already reads one snapshot under `READ COMMITTED`; the isolation choice matters only when several statements must agree.
