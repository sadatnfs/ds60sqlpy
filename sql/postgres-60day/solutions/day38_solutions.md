# Day 38 — Solutions: Transactions and Isolation


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day38_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day38_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are MVCC, Isolation level, Serialization failure. Its worked-model focus is:
Open two disposable sessions and write down each statement before running it. Under READ COMMITTED, have session A read a count, session B commit a matching insert, and session A read again. Repeat at REPEATABLE READ and explain the snapshot difference; clean up the shared disposable table afterward.

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
INSERT INTO savepoint_demo VALUES (1, 10);

SAVEPOINT before_change;
UPDATE savepoint_demo
SET qty = qty + 100
WHERE id = 1;
ROLLBACK TO SAVEPOINT before_change;

SELECT id, qty
FROM savepoint_demo;

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

## Exercise 1 — Non-repeatable read under `READ COMMITTED`

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

- **Inputs/evidence:** For sql-38 Exercise 1, read from `isolation_lab`. Build the answer toward `qty`; keep `qty` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-38 Exercise 1, expected output: one row per `qty`. The final columns are `qty`.
- **Independent verification:** For sql-38 Exercise 1, run an anti-check that counts rows where NOT ((id = 1)); require unique `qty` where the expected grain is one row per key and confirm the projected `qty` against `isolation_lab`. Add one row for which `(id = 1)` is true and one for which it is false; verify only the matching `qty` value is returned.
- **Intermediate relation check:** For sql-38 Exercise 1, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-38 Exercise 1, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `isolation_lab`, preserve one row per `qty`, and finish with `qty`.
- **Alternative/trade-off:** For sql-38 Exercise 1, the chosen form is justified by this lesson-specific rationale: Session A: While A remains open, Session B: Back in Session A: The two reads in A return different committed versions because `READ COMMITTED` takes a new statement snapshot. Evaluate another form against the concrete expected result (one row per `qty`) and the verification above.
- **Edge case:** Add one row for which `(id = 1)` is true and one for which it is false; verify only the matching `qty` value is returned.

## Exercise 2 — Phantom rows between two counts

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

- **Inputs/evidence:** For sql-38 Exercise 2, read the target keys from `training.isolation_lab` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-38 Exercise 2, expected output: the command tag and an independently counted set of affected `affected_row_count` values. The final columns are `affected_row_count`, and `command_tag`.
- **Independent verification:** For sql-38 Exercise 2, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `training.isolation_lab` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.
- **Intermediate relation check:** For sql-38 Exercise 2, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `training.isolation_lab` again and prove rollback or idempotent retry.
- **Clause check:** For sql-38 Exercise 2, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `training.isolation_lab`, preserve exactly one summary row, and finish with `affected_row_count`, and `command_tag`.
- **Alternative/trade-off:** For sql-38 Exercise 2, the chosen form is justified by this lesson-specific rationale: Reset, then start Session A: Session B inserts a new qualifying row: Back in Session A: The new qualifying row is a phantom. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `affected_row_count` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.

## Exercise 3 — Serialization failure under contention

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

PostgreSQL must abort one transaction with SQLSTATE `40001` to prevent the
read/write dependency cycle. Real applications retry the entire transaction,
not just the final statement.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 3, read from `training.isolation_lab`. Build the answer toward `serializable`; keep `serializable` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-38 Exercise 3, expected output: one row per `serializable`. The final columns are `serializable`.
- **Independent verification:** For sql-38 Exercise 3, run an anti-check that counts rows where NOT ((id = 1) OR (id = 2) OR (id >= 3)); require unique `serializable` where the expected grain is one row per key and confirm the projected `serializable` against `training.isolation_lab`. Add one row for which `(id = 1) OR (id = 2) OR (id >= 3)` is true and one for which it is false; verify only the matching `serializable` value is returned.
- **Intermediate relation check:** For sql-38 Exercise 3, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-38 Exercise 3, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `training.isolation_lab`, preserve one row per `serializable`, and finish with `serializable`.
- **Alternative/trade-off:** For sql-38 Exercise 3, the chosen form is justified by this lesson-specific rationale: Reset the two rows, then interleave these commands. Evaluate another form against the concrete expected result (one row per `serializable`) and the verification above.
- **Edge case:** Add one row for which `(id = 1) OR (id = 2) OR (id >= 3)` is true and one for which it is false; verify only the matching `serializable` value is returned.

## Cleanup and cautions

After both sessions have no open transaction, run:

```text
DROP TABLE IF EXISTS training.isolation_lab;
```

Do not leave terminals “idle in transaction.” Results depend on exact
interleaving, and the setup state must be reset between experiments.

## Exercise 4 — Reuse and release a savepoint

