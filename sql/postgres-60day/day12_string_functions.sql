-- Day 12: String functions
BEGIN;
SET search_path TO training, public;

-- Clean emails and extract domains
SELECT customer_id,
       email,
       lower(trim(email)) AS email_clean,
       split_part(email, '@', 2) AS domain
FROM customers
ORDER BY customer_id
LIMIT 50;

-- Replace and substring
SELECT product_id,
       name,
       replace(name, 'Product', 'Item') AS renamed,
       substr(name, 1, 10) AS short_name
FROM products
LIMIT 50;

-- Exercises
-- 1) Normalize country codes to upper-case and trim whitespace.
-- 2) Build a concatenated "full label" for products: "<category> - <name> ($<price>)".

ROLLBACK;
