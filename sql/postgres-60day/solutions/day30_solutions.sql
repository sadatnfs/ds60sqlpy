-- Day 30 executable solutions
-- SOLUTION READING MAP — sql-30: Phase2 Project
-- Explanation: sql/postgres-60day/solutions/day30_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day30_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Build a cohort-retention analysis through explicit grains, a stable denominator, a dense calendar, reconciled revenue, and clearly limited projections.
-- Assumptions: Cohort month is customer creation month in UTC. Active means at least one order in the order month. Net revenue is computed from line items.
-- Pitfall: Observed rows are not a complete calendar; active customers must not exceed original cohort size, and a moving average is not a production CLV model.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Calculate original customer count for each UTC signup cohort month.
-- Why: Build the denominator from customers, including customers who never order.
-- Expected: One row per cohort month.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
)
SELECT cohort_month,
       COUNT(*) AS cohort_size
FROM cohorts
GROUP BY cohort_month
ORDER BY cohort_month;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Calculate active customers and net line revenue for each cohort/order month.
-- Why: Aggregate line items to order grain before cohort joins, then count distinct active customers.
-- Expected: One row per observed cohort/order month.
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
WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
)
SELECT c.cohort_month,
       ov.order_month,
       COUNT(DISTINCT ov.customer_id) AS active_customers,
       ROUND(SUM(ov.order_value), 2) AS net_revenue
FROM cohorts AS c
JOIN order_values AS ov ON ov.customer_id = c.customer_id
GROUP BY c.cohort_month, ov.order_month
ORDER BY c.cohort_month, ov.order_month;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Calculate cohort month offset and retention using original cohort size.
-- Why: Use year-plus-month age components and guard the denominator.
-- Expected: Observed cohort/offset rows with retention from 0 to 1.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_month
), activity AS (
  SELECT c.cohort_month,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
         COUNT(DISTINCT o.customer_id) AS active_customers
  FROM cohorts AS c
  JOIN orders AS o ON o.customer_id = c.customer_id
  GROUP BY c.cohort_month,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')
)
SELECT a.cohort_month,
       (
         EXTRACT(YEAR FROM age(a.order_month, a.cohort_month)) * 12
         + EXTRACT(MONTH FROM age(a.order_month, a.cohort_month))
       )::integer AS month_offset,
       cs.cohort_size,
       a.active_customers,
       ROUND(a.active_customers::numeric / NULLIF(cs.cohort_size, 0), 4) AS retention_rate
FROM activity AS a
JOIN cohort_sizes AS cs USING (cohort_month)
ORDER BY a.cohort_month, month_offset;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Create a dense cohort/offset spine from offset 0 through 12 and show missing activity as zero.
-- Why: Cross join cohort months with generate_series, then left join observed activity at the same offset grain.
-- Expected: Thirteen rows per cohort.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_month
), activity AS (
  SELECT c.cohort_month,
         (
           EXTRACT(YEAR FROM age(
             date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date,
             c.cohort_month
           )) * 12
           + EXTRACT(MONTH FROM age(
             date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date,
             c.cohort_month
           ))
         )::integer AS month_offset,
         COUNT(DISTINCT o.customer_id) AS active_customers
  FROM cohorts AS c
  JOIN orders AS o ON o.customer_id = c.customer_id
  GROUP BY c.cohort_month,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), spine AS (
  SELECT cs.cohort_month,
         cs.cohort_size,
         offset_value AS month_offset
  FROM cohort_sizes AS cs
  CROSS JOIN generate_series(0, 12) AS offsets(offset_value)
)
SELECT s.cohort_month,
       s.month_offset,
       s.cohort_size,
       COALESCE(a.active_customers, 0) AS active_customers
FROM spine AS s
LEFT JOIN activity AS a
  ON a.cohort_month = s.cohort_month
 AND a.month_offset = s.month_offset
ORDER BY s.cohort_month, s.month_offset;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Calculate revenue per active customer and a trailing three-observation annualized teaching projection.
-- Why: Compute stable cohort metrics before applying the window; disclose that observed rows may have month gaps.
-- Expected: One row per observed cohort/month with nullable guarded measures.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
), metrics AS (
  SELECT c.cohort_month,
         ov.order_month,
         (
           EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12
           + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month))
         )::integer AS month_offset,
         COUNT(DISTINCT ov.customer_id) AS active_customers,
         SUM(ov.order_value) AS revenue
  FROM cohorts AS c
  JOIN order_values AS ov ON ov.customer_id = c.customer_id
  GROUP BY c.cohort_month, ov.order_month
), per_active AS (
  SELECT metrics.*,
         revenue / NULLIF(active_customers, 0) AS revenue_per_active
  FROM metrics
)
SELECT cohort_month,
       order_month,
       month_offset,
       active_customers,
       ROUND(revenue, 2) AS revenue,
       ROUND(revenue_per_active, 2) AS revenue_per_active,
       ROUND(
         AVG(revenue_per_active) OVER (
           PARTITION BY cohort_month
           ORDER BY month_offset
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
         ) * 12,
         2
       ) AS illustrative_annualized_clv
FROM per_active
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month, month_offset;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Audit cohort constraints and reconcile cohort revenue to net line revenue for offsets 0–12.
-- Why: Calculate violations and compare totals at the same scoped population.
-- Expected: One row with zero retention violations and zero revenue difference.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month
  FROM customers AS c
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_month
), metrics AS (
  SELECT c.cohort_month,
         ov.order_month,
         (
           EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12
           + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month))
         )::integer AS month_offset,
         COUNT(DISTINCT ov.customer_id) AS active_customers,
         SUM(ov.order_value) AS revenue
  FROM cohorts AS c
  JOIN order_values AS ov ON ov.customer_id = c.customer_id
  GROUP BY c.cohort_month, ov.order_month
), scoped AS (
  SELECT m.*, cs.cohort_size
  FROM metrics AS m
  JOIN cohort_sizes AS cs USING (cohort_month)
  WHERE m.month_offset BETWEEN 0 AND 12
)
SELECT COUNT(*) FILTER (
         WHERE active_customers > cohort_size
       ) AS active_exceeds_cohort_violations,
       ROUND(SUM(revenue), 2) AS cohort_revenue,
       ROUND((
         SELECT SUM(ov.order_value)
         FROM order_values AS ov
         JOIN cohorts AS c ON c.customer_id = ov.customer_id
         WHERE (
           EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12
           + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month))
         )::integer BETWEEN 0 AND 12
       ), 2) AS independent_revenue,
       ROUND(
         SUM(revenue) - (
           SELECT SUM(ov.order_value)
           FROM order_values AS ov
           JOIN cohorts AS c ON c.customer_id = ov.customer_id
           WHERE (
             EXTRACT(YEAR FROM age(ov.order_month, c.cohort_month)) * 12
             + EXTRACT(MONTH FROM age(ov.order_month, c.cohort_month))
           )::integer BETWEEN 0 AND 12
         ),
         2
       ) AS revenue_difference
FROM scoped;

-- No course answer persists changes or temporary objects.
ROLLBACK;
