-- Day 29: Advanced Filtering & Pattern Matching
BEGIN;
SET search_path TO training, public;

-- LIKE/ILIKE patterns
SELECT * FROM customers
WHERE email ILIKE '%@example.com'
  AND full_name ILIKE 'customer %'
LIMIT 20;

-- Regex with ~ and ~*
SELECT * FROM products
WHERE name ~ 'Product [0-9]{2,3}'
LIMIT 20;

-- Full-text search (basic)
-- Ensure textsearch configs are available (Postgres built-in)
SELECT p.product_id, p.name
FROM products p
WHERE to_tsvector('english', p.name || ' ' || p.category) @@ to_tsquery('english', 'electronics | sports');

-- Exercises
-- 1) Find customers whose emails start with 'customer1' followed by 2 digits using regex.
-- 2) Full-text search: products matching both 'home' and 'product'.

ROLLBACK;
