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

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** An alternative physical/object design is valid only if catalog inspection and valid/invalid behavior prove the same invariant.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 5 — Transfer atomically

The solution locks/reads the debit account, rejects insufficient funds, and
updates both balances in one unit. A final SUM proves conservation of money.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 6 — Recover from a constraint error

A PL/pgSQL exception block creates an internal subtransaction. It catches the
expected unique violation and demonstrates that the outer transaction can
still execute a query.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** An alternative physical/object design is valid only if catalog inspection and valid/invalid behavior prove the same invariant.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 7 — Choose isolation for read-only work

Several SELECT statements that must describe one consistent snapshot justify
`REPEATABLE READ`. If per-statement freshness is intended, `READ COMMITTED` may
be correct. “Read-only” does not decide the snapshot contract.

### Reasoning and verification

- **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.