`ROLLBACK TO` reverses later work but retains the named savepoint. `RELEASE`
then removes it explicitly before the outer transaction continues.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 4, read from `isolation_solution`. Build the answer toward `release`; keep `release` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-38 Exercise 4, expected output: one row per `release`. The final columns are `release`. The final order is `id`.
- **Independent verification:** For sql-38 Exercise 4, run an anti-check that counts rows where NOT ((id = 2)); require unique `release` where the expected grain is one row per key and confirm the projected `release` against `isolation_solution`. Add one row for which `(id = 2)` is true and one for which it is false; verify only the matching `release` value is returned.
- **Intermediate relation check:** For sql-38 Exercise 4, inspect the source keys that survive `WHERE`; then check `id` before applying the row cap.
- **Clause check:** For sql-38 Exercise 4, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `isolation_solution`, preserve one row per `release`, and finish with `release` ordered by `id`.
- **Alternative/trade-off:** For sql-38 Exercise 4, the chosen form is justified by this lesson-specific rationale: `ROLLBACK TO` reverses later work but retains the named savepoint. Evaluate another form against the concrete expected result (one row per `release`) and the verification above.
- **Edge case:** Add one row for which `(id = 2)` is true and one for which it is false; verify only the matching `release` value is returned.

## Exercise 5 — Transfer atomically

The solution locks/reads the debit account, rejects insufficient funds, and
updates both balances in one unit. A final SUM proves conservation of money.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 5, read from `transfer_accounts`. Build the answer toward `available`; keep `available` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-38 Exercise 5, expected output: one row per `available`. The final columns are `available`.
- **Independent verification:** For sql-38 Exercise 5, run an anti-check that counts rows where NOT ((account_id = 1 FOR UPDATE) OR (account_id = 1) OR (account_id = 2)); require unique `available` where the expected grain is one row per key and confirm the projected `available` against `transfer_accounts`. Add one row for which `(account_id = 1 FOR UPDATE) OR (account_id = 1) OR (account_id = 2)` is true and one for which it is false; verify only the matching `available` value is returned.
- **Intermediate relation check:** For sql-38 Exercise 5, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-38 Exercise 5, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `transfer_accounts`, preserve one row per `available`, and finish with `available`.
- **Alternative/trade-off:** For sql-38 Exercise 5, the chosen form is justified by this lesson-specific rationale: The solution locks/reads the debit account, rejects insufficient funds, and updates both balances in one unit. Evaluate another form against the concrete expected result (one row per `available`) and the verification above.
- **Edge case:** Add one row for which `(account_id = 1 FOR UPDATE) OR (account_id = 1) OR (account_id = 2)` is true and one for which it is false; verify only the matching `available` value is returned.

## Exercise 6 — Recover from a constraint error

A PL/pgSQL exception block creates an internal subtransaction. It catches the
expected unique violation and demonstrates that the outer transaction can
still execute a query.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 6, read from `isolation_solution`. Build the answer toward `still_usable`; keep `still_usable` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-38 Exercise 6, expected output: one row per `still_usable`. The final columns are `still_usable`.
- **Independent verification:** For sql-38 Exercise 6, reselect the returned keys directly from the source; require unique `still_usable` where the expected grain is one row per key and confirm the projected `still_usable` against `isolation_solution`. Add duplicate source candidates for `still_usable`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-38 Exercise 6, select `still_usable` from `isolation_solution` before adding derived columns.
- **Clause check:** For sql-38 Exercise 6, the solution actually uses `WITH`, `FROM`, and `SELECT`. Read only those operations: begin at `isolation_solution`, preserve one row per `still_usable`, and finish with `still_usable`.
- **Alternative/trade-off:** For sql-38 Exercise 6, the chosen form is justified by this lesson-specific rationale: A PL/pgSQL exception block creates an internal subtransaction. Evaluate another form against the concrete expected result (one row per `still_usable`) and the verification above.
- **Edge case:** Add duplicate source candidates for `still_usable`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Exercise 7 — Choose isolation for read-only work

Several SELECT statements that must describe one consistent snapshot justify
`REPEATABLE READ`. If per-statement freshness is intended, `READ COMMITTED` may
be correct. “Read-only” does not decide the snapshot contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-38 Exercise 7, use two labeled terminals and only `txn_demo`, `isolation_solution`, and `transfer_accounts`. Write the statement order, expected wait/SQLSTATE, and cleanup step before opening either transaction.
- **Expected result/shape:** For sql-38 Exercise 7, expected output: a statement-by-statement Session A/Session B transcript followed by the committed fixture state and cleanup evidence. The final columns are `session`, `statement_number`, `outcome`, and `sqlstate`.
- **Independent verification:** For sql-38 Exercise 7, compare every observed value, wait, and SQLSTATE with the written schedule; query `txn_demo`, `isolation_solution`, and `transfer_accounts` after each commit/rollback and finish with both sessions idle and the fixture reset. Repeat the exact interleaving after cleanup and confirm the same wait, SQLSTATE, and committed final rows.
- **Intermediate relation check:** For sql-38 Exercise 7, compare every observed value, wait, and SQLSTATE with the written schedule; query `txn_demo`, `isolation_solution`, and `transfer_accounts` after each commit/rollback and finish with both sessions idle and the fixture reset.
- **Clause check:** For sql-38 Exercise 7, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `txn_demo`, `isolation_solution`, and `transfer_accounts` or label it as proposed policy.
- **Alternative/trade-off:** For sql-38 Exercise 7, the chosen form is justified by this lesson-specific rationale: Several SELECT statements that must describe one consistent snapshot justify `REPEATABLE READ`. Evaluate another form against the concrete expected result (a statement-by-statement Session A/Session B transcript followed by the committed fixture state and cleanup evidence) and the verification above.
- **Edge case:** Repeat the exact interleaving after cleanup and confirm the same wait, SQLSTATE, and committed final rows.
