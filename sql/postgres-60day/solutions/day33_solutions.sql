-- Day 33 solutions: index optimization strategies
BEGIN;
SET search_path TO training, public;

-- Exercise 1: equality first, range second in a composite index.
CREATE INDEX idx_products_category_created_solution
  ON products(category, created_at);

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, name, created_at
FROM products
WHERE category = 'Home'
  AND created_at >= CURRENT_TIMESTAMP - interval '1 year'
ORDER BY created_at;

-- Exercise 2: a compact partial index for only high-value orders.
CREATE INDEX idx_orders_high_value_solution
  ON orders(total_amount, order_date)
  WHERE total_amount > 1000;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, order_date, total_amount
FROM orders
WHERE total_amount > 1000
  AND order_date >= CURRENT_TIMESTAMP - interval '90 days'
ORDER BY total_amount DESC;

ROLLBACK;
