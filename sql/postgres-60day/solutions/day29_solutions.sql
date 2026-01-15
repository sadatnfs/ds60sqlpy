-- Day 29 - Solutions: Pattern Matching (LIKE/ILIKE, SIMILAR TO, Regex)
-- Assumes: customers(email, full_name, country), products(sku, name), orders(...)

/*
Exercise 1) Extract country codes from freeform addresses with regex.
Assume customers has address_text with country code like '... [US]' at the end; adjust pattern as needed.
*/
SELECT customer_id,
       address_text,
       SUBSTRING(address_text FROM '\\[([A-Z]{2})\\]$') AS country_code
FROM customers
ORDER BY customer_id
LIMIT 200;

/*
Exercise 2) Create a trigram index on product name and compare ILIKE performance before/after.
*/
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX IF NOT EXISTS idx_products_name_trgm ON products USING gin (name gin_trgm_ops);
-- EXPLAIN ANALYZE SELECT * FROM products WHERE name ILIKE '%adapter%';

/*
Exercise 3) Write a validator for phone numbers with optional country codes.
E.164-like simple check: optional '+' then 8–15 digits. Use anchored regex for validation.
*/
SELECT phone,
       (phone ~ '^\\+?[0-9]{8,15}$') AS is_valid
FROM customers
ORDER BY is_valid DESC, phone
LIMIT 200;

/* Portable notes:
- Replace ILIKE with LOWER(col) LIKE LOWER(pattern) if ILIKE unavailable.
- For complex matching without regex, SIMILAR TO may work but is less powerful.
*/
