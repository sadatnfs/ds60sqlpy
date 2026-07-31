# Day 43 Solutions — Logical Backup and Recovery


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day43_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day43_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Logical backup, Staging table, Idempotent merge. Its worked-model focus is:
Use \copy (SELECT ... WHERE ...) TO ... from a path owned by the learner, import into a staging table, and compare count, keys, types, and sample rows. Only then merge inside BEGIN/ROLLBACK with an explicit email conflict policy.

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

This day distinguishes client-side export from database recovery logic. The
answer uses `COPY ... TO STDOUT` so it works through the current connection and
models a restore with a temporary staging table. See
[`day43_solutions.sql`](day43_solutions.sql).

## Exercise 1 — Export and stage a subset

In interactive `psql`, `\copy` writes on the client machine:

```text
\copy (SELECT * FROM training.customers WHERE country = 'US' ORDER BY customer_id) TO 'customers_us.csv' WITH (FORMAT csv, HEADER true)
```

Replace that filename with a path the learner owns. Path syntax, directory
creation, and write permission are environment-specific on Windows, macOS, and
Linux; the repository cannot choose or create that destination safely.

The executable solution uses SQL-standard server output instead:

```sql
BEGIN;
SET search_path TO training, public;

COPY (
  SELECT customer_id, full_name, email, country, created_at, segment, attributes
  FROM customers
  WHERE country = 'US'
  ORDER BY customer_id
) TO STDOUT WITH (FORMAT csv, HEADER true);

CREATE TEMP TABLE customers_restore_stage AS
SELECT full_name, email, country, created_at, segment, attributes
FROM customers
WHERE country = 'US';

SELECT COUNT(*) AS staged_rows FROM customers_restore_stage;
ROLLBACK;
```

Expected shape: CSV rows are streamed to the client, and `staged_rows` equals
the number of US customers. A real import would create an explicit staging
table and run `\copy customers_restore_stage FROM ...`.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 1, read from `training.customers`. Build the answer toward `staged_rows`, and `customers_restore_stage`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-43 Exercise 1, expected output: CSV rows are streamed to the client, and `staged_rows` equals the number of US customers. A real import would create an explicit staging table and run `\copy customers_restore_stage FROM. The final columns are `staged_rows`, and `customers_restore_stage`.
- **Independent verification:** For sql-43 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `staged_rows`, and `customers_restore_stage` against `training.customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-43 Exercise 1, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-43 Exercise 1, the solution actually uses `WITH`, `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `training.customers`, preserve one row per `customer_id`, and finish with `staged_rows`, and `customers_restore_stage`.
- **Alternative/trade-off:** For sql-43 Exercise 1, the chosen form is justified by this lesson-specific rationale: In interactive `psql`, `\copy` writes on the client machine: Replace that filename with a path the learner owns. Evaluate another form against the concrete expected result (CSV rows are streamed to the client, and `staged_rows` equals the number of US customers. A real import would create an explicit staging table and run `\copy customers_restore_stage FROM) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Exercise 2 — Idempotent restore with conflict handling

Email is the current schema's unique business key for this exercise.

```sql
BEGIN;
SET search_path TO training, public;

CREATE TEMP TABLE customers_restore_stage AS
SELECT full_name, email, country, created_at, segment, attributes
FROM customers
WHERE country = 'US';

UPDATE customers_restore_stage
SET full_name = full_name || ' [restored]'
WHERE email = 'customer1@example.com';

INSERT INTO customers(full_name, email, country, created_at, segment, attributes)
SELECT full_name, email, country, created_at, segment, attributes
FROM customers_restore_stage
ON CONFLICT (email) DO UPDATE
SET full_name = EXCLUDED.full_name,
    country = EXCLUDED.country,
    segment = EXCLUDED.segment,
    attributes = EXCLUDED.attributes;

ROLLBACK;
```

The transaction proves both insert and update paths while leaving the course
data unchanged.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 2, use `customers`, and `customers_restore_stage` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-43 Exercise 2, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `full_name`, `email`, `country`, `created_at`, `segment`, and `attributes`.
- **Independent verification:** For sql-43 Exercise 2, restore into an isolated target and reconcile `customers`, and `customers_restore_stage` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-43 Exercise 2, restore into an isolated target and reconcile `customers`, and `customers_restore_stage` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-43 Exercise 2, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `customers`, and `customers_restore_stage`, preserve one row per `country`, and `segment`, and finish with `full_name`, `email`, `country`, `created_at`, `segment`, and `attributes`.
- **Alternative/trade-off:** For sql-43 Exercise 2, the chosen form is justified by this lesson-specific rationale: Email is the current schema's unique business key for this exercise. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Reasoning, safety, and pitfalls

