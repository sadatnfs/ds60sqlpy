# Day 35 — Solutions: Avoiding Performance Pitfalls


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day35_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day35_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Sargability, Half-open range, Set-based rewrite. Its worked-model focus is:
Compare datetrunc('day', orderdate) = targetday with orderdate >= targetday AND orderdate < targetday + interval '1 day'. Test timestamps at both boundaries, reconcile row IDs, and compare plans with a matching orderdate index.

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

This learner day asks for three rewrites that keep functions off an indexed
column and one rewrite of a correlated subquery. The examples use half-open
timestamp ranges because they are precise and B-tree friendly.

## Exercise 1 — Three sargable predicate rewrites

Each “better” predicate leaves `order_date` bare, allowing an index on that
column to define a contiguous range.

```sql
SET search_path TO training, public;

-- 1. One calendar day
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE date_trunc('day', order_date) = date_trunc('day', CURRENT_TIMESTAMP);

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date >= date_trunc('day', CURRENT_TIMESTAMP)
  AND order_date < date_trunc('day', CURRENT_TIMESTAMP) + interval '1 day';

-- 2. Current calendar year
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE EXTRACT(year FROM order_date) = EXTRACT(year FROM CURRENT_DATE);

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date >= date_trunc('year', CURRENT_DATE)
  AND order_date < date_trunc('year', CURRENT_DATE) + interval '1 year';

-- 3. Last seven calendar dates, including today
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date::date >= CURRENT_DATE - 6;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE order_date >= (CURRENT_DATE - 6)::timestamptz
  AND order_date < (CURRENT_DATE + 1)::timestamptz;
```

Expected result sets within each pair are equivalent under the session time
zone. Plan nodes can remain sequential scans because the dataset is small or
because the demonstration index from Day 32 was rolled back.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 1, run the underlying read-only query over `orders`, `order_date`, and `CURRENT_DATE` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-35 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`.
- **Independent verification:** For sql-35 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-35 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
- **Clause check:** For sql-35 Exercise 1, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `orders`, `order_date`, and `CURRENT_DATE`, preserve one row per `order_id`, and finish with `order_id`.
- **Alternative/trade-off:** For sql-35 Exercise 1, the chosen form is justified by this lesson-specific rationale: Each “better” predicate leaves `order_date` bare, allowing an index on that column to define a contiguous range. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 2 — Replace a per-customer correlated aggregate

```sql
SET search_path TO training, public;

EXPLAIN (ANALYZE, BUFFERS)
SELECT c.customer_id,
       (
         SELECT SUM(o.total_amount)
         FROM orders o
         WHERE o.customer_id = c.customer_id
       ) AS lifetime_revenue
FROM customers c;

EXPLAIN (ANALYZE, BUFFERS)
WITH order_totals AS (
  SELECT customer_id,
         SUM(total_amount) AS lifetime_revenue
  FROM orders
  GROUP BY customer_id
)
SELECT c.customer_id,
       ot.lifetime_revenue
