-- Day 1: SELECT, WHERE, ORDER BY, LIMIT
-- Focus: Query execution order and basic filtering/sorting

BEGIN;
SET search_path TO training, public;

-- Example 1: Select specific columns with filtering and sorting
SELECT customer_id, full_name, country, created_at
FROM customers
WHERE country IN ('US','CA')
ORDER BY created_at DESC
LIMIT 10;

-- Example 2: Derived column and alias
SELECT 
  product_id,
  name,
  price,
  cost,
  (price - cost) AS gross_margin
FROM products
WHERE price > 50
ORDER BY gross_margin DESC, price DESC
LIMIT 15;

-- Example 3: Basic filtering with patterns
SELECT *
FROM customers
WHERE email LIKE '%@example.com'
  AND full_name ILIKE 'customer %1_'
ORDER BY customer_id;

-- Exercises
-- 1) List the 20 newest orders with customer_id and total_amount.
-- 2) Find top 10 most expensive products created in the last 90 days.
-- 3) Show customers from GB or DE created within the last year, newest first.

ROLLBACK;