- `COPY ... TO '/path'` reads or writes on the database server and usually needs
  elevated privileges. `\copy` reads or writes on the `psql` client.
- Restore into staging first; validate counts, keys, types, and representative
  rows before merging into the base table.
- `ON CONFLICT` is idempotent only when the conflict key represents the intended
  entity and update policy.
- Logical export is not point-in-time recovery. Production PITR requires base
  backups plus WAL archiving, which is outside this SQL-only exercise.

## Exercise 3 — Choose COPY or backslash-copy

Server-side `COPY` accesses the database server's filesystem. psql `\copy`
streams through the client, which is usually the appropriate learner-machine
workflow.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 3, complete the explain server-side copy versus client-side copy written analysis and support its claims with read-only evidence from `customers`, `customers_stg`, and `customers_restore_stage`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-43 Exercise 3, expected output: a completed the explain server-side copy versus client-side copy written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `copy`.
- **Independent verification:** For sql-43 Exercise 3, check the explain server-side copy versus client-side copy written analysis against `copy`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-43 Exercise 3, check the explain server-side copy versus client-side copy written analysis against `copy`.
- **Clause check:** For sql-43 Exercise 3, the solution actually uses `FROM`. Read only those operations: begin at `customers`, `customers_stg`, and `customers_restore_stage`, preserve one row per `customer_id`, and finish with `copy`.
- **Alternative/trade-off:** For sql-43 Exercise 3, the chosen form is justified by this lesson-specific rationale: Server-side `COPY` accesses the database server's filesystem. Evaluate another form against the concrete expected result (a completed the explain server-side copy versus client-side copy written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 4 — Build a manifest

The manifest records table, count, key range, and observation time. Production
automation should also hash the exported file outside SQL.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 4, read from `customers`. Build the answer toward `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-43 Exercise 4, expected output: one row per `customer_id`. The final columns are `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at`.
- **Independent verification:** For sql-43 Exercise 4, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-43 Exercise 4, select `customer_id` from `customers` before adding derived columns.
- **Clause check:** For sql-43 Exercise 4, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `table_name`, `row_count`, `min_key`, `max_key`, and `observed_at`.
- **Alternative/trade-off:** For sql-43 Exercise 4, the chosen form is justified by this lesson-specific rationale: The manifest records table, count, key range, and observation time. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Exercise 5 — Deduplicate deterministically

`ROW_NUMBER` partitions by normalized email and orders by an explicit newest/
tie-break policy. Upsert never receives arbitrary duplicate winners.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 5, read from `customers_restore_stage`. Build the answer toward `full_name`, `email`, and `country`; keep `country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-43 Exercise 5, expected output: one row per `country`. The final columns are `full_name`, `email`, and `country`. The final order is `email`.
- **Independent verification:** For sql-43 Exercise 5, run an anti-check that counts rows where NOT ((winner_rank = 1)); require unique `country` where the expected grain is one row per key and confirm the projected `full_name`, `email`, and `country` against `customers_restore_stage`. Add duplicate source candidates for `country`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-43 Exercise 5, run `staged_duplicates` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
- **Clause check:** For sql-43 Exercise 5, the solution actually uses `WITH`, `FROM`, `WHERE`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers_restore_stage`, preserve one row per `country`, and finish with `full_name`, `email`, and `country` ordered by `email`.
- **Alternative/trade-off:** For sql-43 Exercise 5, the chosen form is justified by this lesson-specific rationale: `ROW_NUMBER` partitions by normalized email and orders by an explicit newest/ tie-break policy. Evaluate another form against the concrete expected result (one row per `country`) and the verification above.
- **Edge case:** Add duplicate source candidates for `country`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Exercise 6 — Compare NULL safely

`IS DISTINCT FROM` treats two NULLs as equal and one NULL as different. It
therefore reports real source/restore differences without UNKNOWN results.

### Reasoning and verification

- **Inputs/evidence:** For sql-43 Exercise 6, use `customers_restore_stage`, `customers`, `c.country`, and `c.segment` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-43 Exercise 6, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `email`, `staged_name`, and `restored_name`. The final order is `s.email`.
- **Independent verification:** For sql-43 Exercise 6, restore into an isolated target and reconcile `customers_restore_stage`, `customers`, `c.country`, and `c.segment` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-43 Exercise 6, start with the first relation in `customers_restore_stage`, `customers`, `c.country`, and `c.segment`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-43 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers_restore_stage`, `customers`, `c.country`, and `c.segment`, preserve one row per `customer_id`, and finish with `email`, `staged_name`, and `restored_name` ordered by `s.email`.
- **Alternative/trade-off:** For sql-43 Exercise 6, the chosen form is justified by this lesson-specific rationale: `IS DISTINCT FROM` treats two NULLs as equal and one NULL as different. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
