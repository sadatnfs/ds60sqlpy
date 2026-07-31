-- Day 20 executable solutions
-- SOLUTION READING MAP — sql-20: First Last Value
-- Explanation: sql/postgres-60day/solutions/day20_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day20_solutions.sql
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
-- Focus: Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.
-- Assumptions: First/last refer to ordered rows, not minimum/maximum values unless ordering states that. Ties need unique keys for deterministic row identity.
-- Pitfall: The default `LAST_VALUE` frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Show every order with the customer's first and last order timestamps.
-- Why: Use one full-partition frame from unbounded preceding through unbounded following.
-- Expected: One row per order with constant first/last values per customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       FIRST_VALUE(o.order_date) OVER customer_orders AS first_order_date,
       LAST_VALUE(o.order_date) OVER customer_orders AS last_order_date
FROM orders AS o
WINDOW customer_orders AS (
  PARTITION BY o.customer_id
  ORDER BY o.order_date, o.order_id
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
ORDER BY o.customer_id, o.order_date, o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Show each product with the cheapest and most expensive price in its category.
-- Why: Order by price and use a full frame; values tie without needing row identity.
-- Expected: One row per product.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT p.product_id,
       p.category,
       p.price,
       FIRST_VALUE(p.price) OVER category_prices AS category_min_price,
       LAST_VALUE(p.price) OVER category_prices AS category_max_price
FROM products AS p
WINDOW category_prices AS (
  PARTITION BY p.category
  ORDER BY p.price, p.product_id
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
ORDER BY p.category, p.price, p.product_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Compare every payment with the first and last payment amount for its order.
-- Why: Partition by order, order by timestamp/payment ID, and keep the full frame.
-- Expected: One row per payment.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT p.payment_id,
       p.order_id,
       p.payment_date,
       p.amount,
       FIRST_VALUE(p.amount) OVER payment_sequence AS first_payment_amount,
       LAST_VALUE(p.amount) OVER payment_sequence AS last_payment_amount
FROM payments AS p
WINDOW payment_sequence AS (
  PARTITION BY p.order_id
  ORDER BY p.payment_date, p.payment_id
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
ORDER BY p.order_id, p.payment_date, p.payment_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.
-- Why: The default ends at the current row; explicit following reaches the true last row.
-- Expected: Three rows showing default current value and full-frame 30.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT value,
       LAST_VALUE(value) OVER (ORDER BY value) AS default_last_value,
       LAST_VALUE(value) OVER (
         ORDER BY value
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS partition_last_value
FROM (VALUES (10), (20), (30)) AS sample(value)
ORDER BY value;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Return one first and one last order per customer without using window output as an accidental duplicate report.
-- Why: Compute first/last IDs with full-frame windows, then select distinct customer-level output.
-- Expected: One row per customer with orders.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - window frame: states exactly which rows or peers contribute to the current row's window result.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH annotated AS (
  SELECT o.customer_id,
         FIRST_VALUE(o.order_id) OVER customer_orders AS first_order_id,
         LAST_VALUE(o.order_id) OVER customer_orders AS last_order_id
  FROM orders AS o
  WINDOW customer_orders AS (
    PARTITION BY o.customer_id
    ORDER BY o.order_date, o.order_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  )
)
SELECT DISTINCT customer_id,
       first_order_id,
       last_order_id
FROM annotated
ORDER BY customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.
-- Why: `DISTINCT ON` keeps the first row under its mandatory leading order keys.
-- Expected: At most one latest order per customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `DISTINCT ON`: keeps the first row in each declared group, so its matching leading sort keys determine which row wins.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT DISTINCT ON (o.customer_id)
       o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount
FROM orders AS o
ORDER BY o.customer_id, o.order_date DESC, o.order_id DESC;

-- No course answer persists changes or temporary objects.
ROLLBACK;
