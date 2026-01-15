# Day 29 — Solutions (Pattern Matching: LIKE/ILIKE, SIMILAR TO, Regex)

We compare text pattern tools in PostgreSQL, from simple LIKE/ILIKE to SIMILAR TO and full regular expressions (~, ~*, !~, !~*). We also discuss escaping, indexes, and practical extraction with regex groups.

Setup
- Tables: customers(full_name, email), products(name, sku), orders(...)
- Operators:
  - LIKE: case-sensitive wildcard match (% any-length, _ single char)
  - ILIKE: case-insensitive (Postgres extension)
  - SIMILAR TO: SQL-standard regex-like (limited); use full regex instead when possible
  - ~, ~*: POSIX regex match (case-sensitive/sensitive*, * means case-insensitive)

Exercise 1 — Find customer emails by domain and safe escaping
```sql
-- Simple: all customers with gmail.com (case-insensitive)
SELECT customer_id, email
FROM customers
WHERE email ILIKE '%@gmail.com';

-- Escape a literal % or _ in LIKE search
-- e.g., search for '100% Organic' product names literally
SELECT product_id, name
FROM products
WHERE name LIKE '%100\% Organic%' ESCAPE '\';
```
Notes
- ILIKE is convenient but may need trigram index for speed (see performance section)
- In LIKE, % and _ are wildcards; escape them when you want literal characters

Exercise 2 — Prefix vs infix searches and index usage
```sql
-- Prefix search can use btree index with text_pattern_ops or default in many cases
-- names starting with 'App'
SELECT product_id, name
FROM products
WHERE name LIKE 'App%'
ORDER BY name
LIMIT 50;

-- Infix search (contains anywhere) generally needs pg_trgm for index acceleration
-- names containing 'wireless'
SELECT product_id, name
FROM products
WHERE name ILIKE '%wireless%'
LIMIT 50;
```
Performance
- Prefix LIKE 'foo%' may use btree (especially with appropriate collation/opclass); but '%foo%' will not
- For infix/ILIKE, add pg_trgm index: `CREATE EXTENSION IF NOT EXISTS pg_trgm;`
  - `CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_name_trgm ON products USING gin (name gin_trgm_ops);`

Exercise 3 — Full regex with capture groups and validation
```sql
-- Extract local and domain from emails using regex SUBSTRING (first capture)
SELECT customer_id,
       email,
       SUBSTRING(email FROM '^(.*?)@')          AS local_part,
       SUBSTRING(email FROM '@(.*)$')           AS domain
FROM customers
WHERE email ~* '^[^@]+@[^@]+\.[^@]+$'  -- basic email shape (very permissive)
LIMIT 100;

-- Validate SKU pattern like ABC-1234 (three letters, dash, four digits)
SELECT sku
FROM products
WHERE sku ~ '^[A-Z]{3}-[0-9]{4}$'
LIMIT 100;
```
Explanation
- ~ is regex match; ~* is case-insensitive match; !~ and !~* are negations
- SUBSTRING(string FROM 'regex') returns the first capture group (or full match if no capture). Use additional parentheses to capture specific parts.

Exercise 4 — SIMILAR TO vs regex
```sql
-- SIMILAR TO is SQL-standard but limited; prefer regex when available
SELECT sku
FROM products
WHERE sku SIMILAR TO '[A-Z]{3}-[0-9]{4}'  -- works, but regex ~ is more flexible
LIMIT 50;
```
Caveats
- SIMILAR TO’s syntax and escaping can be surprising; if you need real regex features, use ~/~* instead

Anti-patterns and tips
- Don’t lower() both sides repeatedly in WHERE; prefer ILIKE or computed/generated columns with indexes
- For heavy regex filtering, consider materialized columns (e.g., domain extracted from email) with ordinary indexes
- Use anchors ^ and $ to avoid unintended substring matches when you need whole-string checks
