-- Day 19 executable solutions
-- SOLUTION READING MAP — sql-19: Running Aggregates
-- Explanation: sql/postgres-60day/solutions/day19_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day19_solutions.sql
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
-- Focus: Define cumulative and moving window frames explicitly so peers, boundaries, and partition resets match the business question.
-- Assumptions: Ordered money windows use exact numeric. `ROWS` counts physical ordered rows; `RANGE` groups peers with equal ordering values.
-- Pitfall: Relying on the default frame can include tied peers unexpectedly; a moving-row window is not automatically a moving-time window.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Calculate cumulative stored revenue across all orders.
-- Why: Order by timestamp and unique ID; declare `ROWS ... CURRENT ROW`.
-- Expected: One row per order with nondecreasing cumulative revenue.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.order_date,
       o.total_amount,
       SUM(o.total_amount) OVER (
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cumulative_revenue
FROM orders AS o
ORDER BY o.order_date, o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Calculate each customer's cumulative stored spend.
-- Why: Partition by customer and reset the explicit row frame for every customer.
-- Expected: One row per order.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       o.total_amount,
       SUM(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS customer_cumulative_spend
FROM orders AS o
ORDER BY o.customer_id, o.order_date, o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Calculate a trailing seven-order average within each customer.
-- Why: A seven-row frame is based on observations, not seven calendar days.
-- Expected: One row per order with up to seven observations in its frame.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       ROUND(
         AVG(o.total_amount) OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date, o.order_id
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
         ),
         2
       ) AS trailing_7_order_average
FROM orders AS o
ORDER BY o.customer_id, o.order_date, o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Compare `ROWS` and `RANGE` cumulative sums when two rows share the same ordering value.
-- Why: `RANGE` includes ordering peers together; `ROWS` advances one physical row at a time.
-- Expected: Three rows making the peer difference visible.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT row_id,
       sort_value,
       amount,
       SUM(amount) OVER (
         ORDER BY sort_value, row_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS rows_sum,
       SUM(amount) OVER (
         ORDER BY sort_value
         RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS range_sum
FROM (VALUES
  (1, 1, 10),
  (2, 1, 20),
  (3, 2, 5)
) AS sample(row_id, sort_value, amount)
ORDER BY row_id;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Reset a running expense total at each category and month.
-- Why: Partition by both reset keys and order by date plus expense ID.
-- Expected: One row per expense.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT e.expense_id,
       e.category,
       e.expense_date,
       e.amount,
       SUM(e.amount) OVER (
         PARTITION BY e.category, date_trunc('month', e.expense_date)
         ORDER BY e.expense_date, e.expense_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS category_month_running_expense
FROM expenses AS e
ORDER BY e.category, e.expense_date, e.expense_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Prove the final cumulative stored revenue equals the ordinary stored-revenue sum.
-- Why: Select the last ordered cumulative value and compare it with an independent aggregate.
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
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
-- - `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
WITH running AS (
  SELECT o.order_id,
         o.order_date,
         SUM(o.total_amount) OVER (
           ORDER BY o.order_date, o.order_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
         ) AS cumulative_revenue
  FROM orders AS o
), final_running AS (
  SELECT r.cumulative_revenue
  FROM running AS r
  ORDER BY r.order_date DESC, r.order_id DESC
  LIMIT 1
)
SELECT ROUND(fr.cumulative_revenue, 2) AS final_cumulative,
       ROUND(SUM(o.total_amount), 2) AS aggregate_total,
       ROUND(fr.cumulative_revenue - SUM(o.total_amount), 2) AS difference
FROM final_running AS fr
CROSS JOIN orders AS o
GROUP BY fr.cumulative_revenue;

-- No course answer persists changes or temporary objects.
ROLLBACK;
