-- Day 08 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.
-- Assumptions: A scalar subquery returning no rows becomes NULL; more than one row is an error. Order a `LIMIT 1` subquery deterministically.
-- Pitfall: Adding `LIMIT 1` to hide an unintended multi-row result creates arbitrary logic unless `ORDER BY` defines the chosen row.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Return orders whose total exceeds the overall average order total.
-- Why: The aggregate subquery is guaranteed to return exactly one value.
-- Expected: Order rows above the global average.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.customer_id,
       o.total_amount
FROM orders AS o
WHERE o.total_amount > (
  SELECT AVG(all_orders.total_amount)
  FROM orders AS all_orders
)
ORDER BY o.total_amount DESC, o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Add the total customer count as a scalar column beside each country-level customer count.
-- Why: An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.
-- Expected: One row per country with a common global total.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.country,
       COUNT(*) AS country_customers,
       (SELECT COUNT(*) FROM customers) AS all_customers
FROM customers AS c
GROUP BY c.country
ORDER BY country_customers DESC, c.country;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Show each customer with their latest order timestamp using a scalar correlated subquery.
-- Why: Use `MAX` to guarantee one result and let customers without orders receive NULL.
-- Expected: One row per customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name,
       (
         SELECT MAX(o.order_date)
         FROM orders AS o
         WHERE o.customer_id = c.customer_id
       ) AS latest_order_date
FROM customers AS c
ORDER BY latest_order_date DESC NULLS LAST, c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Demonstrate that a scalar subquery with no matching rows returns NULL.
-- Why: Use a deliberately impossible product key and test the scalar result with `IS NULL`.
-- Expected: One row whose boolean result is true.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
SELECT (
         SELECT p.price
         FROM products AS p
         WHERE p.product_id = -1
       ) IS NULL AS no_row_becomes_null;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Repair a scalar subquery that returns many product prices by aggregating to the intended single value.
-- Why: Choose the business reduction explicitly; this answer uses maximum price.
-- Expected: One row per category with a scalar global maximum for comparison.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT p.category,
       MAX(p.price) AS category_max_price,
       (SELECT MAX(all_products.price) FROM products AS all_products) AS global_max_price
FROM products AS p
GROUP BY p.category
ORDER BY p.category;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report.
-- Why: Compute the global total once, then cross join the guaranteed one-row relation.
-- Expected: One row per country with country share.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH global AS (
  SELECT COUNT(*)::numeric AS customer_count
  FROM customers
)
SELECT c.country,
       COUNT(*) AS country_customers,
       ROUND(COUNT(*) / NULLIF(global.customer_count, 0), 4) AS customer_share
FROM customers AS c
CROSS JOIN global
GROUP BY c.country, global.customer_count
ORDER BY customer_share DESC, c.country;

-- No course answer persists changes or temporary objects.
ROLLBACK;
