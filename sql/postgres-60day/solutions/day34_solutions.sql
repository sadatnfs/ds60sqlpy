-- Day 34 solutions: query optimization
-- SOLUTION READING MAP for sql-34: Query Optimization Techniques
-- Explanation: sql/postgres-60day/solutions/day34_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day34_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
BEGIN;
SET search_path TO training, public;

-- Exercise 1: compare an EXISTS subquery with a DISTINCT join.
EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  o.order_id,
  o.order_date
FROM
  orders o
WHERE
  EXISTS (
    SELECT
      1
    FROM
      order_items oi
      JOIN products p ON p.product_id = oi.product_id
    WHERE
      oi.order_id = o.order_id
      AND p.category = 'Electronics');

-- DISTINCT is needed in the join form because one order could hold several
-- Electronics lines.
EXPLAIN (
  ANALYZE,
  BUFFERS
) SELECT DISTINCT
  o.order_id,
  o.order_date
FROM
  orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
WHERE
  p.category = 'Electronics';

-- Exercise 2: compare joining every order before LIMIT...
EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  o.order_id,
  o.order_date,
  c.country
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
ORDER BY
  o.order_date DESC,
  o.order_id DESC
LIMIT 100;

-- ...with keeping the 100 newest orders before joining customers.
-- Both return the same 100 rows; measure which one does less work.
EXPLAIN (
  ANALYZE,
  BUFFERS
) WITH top_orders AS MATERIALIZED (
  SELECT
    order_id,
    customer_id,
    order_date
  FROM
    orders
  ORDER BY
    order_date DESC,
    order_id DESC
  LIMIT 100
)
SELECT
  t.order_id,
  t.order_date,
  c.country
FROM
  top_orders t
  JOIN customers c ON c.customer_id = t.customer_id
ORDER BY
  t.order_date DESC,
  t.order_id DESC;

-- Exercise 3: MATERIALIZED creates an optimization boundary; NOT MATERIALIZED
-- permits the CTE to be folded into its single parent query.
EXPLAIN WITH recent AS MATERIALIZED (
  SELECT
    order_id,
    customer_id
  FROM
    orders
  WHERE
    order_date >= CURRENT_TIMESTAMP - interval '30 days'
)
SELECT
  COUNT(*)
FROM
  recent
  JOIN customers USING (customer_id);

EXPLAIN WITH recent AS NOT MATERIALIZED (
  SELECT
    order_id,
    customer_id
  FROM
    orders
  WHERE
    order_date >= CURRENT_TIMESTAMP - interval '30 days'
)
SELECT
  COUNT(*)
FROM
  recent
  JOIN customers USING (customer_id);

-- Exercise 4: reduce items to one row per order before crossing the next grain.
WITH item_totals AS (
  SELECT
    order_id,
    SUM(quantity) AS units
  FROM
    order_items
  GROUP BY
    order_id
)
SELECT
  c.country,
  SUM(it.units) AS units
FROM
  item_totals it
  JOIN orders o USING (order_id)
  JOIN customers c USING (customer_id)
GROUP BY
  c.country
ORDER BY
  c.country;

-- Exercise 5: aggregate each independent many-side to order grain. Joining raw
-- payments and items would multiply both amounts.
WITH paid AS (
  SELECT
    order_id,
    SUM(amount) AS paid_amount
  FROM
    payments
  GROUP BY
    order_id
),
sold AS (
  SELECT
    order_id,
    SUM(quantity * unit_price * (1 - discount)) AS line_revenue
  FROM
    order_items
  GROUP BY
    order_id
)
SELECT
  o.order_id,
  p.paid_amount,
  s.line_revenue
FROM
  orders o
  LEFT JOIN paid p USING (order_id)
  LEFT JOIN sold s USING (order_id)
ORDER BY
  o.order_id
LIMIT 20;

-- Exercise 6: NOT EXISTS remains two-valued for each customer even if the
-- subquery's projected expression could contain NULL.
SELECT
  c.customer_id
FROM
  customers c
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      orders o
    WHERE
      o.customer_id = c.customer_id)
ORDER BY
  c.customer_id;

ROLLBACK;
