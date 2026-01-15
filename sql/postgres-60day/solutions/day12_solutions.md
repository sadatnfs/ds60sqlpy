# Day 12 — Solutions (String Functions and Text Processing)

We normalize emails for deduplication, extract top-level domains (TLDs), and detect near-duplicate product names with trigrams. Each block includes the reasoning and pitfalls.

Setup
- Schema: training; tables: customers(email, full_name), products(name, sku)
- Extensions: pg_trgm for similarity() if doing fuzzy matches

Exercise 1 — Normalize emails and find duplicates
```sql
SELECT LOWER(TRIM(email)) AS normalized_email,
       COUNT(*) AS cnt
FROM customers
GROUP BY LOWER(TRIM(email))
HAVING COUNT(*) > 1
ORDER BY cnt DESC, normalized_email
LIMIT 200;
```
Line-by-line
- TRIM removes leading/trailing whitespace; LOWER ensures case-insensitive grouping.
- GROUP BY the normalized value and HAVING > 1 surfaces duplicates.
- ORDER BY by count then email helps triage the worst offenders first.
Pitfalls
- Internal whitespace (e.g., 'foo  @bar.com') won’t be removed by TRIM alone; consider REGEXP_REPLACE(email, '\\s+', '', 'g') for aggressive cleanup when safe.
- Some domains treat dots as insignificant in local-part (e.g., Gmail). That normalization is domain-specific—document before applying.

Exercise 2 — Extract TLD distribution
```sql
SELECT LOWER(SPLIT_PART(email, '.', 2)) AS tld,
       COUNT(*) AS cnt
FROM (
  SELECT SPLIT_PART(LOWER(TRIM(email)), '@', 2) AS domain
  FROM customers
) d
GROUP BY LOWER(SPLIT_PART(domain, '.', 2))
ORDER BY cnt DESC
LIMIT 50;
```
Explanation
- Inner subquery extracts the domain (`after @`); the outer query takes the second dot-split piece as a naive TLD.
- Real domains can be multi-label (co.uk). For accuracy use a public suffix list or a dedicated library; this example illustrates string functions.
Tips
- SPLIT_PART is 1-based in Postgres.

Exercise 3 — Find near-duplicate product names (trigrams)
```sql
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
SELECT p1.product_id, p1.name AS name_a,
       p2.product_id, p2.name AS name_b,
       similarity(p1.name, p2.name) AS sim
FROM products p1
JOIN products p2 ON p1.product_id < p2.product_id
WHERE similarity(p1.name, p2.name) > 0.7
ORDER BY sim DESC, p1.product_id
LIMIT 200;
```
Why this way
- Self-join pairs names and enforces one direction (id < id) to avoid duplicates.
- similarity() > 0.7 is a starting threshold; tune per dataset. Consider ILIKE/LOWER around names if case varies.
Hardening
- Index support: CREATE INDEX ON products USING gin (name gin_trgm_ops) to accelerate similarity lookups.
- Pre-filter by first letter or length band for speed on very large catalogs.
