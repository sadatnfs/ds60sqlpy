# Day 53 Solutions — SCD Type 2 and Temporal Fact Keys


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day53_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day53_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are SCD Type 2, Business key, Validity interval. Its worked-model focus is:
For one changed customer, locate exactly one current row, set its validto to the day before the new version, and insert the successor at CURRENTDATE. Then as-of join a fact date using inclusive bounds and verify it resolves to one surrogate key—not zero and not two.

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

Run [`day52_solutions.sql`](day52_solutions.sql) first in the same database.
Day 53 reads that committed `dwh` state but wraps its own changes in a
transaction and rolls them back. The full answer is
[`day53_solutions.sql`](day53_solutions.sql).

## Exercise 1 — Resolve dimension versions by fact date

The exercise requires the customer and product surrogate keys whose validity
intervals contain each source order date.

```sql
BEGIN;
SET search_path TO dwh, training, public;

CREATE TEMP TABLE fact_sales_temporal_solution AS
SELECT o.order_id,
       oi.order_item_id,
       dd.date_key,
       dc.customer_sk,
       dp.product_sk,
       oi.quantity,
       oi.unit_price,
       oi.discount,
       oi.unit_price * oi.quantity * (1 - oi.discount) AS amount
FROM training.orders o
JOIN training.order_items oi USING (order_id)
JOIN dim_date dd ON dd.date_actual = o.order_date::date
JOIN dim_customer dc
  ON dc.customer_id = o.customer_id
 AND o.order_date::date >= dc.valid_from
 AND o.order_date::date <= COALESCE(dc.valid_to, 'infinity'::date)
JOIN dim_product dp
  ON dp.product_id = oi.product_id
 AND o.order_date::date >= dp.valid_from
 AND o.order_date::date <= COALESCE(dp.valid_to, 'infinity'::date);

SELECT (SELECT COUNT(*) FROM fact_sales_temporal_solution) AS mapped_fact_rows,
       (SELECT COUNT(*) FROM training.order_items) AS source_item_rows;

ROLLBACK;
```

Expected result: `mapped_fact_rows` equals `source_item_rows`. A lower count
means a date or dimension-version gap; a higher count means overlapping
validity ranges caused one fact to match more than one version.

The executable solution also stages a deterministic customer change effective
30 days ago, closes the previous current row at `effective_date - 1`, inserts a
new current row, and then performs this temporal mapping.

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

## Exercise 2 — Audit columns

Inside the Day 53 transaction, the answer adds:

```sql
BEGIN;
SET search_path TO dwh, training, public;

ALTER TABLE dim_customer
  ADD COLUMN updated_by text NOT NULL DEFAULT CURRENT_USER,
  ADD COLUMN updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE dim_product
  ADD COLUMN updated_by text NOT NULL DEFAULT CURRENT_USER,
  ADD COLUMN updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP;

ROLLBACK;
```

The SCD close and insert explicitly stamp `updated_by = 'day53_solution'`.
Because the executable answer rolls back, these columns do not remain after the
lesson.

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

## Reasoning, state, and pitfalls

- A Type 2 change is two operations in one transaction: close the current
  version, then insert the replacement.
- `valid_from <= fact_date <= COALESCE(valid_to, infinity)` matches the
  course's inclusive-date convention.
- Enforce one current row per business key in a production warehouse, commonly
  with a partial unique index on the business key where `is_current`.
- Audit defaults cover inserts, not meaningful update actors; set audit values
  explicitly when closing versions.
- Do not run this before Day 52; the executable file raises a clear exception if
  `dwh.dim_customer` is absent.

## Exercise 3 — Diagnose same-day changes

Inclusive DATE ranges cannot order two changes on one day without overlap or an
invalid close-before-open interval. The answer surfaces invalid ranges.

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

## Exercise 4 — Detect overlapping versions

The self-join compares each customer-version pair once and applies the inclusive
overlap condition. Any row can map one fact date to multiple surrogates.

### Reasoning and verification

- **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
- **Independent verification:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
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

## Exercise 5 — Gate unchanged reruns

`IS DISTINCT FROM` compares nullable attributes safely. Only real source/current
differences should close and insert a version; zero differences prove idempotency.

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

## Exercise 6 — Define a same-day policy

Half-open `tstzrange` examples show how effective timestamps can order changes.
They require trustworthy source effective time or sequence, not load-time guesswork.

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
