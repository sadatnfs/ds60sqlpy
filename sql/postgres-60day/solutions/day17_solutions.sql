-- Day 17 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Choose `ROW_NUMBER`, `RANK`, or `DENSE_RANK` from tie semantics, and separate ranking from top-N filtering.
-- Assumptions: All ranking orders include a stable key when a unique sequence is required. Equal business values intentionally tie under rank functions.
-- Pitfall: `ROW_NUMBER` breaks ties, `RANK` leaves gaps, and `DENSE_RANK` does not; using the wrong function changes top-N membership.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Number each customer's orders from newest to oldest.
-- Why: Partition by customer and use order date plus order ID as a unique descending order.
-- Expected: One row per order with sequence starting at one per customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       ROW_NUMBER() OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date DESC, o.order_id DESC
       ) AS recency_number
FROM orders AS o
ORDER BY o.customer_id, recency_number;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Rank products by price within category using both `RANK` and `DENSE_RANK`.
-- Why: Rank only on price so equal prices tie; order the final display by product ID.
-- Expected: One row per product with two rank semantics.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT p.product_id,
       p.category,
       p.price,
       RANK() OVER (
         PARTITION BY p.category ORDER BY p.price DESC
       ) AS price_rank,
       DENSE_RANK() OVER (
         PARTITION BY p.category ORDER BY p.price DESC
       ) AS dense_price_rank
FROM products AS p
ORDER BY p.category, p.price DESC, p.product_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Return the three highest-priced products per category, including price ties.
-- Why: Compute `DENSE_RANK` in a CTE and filter outside.
-- Expected: At least three price levels per category where available.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH ranked AS (
  SELECT p.*,
         DENSE_RANK() OVER (
           PARTITION BY p.category ORDER BY p.price DESC
         ) AS price_rank
  FROM products AS p
)
SELECT product_id,
       name,
       category,
       price,
       price_rank
FROM ranked
WHERE price_rank <= 3
ORDER BY category, price_rank, product_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Compare row number, rank, and dense rank on values 100, 100, and 90.
-- Why: Use a deterministic ID only for row number; adding it to rank ordering would destroy the tie.
-- Expected: Three rows showing sequences 1/2/3, 1/1/3, and 1/1/2.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT sample_id,
       score,
       ROW_NUMBER() OVER (ORDER BY score DESC, sample_id) AS row_number_value,
       RANK() OVER (ORDER BY score DESC) AS rank_value,
       DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank_value
FROM (VALUES (1, 100), (2, 100), (3, 90)) AS sample(sample_id, score)
ORDER BY sample_id;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Return exactly one latest order per customer even when timestamps tie.
-- Why: Use row number with the unique order ID as final tie-breaker.
-- Expected: At most one row per customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH numbered AS (
  SELECT o.*,
         ROW_NUMBER() OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date DESC, o.order_id DESC
         ) AS recency_number
  FROM orders AS o
)
SELECT order_id,
       customer_id,
       order_date,
       total_amount
FROM numbered
WHERE recency_number = 1
ORDER BY customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Rank employee salaries within department and show only the top two distinct salary levels.
-- Why: Dense rank includes all employees tied at either of the top two salary values.
-- Expected: Top two salary levels per department.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH ranked AS (
  SELECT e.*,
         DENSE_RANK() OVER (
           PARTITION BY e.department_id ORDER BY e.salary DESC
         ) AS salary_rank
  FROM employees AS e
)
SELECT employee_id,
       full_name,
       department_id,
       salary,
       salary_rank
FROM ranked
WHERE salary_rank <= 2
ORDER BY department_id, salary_rank, employee_id;

-- No course answer persists changes or temporary objects.
ROLLBACK;
