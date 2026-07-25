-- Day 32 solutions: index fundamentals
BEGIN;
SET search_path TO training, public;

-- Exercise 1: create and test an index on products(category).
CREATE INDEX idx_products_category_solution ON products(category);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, name, price
FROM products
WHERE category = 'Electronics';

-- Exercise 2: compare the plan without and with the course-owned index.
DROP INDEX idx_products_category_solution;

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, name, price
FROM products
WHERE category = 'Electronics';

CREATE INDEX idx_products_category_solution ON products(category);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, name, price
FROM products
WHERE category = 'Electronics';

-- On a 300-row table PostgreSQL may rationally choose a sequential scan.
ROLLBACK;
