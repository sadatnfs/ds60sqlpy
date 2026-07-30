-- Day 04 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.
-- Assumptions: Missing matches appear as NULL-extended columns. Decide whether absence means zero, unknown, or an exception before applying `COALESCE`.
-- Pitfall: A right-side predicate in `WHERE` can turn a left join into an inner join; put match-qualification predicates in `ON` when unmatched left rows must remain.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: List every customer with order count, including customers with zero orders.
-- Why: Start from customers, left join orders, and count the nullable order key rather than `COUNT(*)`.
-- Expected: One row per customer; zero is visible.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name,
       COUNT(o.order_id) AS order_count
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY order_count DESC, c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Find products that have never appeared in an order item.
-- Why: Left join and retain rows where the right-side primary key is NULL.
-- Expected: One row per unsold product.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT p.product_id,
       p.name,
       p.category
FROM products AS p
LEFT JOIN order_items AS oi
  ON oi.product_id = p.product_id
WHERE oi.order_item_id IS NULL
ORDER BY p.product_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Compare monthly budgets and expenses by category with a full outer join.
-- Why: Aggregate each side to the same category/month grain before joining; preserve keys from either side.
-- Expected: One row per category/month present in either source.
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
WITH expense_months AS (
  SELECT e.category,
         date_trunc('month', e.expense_date)::date AS period,
         SUM(e.amount) AS actual_amount
  FROM expenses AS e
  GROUP BY e.category, date_trunc('month', e.expense_date)
), budget_months AS (
  SELECT b.category,
         b.period,
         SUM(b.amount) AS budget_amount
  FROM budgets AS b
  GROUP BY b.category, b.period
)
SELECT COALESCE(bm.category, em.category) AS category,
       COALESCE(bm.period, em.period) AS period,
       ROUND(bm.budget_amount, 2) AS budget_amount,
       ROUND(em.actual_amount, 2) AS actual_amount
FROM budget_months AS bm
FULL JOIN expense_months AS em
  ON em.category = bm.category
 AND em.period = bm.period
ORDER BY period, category;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Preserve every customer while counting only delivered orders; compare a status predicate in `ON` with the same predicate in `WHERE`.
-- Why: Place `o.status = 'delivered'` in `ON`; `WHERE` would remove NULL-extended customers.
-- Expected: One row per customer, including zero delivered orders.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name,
       COUNT(o.order_id) AS delivered_orders
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
 AND o.status = 'delivered'
GROUP BY c.customer_id, c.full_name
ORDER BY delivered_orders DESC, c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Repair `COUNT(*)` in a left-join order count so customers without orders report zero rather than one.
-- Why: Count a non-nullable right-side key that becomes NULL for an unmatched row.
-- Expected: One row per customer with correct zero counts.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       COUNT(o.order_id) AS order_count
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
GROUP BY c.customer_id
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys.
-- Why: Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero.
-- Expected: One summary row with three mutually interpretable counts.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
SELECT COUNT(DISTINCT p.product_id) FILTER (
         WHERE p.product_id IS NOT NULL AND oi.product_id IS NOT NULL
       ) AS matched_products,
       COUNT(DISTINCT p.product_id) FILTER (
         WHERE p.product_id IS NOT NULL AND oi.product_id IS NULL
       ) AS unsold_products,
       COUNT(DISTINCT oi.product_id) FILTER (
         WHERE p.product_id IS NULL AND oi.product_id IS NOT NULL
       ) AS orphan_item_product_ids
FROM products AS p
FULL JOIN order_items AS oi
  ON oi.product_id = p.product_id;

-- No course answer persists changes or temporary objects.
ROLLBACK;
