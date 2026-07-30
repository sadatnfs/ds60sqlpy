-- Day 02 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.
-- Assumptions: Money columns are exact `numeric`; round only presentation values. `COUNT(column)` excludes NULL while `COUNT(*)` counts rows.
-- Pitfall: Selecting a non-grouped, non-aggregated column or using `WHERE` for an aggregate condition changes or invalidates the question.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Count customers by country and order countries by count then country.
-- Why: The output grain is one row per country; include a deterministic secondary sort.
-- Expected: One row per country.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.country,
       COUNT(*) AS customer_count
FROM customers AS c
GROUP BY c.country
ORDER BY customer_count DESC, c.country;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Calculate net revenue and average unit price by product category, keeping categories above 100,000 in revenue.
-- Why: Join at line grain, aggregate once per category, and place the aggregate predicate in `HAVING`.
-- Expected: One row per qualifying category.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `HAVING`: filters completed groups after aggregation, unlike `WHERE`, which filters source rows first.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT p.category,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue,
       ROUND(AVG(oi.unit_price), 2) AS average_unit_price
FROM order_items AS oi
JOIN products AS p
  ON p.product_id = oi.product_id
GROUP BY p.category
HAVING SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) > 100000
ORDER BY net_revenue DESC, p.category;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Summarize order count and average total by status, retaining statuses with at least 100 orders.
-- Why: Filter groups after aggregation with `HAVING COUNT(*)`.
-- Expected: One row per qualifying order status.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `HAVING`: filters completed groups after aggregation, unlike `WHERE`, which filters source rows first.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.status,
       COUNT(*) AS order_count,
       ROUND(AVG(o.total_amount), 2) AS average_order_total
FROM orders AS o
GROUP BY o.status
HAVING COUNT(*) >= 100
ORDER BY order_count DESC, o.status;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Show `COUNT(*)`, `COUNT(email)`, and missing-email count together; predict their relationship.
-- Why: `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit.
-- Expected: One row; present plus missing equals total.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
SELECT COUNT(*) AS all_rows,
       COUNT(c.email) AS nonnull_email_rows,
       COUNT(*) FILTER (WHERE c.email IS NULL) AS missing_email_rows
FROM customers AS c;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Repair a query that tries to filter `SUM(amount)` in `WHERE` by moving the aggregate condition to the correct clause.
-- Why: `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward.
-- Expected: One row per expense category over the threshold.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `HAVING`: filters completed groups after aggregation, unlike `WHERE`, which filters source rows first.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT e.category,
       ROUND(SUM(e.amount), 2) AS total_expense
FROM expenses AS e
GROUP BY e.category
HAVING SUM(e.amount) > 1000000
ORDER BY total_expense DESC, e.category;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Produce monthly order count, total revenue, and returned-order count for the last 12 complete or partial months.
-- Why: Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable.
-- Expected: Up to 12 month rows in chronological order.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT date_trunc('month', o.order_date)::date AS order_month,
       COUNT(*) AS order_count,
       ROUND(SUM(o.total_amount), 2) AS order_revenue,
       COUNT(*) FILTER (WHERE o.status = 'returned') AS returned_orders
FROM orders AS o
WHERE o.order_date >= date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'
GROUP BY date_trunc('month', o.order_date)
ORDER BY order_month;

-- No course answer persists changes or temporary objects.
ROLLBACK;
