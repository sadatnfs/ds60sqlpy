-- Day 27: PIVOT / UNPIVOT (PostgreSQL approaches)
-- BEGINNER WORKFLOW — sql-27: Pivot Unpivot
-- Guide: sql/postgres-60day/companion-guides/day27_pivot_unpivot.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-27/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
SELECT p.category,
       SUM(oi.quantity) FILTER (
         WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 1
       ) AS jan_qty,
       SUM(oi.quantity) FILTER (
         WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 2
       ) AS feb_qty,
       SUM(oi.quantity) FILTER (
         WHERE EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC') = 3
       ) AS mar_qty
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.order_date >= (
        date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
        AT TIME ZONE 'UTC'
      )
  AND o.order_date < (
        date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
        + INTERVAL '1 year'
      ) AT TIME ZONE 'UTC'
GROUP BY p.category
ORDER BY p.category;

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
  SELECT p.category,
         EXTRACT(MONTH FROM o.order_date AT TIME ZONE 'UTC')::integer
           AS month_number,
         oi.quantity
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.order_date >= (
          date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
          AT TIME ZONE 'UTC'
        )
    AND o.order_date < (
          date_trunc('year', CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
          + INTERVAL '1 year'
        ) AT TIME ZONE 'UTC'
), wide AS (
  SELECT category,
         SUM(quantity) FILTER (WHERE month_number = 1) AS jan_qty,
         SUM(quantity) FILTER (WHERE month_number = 2) AS feb_qty
  FROM source
  GROUP BY category
)
SELECT wide.category,
       month_value.month_name,
       month_value.quantity
FROM wide
CROSS JOIN LATERAL (
  VALUES ('jan', wide.jan_qty), ('feb', wide.feb_qty)
) AS month_value(month_name, quantity)
ORDER BY wide.category, month_value.month_name;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Pivot order counts by status into one summary row.
--    Hint: Use one filtered count per known status and keep an all-orders denominator.
--    Inputs: For sql-27 Exercise 1, read from `orders`. Build the answer toward `placed_orders`, `paid_orders`, `shipped_orders`, `delivered_orders`, `returned_orders`, and `all_orders`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-27 Exercise 1, expected output: Exactly one row. The final columns are `placed_orders`, `paid_orders`, `shipped_orders`, `delivered_orders`, `returned_orders`, and `all_orders`.
--    Verify: For sql-27 Exercise 1, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `placed_orders`, `paid_orders`, `shipped_orders`, `delivered_orders`, `returned_orders`, and `all_orders` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-27 Exercise 1, inspect the source keys that survive `WHERE`.
-- 2. [Query writing] Pivot customer counts for US, CA, GB, and DE by segment.
--    Hint: Group at segment grain and use filtered counts for known country columns.
--    Inputs: For sql-27 Exercise 2, read from `customers`. Build the answer toward `segment`, `us_customers`, `ca_customers`, `gb_customers`, `de_customers`, and `all_customers`; keep `segment` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-27 Exercise 2, expected output: One row per segment. The final columns are `segment`, `us_customers`, `ca_customers`, `gb_customers`, `de_customers`, and `all_customers`. The final order is `c.segment NULLS LAST`.
--    Verify: For sql-27 Exercise 2, independently aggregate `customers` by `segment`; require one output row for every distinct `segment` tuple and compare `us_customers`, `ca_customers`, `gb_customers`, `de_customers`, and `all_customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `us_customers`, `ca_customers`, and `gb_customers` for the existing `segment` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-27 Exercise 2, inspect the source keys that survive `WHERE`; then confirm the groups are `segment`; then check `c.segment NULLS LAST` before applying the row cap.
-- 3. [Query writing] Unpivot a wide quarterly sample into quarter/amount rows.
--    Hint: Use a lateral `VALUES` relation with one output row per source column.
--    Inputs: For sql-27 Exercise 3, read from `wide`. Build the answer toward `company`, `quarter`, and `amount`; keep `company` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-27 Exercise 3, expected output: Eight rows from two source rows and four quarters. The final columns are `company`, `quarter`, and `amount`. The final order is `w.company, unpivoted.quarter`.
--    Verify: For sql-27 Exercise 3, project `company` plus the raw source columns from `wide` at each join stage; record row count and distinct `company`, then assert the final `company`, `quarter`, and `amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `company`; verify the result gains exactly one row carrying that `company` value.
--    Hint ladder, rung 1: For sql-27 Exercise 3, start with the first relation in `wide`; after each join, record total rows and distinct `company` so the exact fanout or loss is visible.
-- 4. [Prediction] Compare a missing pivot combination with a real zero and preserve the distinction.
--    Hint: Filtered `SUM` returns NULL when no rows contribute; `COALESCE` should be used only when the report defines absence as zero.
--    Inputs: For sql-27 Exercise 4, read from `expenses`. Build the answer toward `category`, `january_observed_amount`, and `january_reported_zero_if_absent`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-27 Exercise 4, expected output: One row per expense category with nullable/zero-aware columns. The final columns are `category`, `january_observed_amount`, and `january_reported_zero_if_absent`. The final order is `e.category`.
--    Verify: For sql-27 Exercise 4, independently aggregate `expenses` by `category`; require one output row for every distinct `category` tuple and compare `january_observed_amount` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `january_observed_amount` for the existing `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-27 Exercise 4, inspect the source keys that survive `WHERE`; then confirm the groups are `category`; then check `e.category` before applying the row cap.
-- 5. [Debugging] Produce a dynamic category report as a JSONB object instead of generating unstable SQL columns.
--    Hint: Aggregate category/value pairs into data values so the result schema remains stable.
--    Inputs: For sql-27 Exercise 5, read from `orders`, `order_items`, and `products`. Build the answer toward `month_start`, and `revenue_by_category`; keep `month_start` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-27 Exercise 5, expected output: One row per UTC month with a JSON object of category revenue. The final columns are `month_start`, and `revenue_by_category`. The final order is `month_start`.
--    Verify: For sql-27 Exercise 5, independently aggregate `orders`, `order_items`, and `products` by `month_start`; require one output row for every distinct `month_start` tuple and compare `revenue_by_category` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue_by_category` for the existing `month_start` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-27 Exercise 5, run `category_month` one at a time. Record each CTE's row count and `month_start` uniqueness before the next stage uses it.
-- 6. [Extension] Round-trip a wide sample to long form and back, verifying values and NULLs.
--    Hint: Unpivot with lateral values, then use conditional aggregation keyed by company.
--    Inputs: For sql-27 Exercise 6, read from `wide`. Build the answer toward `company`, `q1`, and `q2`; keep `company` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-27 Exercise 6, expected output: Two reconstructed rows matching the source. The final columns are `company`, `q1`, and `q2`. The final order is `company`.
--    Verify: For sql-27 Exercise 6, independently aggregate `wide` by `company`; require one output row for every distinct `company` tuple and compare `q1`, and `q2` tuple by tuple. Repeat with `NULL` in `company`, and `q1` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-27 Exercise 6, run `long` one at a time. Record each CTE's row count and `company` uniqueness before the next stage uses it.

ROLLBACK;
