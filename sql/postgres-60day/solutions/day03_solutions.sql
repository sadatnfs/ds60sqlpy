-- Day 03 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Use inner joins only when unmatched rows should disappear, and verify key cardinality before aggregating.
-- Assumptions: Foreign keys define expected many-to-one relationships. Net line revenue is `unit_price * quantity * (1 - discount)`.
-- Pitfall: A missing or incomplete `ON` condition creates row multiplication; joining two detail tables before aggregation can multiply measures.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: List orders with customer names and countries.
-- Why: Join the order foreign key to the customer primary key and qualify every selected column.
-- Expected: One row per order.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.order_date,
       o.total_amount,
       c.customer_id,
       c.full_name,
       c.country
FROM orders AS o
JOIN customers AS c
  ON c.customer_id = o.customer_id
ORDER BY o.order_date DESC, o.order_id DESC;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Calculate each order item's net line revenue with the product name and category.
-- Why: Remain at one row per order item; do not aggregate until the desired grain changes.
-- Expected: One row per order item.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT oi.order_item_id,
       oi.order_id,
       p.product_id,
       p.name,
       p.category,
       oi.quantity,
       ROUND(oi.unit_price * oi.quantity * (1 - oi.discount), 2) AS line_revenue
FROM order_items AS oi
JOIN products AS p
  ON p.product_id = oi.product_id
ORDER BY oi.order_id, oi.order_item_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: List payments with order status and customer name.
-- Why: Follow payments → orders → customers using each declared foreign key.
-- Expected: One row per payment.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT p.payment_id,
       p.payment_date,
       p.amount,
       p.method,
       o.order_id,
       o.status,
       c.full_name
FROM payments AS p
JOIN orders AS o
  ON o.order_id = p.order_id
JOIN customers AS c
  ON c.customer_id = o.customer_id
ORDER BY p.payment_date DESC, p.payment_id DESC;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation.
-- Why: Aggregate items and payments separately to one row per order before joining those aggregates.
-- Expected: One row per order; no six-row multiplication.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH item_totals AS (
  SELECT oi.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS item_total
  FROM order_items AS oi
  GROUP BY oi.order_id
), payment_totals AS (
  SELECT p.order_id,
         SUM(p.amount) AS paid_total
  FROM payments AS p
  GROUP BY p.order_id
)
SELECT o.order_id,
       ROUND(it.item_total, 2) AS item_total,
       ROUND(COALESCE(pt.paid_total, 0), 2) AS paid_total
FROM orders AS o
JOIN item_totals AS it
  ON it.order_id = o.order_id
LEFT JOIN payment_totals AS pt
  ON pt.order_id = o.order_id
ORDER BY o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Repair a customer/order join whose `ON` clause compares unrelated IDs.
-- Why: Join `orders.customer_id` to `customers.customer_id`; verify output cannot exceed the order count for an inner many-to-one join.
-- Expected: Exactly one customer match per order.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
SELECT COUNT(*) AS joined_rows,
       COUNT(DISTINCT o.order_id) AS distinct_orders
FROM orders AS o
JOIN customers AS c
  ON c.customer_id = o.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Calculate net line revenue by customer country without double-counting order totals.
-- Why: Start from line items, join through orders and customers, then aggregate at country grain.
-- Expected: One row per country represented by an order.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.country,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue
FROM order_items AS oi
JOIN orders AS o
  ON o.order_id = oi.order_id
JOIN customers AS c
  ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY net_revenue DESC, c.country;

-- No course answer persists changes or temporary objects.
ROLLBACK;
