-- Day 26 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.
-- Assumptions: Monthly reporting uses UTC. Window order always includes chronological keys; revenue uses exact numeric and is rounded only in final output.
-- Pitfall: Applying windows before aggregation compares detail rows, while filtering too early can remove the history a lag or moving frame needs.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Calculate monthly stored revenue and its prior-month value/change.
-- Why: Aggregate to month in a CTE, then lag the monthly measure.
-- Expected: One row per observed month.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH monthly AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         SUM(o.total_amount) AS revenue
  FROM orders AS o
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), compared AS (
  SELECT month_start,
         revenue,
         LAG(revenue) OVER (ORDER BY month_start) AS previous_revenue
  FROM monthly
)
SELECT month_start,
       ROUND(revenue, 2) AS revenue,
       ROUND(previous_revenue, 2) AS previous_revenue,
       ROUND(revenue - previous_revenue, 2) AS change
FROM compared
ORDER BY month_start;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Rank product categories by net revenue within each UTC order month.
-- Why: Aggregate month/category first, then rank the stable aggregate.
-- Expected: One row per observed month/category.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH category_month AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM orders AS o
  JOIN order_items AS oi
    ON oi.order_id = o.order_id
  JOIN products AS p
    ON p.product_id = oi.product_id
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'), p.category
)
SELECT month_start,
       category,
       ROUND(revenue, 2) AS revenue,
       DENSE_RANK() OVER (
         PARTITION BY month_start ORDER BY revenue DESC
       ) AS revenue_rank
FROM category_month
ORDER BY month_start, revenue_rank, category;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Return the top three category revenue levels per month.
-- Why: Rank in one CTE and filter the window result outside.
-- Expected: Top three revenue ranks for each observed month.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH category_month AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  JOIN products AS p ON p.product_id = oi.product_id
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'), p.category
), ranked AS (
  SELECT category_month.*,
         DENSE_RANK() OVER (
           PARTITION BY month_start ORDER BY revenue DESC
         ) AS revenue_rank
  FROM category_month
)
SELECT month_start, category, ROUND(revenue, 2) AS revenue, revenue_rank
FROM ranked
WHERE revenue_rank <= 3
ORDER BY month_start, revenue_rank, category;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Calculate each category's cumulative share of monthly revenue in descending contribution order.
-- Why: Divide running category revenue by the full monthly total; use explicit frames.
-- Expected: One row per month/category with final share equal to one.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH category_month AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM orders AS o
  JOIN order_items AS oi ON oi.order_id = o.order_id
  JOIN products AS p ON p.product_id = oi.product_id
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'), p.category
)
SELECT month_start,
       category,
       ROUND(revenue, 2) AS revenue,
       ROUND(
         SUM(revenue) OVER (
           PARTITION BY month_start
           ORDER BY revenue DESC, category
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
         ) / NULLIF(SUM(revenue) OVER (PARTITION BY month_start), 0),
         4
       ) AS cumulative_revenue_share
FROM category_month
ORDER BY month_start, revenue DESC, category;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Calculate a three-month moving average after building a dense month calendar.
-- Why: Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way.
-- Expected: A continuous chronological month series.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH bounds AS (
  SELECT MIN(date_trunc('month', o.order_date AT TIME ZONE 'UTC'))::date AS first_month,
         MAX(date_trunc('month', o.order_date AT TIME ZONE 'UTC'))::date AS last_month
  FROM orders AS o
), calendar AS (
  SELECT generate_series(first_month, last_month, INTERVAL '1 month')::date AS month_start
  FROM bounds
), monthly AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         SUM(o.total_amount) AS revenue
  FROM orders AS o
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), dense AS (
  SELECT c.month_start,
         COALESCE(m.revenue, 0) AS revenue
  FROM calendar AS c
  LEFT JOIN monthly AS m USING (month_start)
)
SELECT month_start,
       ROUND(revenue, 2) AS revenue,
       ROUND(
         AVG(revenue) OVER (
           ORDER BY month_start
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
         ),
         2
       ) AS moving_3_month_average
FROM dense
ORDER BY month_start;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Reconcile the final cumulative monthly revenue with the independent order total.
-- Why: Compare at the end of the CTE/window chain instead of assuming transformations preserved totals.
-- Expected: One row with zero difference.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
-- - `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
WITH monthly AS (
  SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_start,
         SUM(o.total_amount) AS revenue
  FROM orders AS o
  GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC')
), running AS (
  SELECT month_start,
         SUM(revenue) OVER (
           ORDER BY month_start
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
         ) AS cumulative_revenue
  FROM monthly
), final AS (
  SELECT cumulative_revenue
  FROM running
  ORDER BY month_start DESC
  LIMIT 1
)
SELECT ROUND(final.cumulative_revenue, 2) AS final_cumulative,
       ROUND(SUM(o.total_amount), 2) AS independent_total,
       ROUND(final.cumulative_revenue - SUM(o.total_amount), 2) AS difference
FROM final
CROSS JOIN orders AS o
GROUP BY final.cumulative_revenue;

-- No course answer persists changes or temporary objects.
ROLLBACK;
