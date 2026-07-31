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
--    Inputs: Use only the declared lesson objects (order_items, orders, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 2. [Query writing] Pivot customer counts for US, CA, GB, and DE by segment.
--    Hint: Group at segment grain and use filtered counts for known country columns.
--    Inputs: Use only the declared lesson objects (order_items, orders, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 3. [Query writing] Unpivot a wide quarterly sample into quarter/amount rows.
--    Hint: Use a lateral `VALUES` relation with one output row per source column.
--    Inputs: Use only the declared lesson objects (order_items, orders, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 4. [Prediction] Compare a missing pivot combination with a real zero and preserve the distinction.
--    Hint: Filtered `SUM` returns NULL when no rows contribute; `COALESCE` should be used only when the report defines absence as zero.
--    Inputs: Use only the declared lesson objects (order_items, orders, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 5. [Debugging] Produce a dynamic category report as a JSONB object instead of generating unstable SQL columns.
--    Hint: Aggregate category/value pairs into data values so the result schema remains stable.
--    Inputs: Use only the declared lesson objects (order_items, orders, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
-- 6. [Extension] Round-trip a wide sample to long form and back, verifying values and NULLs.
--    Hint: Unpivot with lateral values, then use conditional aggregation keyed by company.
--    Inputs: Use only the declared lesson objects (order_items, orders, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.

ROLLBACK;
