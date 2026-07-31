-- Day 33: Index Optimization Strategies (composite, covering, partial)
-- BEGINNER WORKFLOW — sql-33: Index Optimization Strategies
-- Guide: sql/postgres-60day/companion-guides/day33_index_optimization_strategies.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-33/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Composite index where predicates use (customer_id, order_date)
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- Covering index (Postgres INCLUDE) for frequent query on order_items
CREATE INDEX idx_oi_order_product_inc ON order_items(order_id, product_id) INCLUDE (quantity, unit_price, discount);

-- Partial index for an active subset. Partial-index predicates must be
-- immutable, so a moving expression such as now() - interval '90 days' is
-- not valid in PostgreSQL.
CREATE INDEX idx_orders_open
  ON orders(order_date)
  WHERE status IN ('placed', 'paid');

-- Test with EXPLAIN
EXPLAIN ANALYZE
SELECT o.order_id, o.order_date
FROM orders o
WHERE o.customer_id = 1 AND o.order_date >= now() - interval '365 days';

EXPLAIN ANALYZE
SELECT oi.order_id, oi.product_id, oi.quantity
FROM order_items oi
WHERE oi.order_id IN (
  SELECT order_id
  FROM orders
  WHERE status IN ('placed', 'paid')
    AND order_date >= now() - interval '90 days'
);

-- Exercises
-- 1. Add a composite index for (category, created_at) on products and test.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Create a partial index for high-value orders (total_amount > 1000) and test.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 3. Prediction: test the composite product index with created_at alone. Explain
--    why the leftmost category column affects how useful the index can be.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: build an INCLUDE index for a customer order-history query
--    that returns order_id, order_date, status, and total_amount.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: write a query whose WHERE clause does not imply the partial
--    index predicate. Compare it with a query that does and explain eligibility
--    separately from the planner's final cost choice.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 6. Edge case: query a nullable column (customers.segment) with IS NULL and
--    discuss whether a partial index for only NULL rows would be worthwhile.
--    Inputs: Use only the declared lesson objects (orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
