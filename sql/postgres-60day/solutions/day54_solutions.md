# Day 54 Solutions — Warehouse Aggregates and Refresh Procedure


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day54_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day54_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Aggregate table, Idempotent refresh, Late-arriving fact. Its worked-model focus is:
For one target year/month, delete category, customer, and product aggregate rows, rebuild each independently from facts, and commit or roll back the whole unit together. Reconcile each table's period revenue with a fact-only control before considering the refresh successful.

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
Day 54 creates and tests aggregate objects inside a transaction, then rolls
everything back. The complete runnable answer is
[`day54_solutions.sql`](day54_solutions.sql).

## Exercise 1 — `agg_sales_product_month`

The answer uses this grain and schema:

```sql
BEGIN;
SET search_path TO dwh, training, public;

CREATE TABLE agg_sales_product_month (
  year int NOT NULL,
  month int NOT NULL,
  product_sk int NOT NULL REFERENCES dim_product(product_sk),
  revenue numeric(14,2) NOT NULL,
  units bigint NOT NULL,
  orders bigint NOT NULL,
  PRIMARY KEY (year, month, product_sk)
);

INSERT INTO agg_sales_product_month(
  year, month, product_sk, revenue, units, orders
)
SELECT dd.year,
       dd.month,
       fs.product_sk,
       ROUND(SUM(fs.amount), 2),
       SUM(fs.quantity),
       COUNT(DISTINCT fs.order_id)
FROM fact_sales fs
JOIN dim_date dd USING (date_key)
GROUP BY dd.year, dd.month, fs.product_sk;

WITH aggregate_total AS (
  SELECT year, month, SUM(revenue) AS revenue
  FROM agg_sales_product_month
  GROUP BY year, month
), fact_total AS (
  SELECT dd.year, dd.month, ROUND(SUM(fs.amount), 2) AS revenue
  FROM fact_sales fs
  JOIN dim_date dd USING (date_key)
  GROUP BY dd.year, dd.month
)
SELECT a.year,
       a.month,
       a.revenue AS aggregate_revenue,
       f.revenue AS fact_revenue,
       a.revenue - f.revenue AS difference
FROM aggregate_total a
JOIN fact_total f USING (year, month)
ORDER BY a.year, a.month;

ROLLBACK;
```

