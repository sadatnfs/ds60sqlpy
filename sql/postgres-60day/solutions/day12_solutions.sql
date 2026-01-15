-- Day 12 - Solutions: String Functions and Text Processing
-- Assumes: customers(email, full_name), products(name, sku)

/*
Exercise 1) Build a normalized_customer_email column and check duplicates.
Why: Normalize case/whitespace before dedup; use LOWER(TRIM(email)).
*/
SELECT LOWER(TRIM(email)) AS normalized_email,
       COUNT(*) AS cnt
FROM customers
GROUP BY LOWER(TRIM(email))
HAVING COUNT(*) > 1
ORDER BY cnt DESC, normalized_email
LIMIT 200;

/*
Exercise 2) Extract TLD from email domain and analyze distribution.
Why: Use SPLIT_PART and LOWER to standardize.
*/
SELECT LOWER(SPLIT_PART(email, '.', 2)) AS tld,
       COUNT(*) AS cnt
FROM (
  SELECT SPLIT_PART(LOWER(TRIM(email)), '@', 2) AS domain
  FROM customers
) d
GROUP BY LOWER(SPLIT_PART(domain, '.', 2))
ORDER BY cnt DESC
LIMIT 50;

/*
Exercise 3) Use trigram similarity to find near-duplicate product names.
Why: pg_trgm provides similarity(); use a threshold and ORDER BY similarity DESC.
Note: Requires CREATE EXTENSION pg_trgm;
*/
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
SELECT p1.product_id, p1.name AS name_a,
       p2.product_id, p2.name AS name_b,
       similarity(p1.name, p2.name) AS sim
FROM products p1
JOIN products p2 ON p1.product_id < p2.product_id
WHERE similarity(p1.name, p2.name) > 0.7
ORDER BY sim DESC, p1.product_id
LIMIT 200;

-- End of Day 12 solutions
