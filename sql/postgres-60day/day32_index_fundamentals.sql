-- Day 32: Index Fundamentals (B-tree, hash, basics)
-- BEGINNER WORKFLOW — sql-32: Index Fundamentals
-- Guide: sql/postgres-60day/companion-guides/day32_index_fundamentals.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-32/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Create simple indexes (demonstration; rolled back)
CREATE INDEX idx_orders_total_amount ON orders(total_amount);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_customers_country ON customers(country);

-- Observe plan changes
EXPLAIN ANALYZE SELECT order_id FROM orders WHERE total_amount > 500 LIMIT 100;
EXPLAIN ANALYZE SELECT * FROM orders WHERE order_date >= now() - interval '30 days';
EXPLAIN ANALYZE SELECT * FROM customers WHERE country = 'US';

-- Hash index example (not commonly needed; Postgres B-tree supports = well)
-- CREATE INDEX idx_customers_email_hash ON customers USING hash(email);

-- Exercises
-- 1. Create an index on products(category) and test a category filter.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 2. Drop vs create index and observe planner differences.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 3. Prediction: inspect category frequency first, then predict whether the
--    planner will prefer a sequential scan or the category index on this small
--    seed. Verify with EXPLAIN (ANALYZE, BUFFERS).
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: create a B-tree index on payments(payment_date), query a
--    bounded half-open date range, and identify its scan node.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 5. Debugging: run a filter with lower(country) = 'us'. Explain why the plain
--    country index may not match it, then create and test an expression index.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 6. Edge case: prove that an index does not provide a guaranteed output order
--    by contrasting a query without ORDER BY with one ordered explicitly.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
