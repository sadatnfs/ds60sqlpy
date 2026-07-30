-- Day 27 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Pivot with conditional aggregation when output categories are known, and unpivot with explicit typed rows while preserving missing-value meaning.
-- Assumptions: PostgreSQL core has no portable dynamic PIVOT keyword. `FILTER`, `CASE`, `VALUES`, JSON objects, or optional `tablefunc` serve different needs.
-- Pitfall: Replacing missing category combinations with zero is a business decision; dynamic columns are difficult for stable downstream schemas.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Pivot order counts by status into one summary row.
-- Why: Use one filtered count per known status and keep an all-orders denominator.
-- Expected: Exactly one row.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
SELECT COUNT(*) FILTER (WHERE o.status = 'placed') AS placed_orders,
       COUNT(*) FILTER (WHERE o.status = 'paid') AS paid_orders,
       COUNT(*) FILTER (WHERE o.status = 'shipped') AS shipped_orders,
       COUNT(*) FILTER (WHERE o.status = 'delivered') AS delivered_orders,
       COUNT(*) FILTER (WHERE o.status = 'returned') AS returned_orders,
       COUNT(*) AS all_orders
FROM orders AS o;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Pivot customer counts for US, CA, GB, and DE by segment.
-- Why: Group at segment grain and use filtered counts for known country columns.
-- Expected: One row per segment.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.segment,
       COUNT(*) FILTER (WHERE c.country = 'US') AS us_customers,
       COUNT(*) FILTER (WHERE c.country = 'CA') AS ca_customers,
       COUNT(*) FILTER (WHERE c.country = 'GB') AS gb_customers,
       COUNT(*) FILTER (WHERE c.country = 'DE') AS de_customers,
       COUNT(*) AS all_customers
FROM customers AS c
GROUP BY c.segment
ORDER BY c.segment NULLS LAST;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Unpivot a wide quarterly sample into quarter/amount rows.
-- Why: Use a lateral `VALUES` relation with one output row per source column.
-- Expected: Eight rows from two source rows and four quarters.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH wide(company, q1, q2, q3, q4) AS (
  VALUES
    ('A', 10::numeric, 20::numeric, 30::numeric, 40::numeric),
    ('B', 5::numeric, NULL::numeric, 15::numeric, 25::numeric)
)
SELECT w.company,
       unpivoted.quarter,
       unpivoted.amount
FROM wide AS w
CROSS JOIN LATERAL (
  VALUES
    ('Q1', w.q1),
    ('Q2', w.q2),
    ('Q3', w.q3),
    ('Q4', w.q4)
) AS unpivoted(quarter, amount)
ORDER BY w.company, unpivoted.quarter;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Compare a missing pivot combination with a real zero and preserve the distinction.
-- Why: Filtered `SUM` returns NULL when no rows contribute; `COALESCE` should be used only when the report defines absence as zero.
-- Expected: One row per expense category with nullable/zero-aware columns.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT e.category,
       SUM(e.amount) FILTER (
         WHERE EXTRACT(MONTH FROM e.expense_date) = 1
       ) AS january_observed_amount,
       COALESCE(
         SUM(e.amount) FILTER (
           WHERE EXTRACT(MONTH FROM e.expense_date) = 1
         ),
         0
       ) AS january_reported_zero_if_absent
FROM expenses AS e
GROUP BY e.category
ORDER BY e.category;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Produce a dynamic category report as a JSONB object instead of generating unstable SQL columns.
-- Why: Aggregate category/value pairs into data values so the result schema remains stable.
-- Expected: One row per UTC month with a JSON object of category revenue.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH category_month AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         p.category,
         ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  JOIN products AS p ON p.product_id = oi.product_id
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'), p.category
)
SELECT month_start,
       jsonb_object_agg(category, revenue ORDER BY category) AS revenue_by_category
FROM category_month
GROUP BY month_start
ORDER BY month_start;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Round-trip a wide sample to long form and back, verifying values and NULLs.
-- Why: Unpivot with lateral values, then use conditional aggregation keyed by company.
-- Expected: Two reconstructed rows matching the source.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH wide(company, q1, q2) AS (
  VALUES
    ('A', 10::numeric, 20::numeric),
    ('B', NULL::numeric, 5::numeric)
), long AS (
  SELECT w.company, u.quarter, u.amount
  FROM wide AS w
  CROSS JOIN LATERAL (
    VALUES ('Q1', w.q1), ('Q2', w.q2)
  ) AS u(quarter, amount)
)
SELECT company,
       MAX(amount) FILTER (WHERE quarter = 'Q1') AS q1,
       MAX(amount) FILTER (WHERE quarter = 'Q2') AS q2
FROM long
GROUP BY company
ORDER BY company;

-- No course answer persists changes or temporary objects.
ROLLBACK;