FROM customers c
LEFT JOIN order_totals ot ON ot.customer_id = c.customer_id;
```

Expected shape: one row per customer in both forms. The `LEFT JOIN` is required
to retain customers with no orders; changing it to an inner join would alter
the answer.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 2, run the underlying read-only query over `orders`, and `customers` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-35 Exercise 2, expected output: one row per customer in both forms. The `LEFT JOIN` is required to retain customers with no orders; changing it to an inner join would alter the answer. The final columns are `customer_id`, and `lifetime_revenue`.
- **Independent verification:** For sql-35 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-35 Exercise 2, run `order_totals` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-35 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, and `SELECT`. Read only those operations: begin at `orders`, and `customers`, preserve one row per `customer_id`, and finish with `customer_id`, and `lifetime_revenue`.
- **Alternative/trade-off:** For sql-35 Exercise 2, the chosen form is justified by this lesson-specific rationale: Expected shape: one row per customer in both forms. Evaluate another form against the concrete expected result (one row per customer in both forms. The `LEFT JOIN` is required to retain customers with no orders; changing it to an inner join would alter the answer) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Pitfalls

- Sargability does not guarantee an index scan; it merely gives the planner the
  option.
- Timestamp-to-date conversion uses the session time zone. Define business
  timezone semantics before reporting calendar periods.
- PostgreSQL can decorrelate some subqueries. Confirm the plan instead of
  assuming every correlated expression runs once per outer row.
- Do not hide fanout with `DISTINCT`; fix the join grain.

## Exercise 3 — Diagnose wildcard search

`LIKE 'A%'` has a fixed starting prefix; `LIKE '%A%'` does not. A normal B-tree
therefore has a more direct opportunity on the first pattern, subject to
collation/operator-class details.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 3, run the underlying read-only query over `customers` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-35 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`.
- **Independent verification:** For sql-35 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-35 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.
- **Clause check:** For sql-35 Exercise 3, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`.
- **Alternative/trade-off:** For sql-35 Exercise 3, the chosen form is justified by this lesson-specific rationale: `LIKE 'A%'` has a fixed starting prefix; `LIKE '%A%'` does not. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 4 — Replace OFFSET with a seek tuple

The boundary tuple comes from `(order_date DESC, order_id DESC)`. The next page
uses the matching tuple comparison and repeats that deterministic order.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 4, read from `orders`. Build the answer toward `order_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-35 Exercise 4, expected output: at most 20 rows keyed by `order_id`. The final columns are `order_id`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
- **Independent verification:** For sql-35 Exercise 4, assert no more than 20 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_date DESC, o.order_id DESC`. Rejoin the returned keys to `orders` to confirm `order_id`, and `order_date` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_date DESC, o.order_id DESC`.
- **Intermediate relation check:** For sql-35 Exercise 4, run `boundary` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-35 Exercise 4, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, preserve one row per `order_id`, and finish with `order_id`, and `order_date` ordered by `o.order_date DESC, o.order_id DESC`.
- **Alternative/trade-off:** For sql-35 Exercise 4, the chosen form is justified by this lesson-specific rationale: The boundary tuple comes from `(order_date DESC, order_id DESC)`. Evaluate another form against the concrete expected result (at most 20 rows keyed by `order_id`) and the verification above.
- **Edge case:** Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_date DESC, o.order_id DESC`.

## Exercise 5 — Fix payment/item fanout

The answer groups each many-side by `order_id` before joining. `DISTINCT` would
only conceal duplicated output, not repair multiplied sums.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 5, read from `payments`, `order_items`, and `orders`. Build the answer toward `order_id`, `paid`, and `sold`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-35 Exercise 5, expected output: at most 20 rows keyed by `order_id`. The final columns are `order_id`, `paid`, and `sold`. The final order is `o.order_id`.
- **Independent verification:** For sql-35 Exercise 5, assert no more than 20 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_id`. Rejoin the returned keys to `payments`, `order_items`, and `orders` to confirm `order_id`, `paid`, and `sold` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_id`.
- **Intermediate relation check:** For sql-35 Exercise 5, run `paid`, and `sold` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-35 Exercise 5, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `payments`, `order_items`, and `orders`, preserve one row per `order_id`, and finish with `order_id`, `paid`, and `sold` ordered by `o.order_id`.
- **Alternative/trade-off:** For sql-35 Exercise 5, the chosen form is justified by this lesson-specific rationale: The answer groups each many-side by `order_id` before joining. Evaluate another form against the concrete expected result (at most 20 rows keyed by `order_id`) and the verification above.
- **Edge case:** Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_id`.

## Exercise 6 — Define nullable counts

`COUNT(*)` measures customer rows; `COUNT(email)` measures customers with a
non-NULL email. The difference is a useful missingness count, not a discrepancy.

### Reasoning and verification

- **Inputs/evidence:** For sql-35 Exercise 6, read from `customers`. Build the answer toward `customer_rows`, `customers_with_email`, and `customers_without_email`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-35 Exercise 6, expected output: one row per `customer_id`. The final columns are `customer_rows`, `customers_with_email`, and `customers_without_email`.
- **Independent verification:** For sql-35 Exercise 6, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_rows`, `customers_with_email`, and `customers_without_email` against `customers`. Repeat with `NULL` in `customer_rows`, and `customers_with_email` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-35 Exercise 6, select `customer_id` from `customers` before adding derived columns.
- **Clause check:** For sql-35 Exercise 6, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_rows`, `customers_with_email`, and `customers_without_email`.
- **Alternative/trade-off:** For sql-35 Exercise 6, the chosen form is justified by this lesson-specific rationale: `COUNT()` measures customer rows; `COUNT(email)` measures customers with a non-NULL email. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Repeat with `NULL` in `customer_rows`, and `customers_with_email` and state whether the row is kept, rejected, or classified.
