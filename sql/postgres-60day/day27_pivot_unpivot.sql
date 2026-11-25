-- Day 27: PIVOT / UNPIVOT (PostgreSQL approaches)
-- BEGINNER WORKFLOW - sql-27: Pivot Unpivot
-- Guide: sql/postgres-60day/companion-guides/day27_pivot_unpivot.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-27.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: order_items, orders, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Pivot with conditional aggregation when output categories are known, and unpivot with explicit typed rows while preserving missing-value meaning.
-- Assumptions: PostgreSQL core has no portable dynamic PIVOT keyword. `FILTER`, `CASE`, `VALUES`, JSON objects, or optional `tablefunc` serve different needs.
-- Pitfall: Replacing missing category combinations with zero is a business decision; dynamic columns are difficult for stable downstream schemas.
-- Predict row grain and NULL/order behavior before executing each example.
-- Approach 1: Conditional aggregation (portable)
SELECT
  p.category,
  SUM(oi.quantity) FILTER (WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 1) AS jan_qty,
  SUM(oi.quantity) FILTER (WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 2) AS feb_qty,
  SUM(oi.quantity) FILTER (WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 3) AS mar_qty
FROM
  order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
WHERE
  o.order_date >= (date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AT TIME ZONE 'UTC')
  AND o.order_date < (date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') + INTERVAL '1 year') AT TIME ZONE 'UTC'
GROUP BY
  p.category
ORDER BY
  p.category;

-- Approach 2: crosstab (requires the optional tablefunc extension; an
-- authorized database role must install it before this query is used)
-- SELECT * FROM crosstab(
--   $$
--   SELECT p.category::text AS rowid,
--          date_part('month', o.order_date)::int AS bucket,
--          SUM(oi.quantity)::numeric AS value
--   FROM order_items oi
--   JOIN orders o ON o.order_id = oi.order_id
--   JOIN products p ON p.product_id = oi.product_id
--   WHERE o.order_date >= date_trunc('year', now())
--   GROUP BY p.category, date_part('month', o.order_date)
--   ORDER BY 1,2
--   $$,
--   $$ SELECT m FROM generate_series(1,12) AS t(m) $$
-- ) AS ct(category text, m1 numeric, m2 numeric, m3 numeric, m4 numeric, m5 numeric, m6 numeric, m7 numeric, m8 numeric, m9 numeric, m10 numeric, m11 numeric, m12 numeric);
-- UNPIVOT-like: calculate the wide row once, then turn named columns into rows.
WITH source AS (
  SELECT
    p.category,
    EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC')::integer AS month_number,
    oi.quantity
  FROM
    order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
  WHERE
    o.order_date >= (date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AT TIME ZONE 'UTC')
    AND o.order_date < (date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') + INTERVAL '1 year') AT TIME ZONE 'UTC'
),
wide AS (
  SELECT
    category,
    SUM(quantity) FILTER (WHERE month_number = 1) AS jan_qty,
  SUM(quantity) FILTER (WHERE month_number = 2) AS feb_qty
FROM
  source
GROUP BY
  category
)
SELECT
  wide.category,
  month_value.month_name,
  month_value.quantity
FROM
  wide
  CROSS JOIN LATERAL (
    VALUES ('jan', wide.jan_qty),
      ('feb', wide.feb_qty)) AS month_value (month_name, quantity)
ORDER BY
  wide.category,
  month_value.month_name;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Pivot order counts by status into one summary row.
--    Hint: Use one filtered count per known status and keep an all-orders denominator.
--    Inputs: For sql-27 Exercise 1, read from `orders` and pivot the status counts into one row, with one `COUNT(*) FILTER (WHERE status = ...)` column per known status plus `all_orders`.
--    Expected result/shape: For sql-27 Exercise 1, expected output: Exactly one row. The final columns are `placed_orders`, `paid_orders`, `shipped_orders`, `delivered_orders`, `returned_orders`, and `all_orders`.
--    Verify: For sql-27 Exercise 1, confirm one row with `placed_orders` 873, `paid_orders` 872, `shipped_orders` 873, `delivered_orders` 872, `returned_orders` 872, and `all_orders` 4362; the five status columns must add up to `all_orders`, or an unknown status exists.
--    Hint ladder, rung 1: For sql-27 Exercise 1, run `SELECT status, COUNT(*) FROM orders GROUP BY status` first; each pivot column must match one of those counts.
-- 2. [Query writing] Pivot customer counts for US, CA, GB, and DE by segment.
--    Hint: Group at segment grain and use filtered counts for known country columns.
--    Inputs: For sql-27 Exercise 2, read the 500 rows of `customers`, group by `segment`, and turn four countries into columns with `COUNT(*) FILTER (WHERE country = ...)`; `all_customers` counts every row in the segment, including the 312 customers in AU, BR, FR, and IN.
--    Expected result/shape: For sql-27 Exercise 2, expected output: exactly 4 rows of 125 customers each, and every segment maps to one country in this seed: `gold` has 63 GB customers, `platinum` 63 DE, `silver` 63 CA, and `standard` 63 US, with 0 in the other three columns. The final columns are `segment`, `us_customers`, `ca_customers`, `gb_customers`, `de_customers`, and `all_customers`. The final order is `c.segment NULLS LAST`.
--    Verify: For sql-27 Exercise 2, confirm `all_customers` adds to 500 and that each country column adds to its `SELECT COUNT(*) FROM customers WHERE country = ...` count of 63; then, inside `BEGIN ... ROLLBACK`, run `UPDATE customers SET segment = NULL WHERE customer_id = 1` (a US customer) and confirm a fifth row with a NULL segment appears last with 1 US customer, while `standard` drops to 62 and 124.
--    Hint ladder, rung 1: For sql-27 Exercise 2, inspect the source keys that survive `WHERE`; then confirm the groups are `segment`; then check `c.segment NULLS LAST` before applying the row cap.
-- 3. [Query writing] Unpivot a wide quarterly sample into quarter/amount rows.
--    Hint: Use a lateral `VALUES` relation with one output row per source column.
--    Inputs: For sql-27 Exercise 3, no table is read: the `wide` CTE holds two `VALUES` rows, company A with 10, 20, 30, 40 and company B with 5, NULL, 15, 25, and `CROSS JOIN LATERAL (VALUES ...)` turns each row's four quarter columns into four `(quarter, amount)` rows.
--    Expected result/shape: For sql-27 Exercise 3, expected output: exactly 8 rows, four per company, with B `Q2` kept as a row whose `amount` is NULL. The final columns are `company`, `quarter`, and `amount`. The final order is `w.company, unpivoted.quarter`.
--    Verify: For sql-27 Exercise 3, confirm 8 rows, 4 per company, that `SUM(amount)` is 100 for A and 45 for B, and that exactly one row has `amount IS NULL`; adding `WHERE unpivoted.amount IS NOT NULL` would return 7 rows and lose the fact that B reported nothing for `Q2`.
--    Hint ladder, rung 1: For sql-27 Exercise 3, start with the first relation in `wide`; after each join, record total rows and distinct `company` so the exact fanout or loss is visible.
-- 4. [Prediction] Compare a missing pivot combination with a real zero and preserve the distinction.
--    Hint: Filtered `SUM` returns NULL when no rows contribute; `COALESCE` should be used only when the report defines absence as zero.
--    Inputs: For sql-27 Exercise 4, read the 10000 `expenses` rows (5 categories, 2000 each, dated over the two years before the load), group by `category`, and sum only January rows with `FILTER (WHERE EXTRACT(MONTH FROM expense_date) = 1)`, once raw and once wrapped in `COALESCE(..., 0)`.
--    Expected result/shape: For sql-27 Exercise 4, expected output: exactly 5 rows; every category has January rows on this load (164 to 192 rows across two Januaries), so both columns match, for example COGS 856904.40 and Marketing 972676.11. The final columns are `category`, `january_observed_amount`, and `january_reported_zero_if_absent`. The final order is `e.category`.
--    Verify: For sql-27 Exercise 4, confirm each category's January row count with `SELECT category, COUNT(*) FROM expenses WHERE EXTRACT(MONTH FROM expense_date) = 1 GROUP BY category`; then, inside `BEGIN ... ROLLBACK`, insert `('Legal', 100, '2026-03-01')` and `('Travel', 0, '2026-01-15')` and confirm Legal returns NULL and 0 (no January rows) while Travel returns 0.00 and 0.00 (a real zero).
--    Hint ladder, rung 1: For sql-27 Exercise 4, inspect the source keys that survive `WHERE`; then confirm the groups are `category`; then check `e.category` before applying the row cap.
-- 5. [Debugging] Produce a dynamic category report as a JSONB object instead of generating unstable SQL columns.
--    Hint: Aggregate category/value pairs into data values so the result schema remains stable.
--    Inputs: For sql-27 Exercise 5, read `orders`, `order_items`, and `products`, round net item revenue per UTC month and `category` in `category_month`, then fold each month's six rows into one JSONB value with `jsonb_object_agg(category, revenue ORDER BY category)`.
--    Expected result/shape: For sql-27 Exercise 5, expected output: one row per UTC month (46 on this load), each object holding all 6 category keys; the first month is `{"Home": 30.20, "Books": 279.76, "Beauty": 94.00, "Sports": 175.41, "Apparel": 407.05, "Electronics": 216.84}`, because JSONB stores keys shorter first, not in the `ORDER BY` order. The final columns are `month_start`, and `revenue_by_category`. The final order is `month_start`.
--    Verify: For sql-27 Exercise 5, confirm every object has 6 keys with `jsonb_object_keys`, and that summing `jsonb_each_text` values over all months gives 2355647.24, slightly above the unrounded 2355647.12 because each cell was rounded first; a missing key such as `revenue_by_category -> 'Toys'` returns NULL, and `jsonb_object_agg` over `VALUES ('a', 1), (NULL, 2)` fails with `field name must not be null`.
--    Hint ladder, rung 1: For sql-27 Exercise 5, run `category_month` one at a time. Record each CTE's row count and `month_start` uniqueness before the next stage uses it.
-- 6. [Extension] Round-trip a wide sample to long form and back, verifying values and NULLs.
--    Hint: Unpivot with lateral values, then use conditional aggregation keyed by company.
--    Inputs: For sql-27 Exercise 6, no table is read: the `wide` CTE holds A with 10 and 20 and B with NULL and 5; `long` unpivots it into four `(company, quarter, amount)` rows, and the outer query pivots back with `MAX(amount) FILTER (WHERE quarter = ...)` grouped by `company`.
--    Expected result/shape: For sql-27 Exercise 6, expected output: exactly 2 rows, A with 10 and 20 and B with NULL and 5, identical to `wide`. The final columns are `company`, `q1`, and `q2`. The final order is `company`.
--    Verify: For sql-27 Exercise 6, confirm `long` has 4 rows with one NULL `amount`, and that both `SELECT * FROM wide EXCEPT SELECT ...` and the reverse return 0 rows, since `EXCEPT` treats the two NULLs as equal; then pivot `VALUES ('A', 'Q1', 10), ('A', 'Q1', 99), ('A', 'Q2', 20)` and confirm `q1` shows 99, because `MAX` silently hides a duplicate quarter that a `COUNT(*)` of 3 would reveal.
--    Hint ladder, rung 1: For sql-27 Exercise 6, run `long` one at a time. Record each CTE's row count and `company` uniqueness before the next stage uses it.
ROLLBACK;