The two sides are aggregated independently before joining, preventing join
fanout. Expected `difference` is zero for every built month.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 1, read from `dim_product`, `agg_sales_product_month`, `fact_sales`, and `dim_date`. Build the answer toward `year`, `month`, and `product_sk`; keep `year`, `month`, and `product_sk` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-54 Exercise 1, expected output: one row per `year`, `month`, and `product_sk`. The final columns are `year`, `month`, and `product_sk`. The final order is `a.year, a.month`.
- **Independent verification:** For sql-54 Exercise 1, independently aggregate `dim_product`, `agg_sales_product_month`, `fact_sales`, and `dim_date` by `year`, `month`, and `product_sk`; require one output row for every distinct `year`, `month`, and `product_sk` tuple and compare `product_sk` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `year`, and `month` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-54 Exercise 1, run `aggregate_total`, and `fact_total` one at a time. Record each CTE's row count and `year`, `month`, and `product_sk` uniqueness before the next stage uses it.
- **Clause check:** For sql-54 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `dim_product`, `agg_sales_product_month`, `fact_sales`, and `dim_date`, preserve one row per `year`, `month`, and `product_sk`, and finish with `year`, `month`, and `product_sk` ordered by `a.year, a.month`.
- **Alternative/trade-off:** For sql-54 Exercise 1, the chosen form is justified by this lesson-specific rationale: The answer uses this grain and schema: The two sides are aggregated independently before joining, preventing join fanout. Evaluate another form against the concrete expected result (one row per `year`, `month`, and `product_sk`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `year`, and `month` tuple and verify the new tuple appears exactly once.

## Exercise 2 — Refresh all aggregates for `(year, month)`

The executable solution creates:

```text
dwh.refresh_sales_aggregates_solution(p_year int, p_month int)
```

Within one procedure call it:

1. deletes the target month from category, customer, and product aggregates;
2. inserts category revenue and units;
3. inserts customer revenue and distinct orders;
4. inserts product revenue, units, and distinct orders.

The delete-then-insert design is idempotent for a target period. The answer
discovers the latest fact month and calls the procedure for that month, then
reconciles product aggregate revenue with `fact_sales`.

To inspect the result after running the canonical file, remember that it ends
with `ROLLBACK`; the aggregate objects intentionally will not persist.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 2, read from `agg_sales_category_month`, `agg_sales_customer_month`, `agg_sales_product_month`, `fact_sales`, and `dim_date`. Build the answer toward `year`, `month`, and `category`; keep `year`, `month`, and `product_sk` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-54 Exercise 2, expected output: one row per `year`, `month`, and `product_sk`. The final columns are `year`, `month`, and `category`. The final order is `dd.year DESC, dd.month DESC`.
- **Independent verification:** For sql-54 Exercise 2, assert no more than 1 rows, no duplicate `year`, `month`, and `product_sk`, and no adjacent pair that violates `dd.year DESC, dd.month DESC`. Rejoin the returned keys to `agg_sales_category_month`, `agg_sales_customer_month`, `agg_sales_product_month`, `fact_sales`, and `dim_date` to confirm `year`, `month`, and `category` came from the same source rows. Run with 1 minus one and 1 plus one eligible rows; require the output cap of 1 while retaining `dd.year DESC, dd.month DESC`.
- **Intermediate relation check:** For sql-54 Exercise 2, run `aggregate_total`, and `fact_total` one at a time. Record each CTE's row count and `year`, `month`, and `product_sk` uniqueness before the next stage uses it.
- **Clause check:** For sql-54 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `agg_sales_category_month`, `agg_sales_customer_month`, `agg_sales_product_month`, `fact_sales`, and `dim_date`, preserve one row per `year`, `month`, and `product_sk`, and finish with `year`, `month`, and `category` ordered by `dd.year DESC, dd.month DESC`.
- **Alternative/trade-off:** For sql-54 Exercise 2, the chosen form is justified by this lesson-specific rationale: The executable solution creates: Within one procedure call it: 1. Evaluate another form against the concrete expected result (one row per `year`, `month`, and `product_sk`) and the verification above.
- **Edge case:** Run with 1 minus one and 1 plus one eligible rows; require the output cap of 1 while retaining `dd.year DESC, dd.month DESC`.

## Required Days 52–54 sequence

```text
psql -X -v ON_ERROR_STOP=1 -d course -f day52_solutions.sql
psql -X -v ON_ERROR_STOP=1 -d course -f day53_solutions.sql
psql -X -v ON_ERROR_STOP=1 -d course -f day54_solutions.sql
```

Day 52 persists course-owned warehouse state. Days 53 and 54 prove their
solutions and roll back. Day 54 does not require Day 53 changes to persist.

## Reasoning, state, and pitfalls

- State the aggregate grain in the primary key; otherwise duplicate loads can
  silently inflate reports.
- Delete and rebuild all related aggregates in one transaction so readers do
  not observe mismatched periods.
- Reconcile totals after every refresh and treat nonzero differences as a load
  failure.
- The compact seed does not justify aggregate tables for performance; this is a
  warehouse-design exercise.
- Reconcile independently aggregated sides; joining aggregates to detail rows
  before summing can fan out both measures.

## Exercise 3 — Account for late facts

The period inventory identifies every loaded month. A late fact requires
refreshing its own affected period, not merely the newest month.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 3, read from `fact_sales`, and `dim_date`. Build the answer toward `year`, `month`, `fact_rows`, and `latest_fact_date`; keep `year`, and `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-54 Exercise 3, expected output: one row per `year`, and `month`. The final columns are `year`, `month`, `fact_rows`, and `latest_fact_date`. The final order is `dd.year DESC, dd.month DESC`.
- **Independent verification:** For sql-54 Exercise 3, independently aggregate `fact_sales`, and `dim_date` by `year`, and `month`; require one output row for every distinct `year`, and `month` tuple and compare `fact_rows` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `fact_rows` for the existing `year`, and `month` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-54 Exercise 3, start with the first relation in `fact_sales`, and `dim_date`; after each join, record total rows and distinct `year`, and `month` so the exact fanout or loss is visible.
- **Clause check:** For sql-54 Exercise 3, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `fact_sales`, and `dim_date`, preserve one row per `year`, and `month`, and finish with `year`, `month`, `fact_rows`, and `latest_fact_date` ordered by `dd.year DESC, dd.month DESC`.
- **Alternative/trade-off:** For sql-54 Exercise 3, the chosen form is justified by this lesson-specific rationale: The period inventory identifies every loaded month. Evaluate another form against the concrete expected result (one row per `year`, and `month`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `fact_rows` for the existing `year`, and `month` tuple and verify the new tuple appears exactly once.

## Exercise 4 — Refresh atomically

Delete and all aggregate inserts run in one transaction through the procedure.
Failure rolls back the whole period instead of leaving partial tables.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 4, read the target keys from `agg_sales_category_month` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-54 Exercise 4, expected output: the command tag and an independently counted set of affected `year`, and `month` values. The final columns are `year`, `month`, `category_rows`, and `revenue`. The final order is `year DESC, month DESC`.
- **Independent verification:** For sql-54 Exercise 4, materialize the intended `year`, and `month` target set first; require the command tag/`RETURNING` set to match it, then query `agg_sales_category_month` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `year`, and `month` values in both cases.
- **Intermediate relation check:** For sql-54 Exercise 4, materialize the intended `year`, and `month` target set first; require the command tag/`RETURNING` set to match it, then query `agg_sales_category_month` again and prove rollback or idempotent retry.
- **Clause check:** For sql-54 Exercise 4, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `agg_sales_category_month`, preserve one row per `year`, and `month`, and finish with `year`, `month`, `category_rows`, and `revenue` ordered by `year DESC, month DESC`.
- **Alternative/trade-off:** For sql-54 Exercise 4, the chosen form is justified by this lesson-specific rationale: Delete and all aggregate inserts run in one transaction through the procedure. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `year`, and `month` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `year`, and `month` values in both cases.

## Exercise 5 — Make reconciliation NULL-safe

FULL JOIN preserves a period missing on either side, and coalesced arithmetic
turns that absence into a visible nonzero difference.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 5, read from `agg_sales_category_month`, `fact_sales`, `dim_date`, and `f.revenue`. Build the answer toward `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`; keep `year`, and `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-54 Exercise 5, expected output: one row per `year`, and `month`. The final columns are `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`. The final order is `year, month`.
- **Independent verification:** For sql-54 Exercise 5, project `year`, and `month` plus the raw source columns from `agg_sales_category_month`, `fact_sales`, `dim_date`, and `f.revenue` at each join stage; record row count and distinct `year`, and `month`, then assert the final `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference` values match those staged rows without unintended fanout or loss. Repeat with `NULL` in `year`, and `month` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-54 Exercise 5, run `aggregate_total`, and `fact_total` one at a time. Record each CTE's row count and `year`, and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-54 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `agg_sales_category_month`, `fact_sales`, `dim_date`, and `f.revenue`, preserve one row per `year`, and `month`, and finish with `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference` ordered by `year, month`.
- **Alternative/trade-off:** For sql-54 Exercise 5, the chosen form is justified by this lesson-specific rationale: FULL JOIN preserves a period missing on either side, and coalesced arithmetic turns that absence into a visible nonzero difference. Evaluate another form against the concrete expected result (one row per `year`, and `month`) and the verification above.
- **Edge case:** Repeat with `NULL` in `year`, and `month` and state whether the row is kept, rejected, or classified.

## Exercise 6 — Prove idempotency

The answer snapshots category aggregates, reruns the same latest period, and
uses two-way `EXCEPT`. Both difference sets must be empty.

### Reasoning and verification

- **Inputs/evidence:** For sql-54 Exercise 6, read from `agg_sales_category_month`, `fact_sales`, `dim_date`, and `aggregate_snapshot_before`. Build the answer toward `except`; keep `except` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-54 Exercise 6, expected output: at most one row keyed by `except`. The final columns are `except`. The final order is `dd.year DESC, dd.month DESC`.
- **Independent verification:** For sql-54 Exercise 6, assert no more than 1 rows, no duplicate `except`, and no adjacent pair that violates `dd.year DESC, dd.month DESC`. Rejoin the returned keys to `agg_sales_category_month`, `fact_sales`, `dim_date`, and `aggregate_snapshot_before` to confirm `except` came from the same source rows. Add duplicate source candidates for `except`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-54 Exercise 6, start with the first relation in `agg_sales_category_month`, `fact_sales`, `dim_date`, and `aggregate_snapshot_before`; after each join, record total rows and distinct `except` so the exact fanout or loss is visible.
- **Clause check:** For sql-54 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `agg_sales_category_month`, `fact_sales`, `dim_date`, and `aggregate_snapshot_before`, preserve one row per `except`, and finish with `except` ordered by `dd.year DESC, dd.month DESC`.
- **Alternative/trade-off:** For sql-54 Exercise 6, the chosen form is justified by this lesson-specific rationale: The answer snapshots category aggregates, reruns the same latest period, and uses two-way `EXCEPT`. Evaluate another form against the concrete expected result (at most one row keyed by `except`) and the verification above.
- **Edge case:** Add duplicate source candidates for `except`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
