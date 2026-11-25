-- Day 29: Advanced Filtering & Pattern Matching
-- BEGINNER WORKFLOW - sql-29: Pattern Matching
-- Guide: sql/postgres-60day/companion-guides/day29_pattern_matching.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-29.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Choose literal, wildcard, or regular-expression matching from the text grammar and make case, escaping, and anchoring explicit.
-- Assumptions: PostgreSQL `LIKE` is case-sensitive, `ILIKE` is case-insensitive, and POSIX regex operators use `~`/`~*`. Collation can affect text behavior.
-- Pitfall: Leading wildcards can prevent ordinary b-tree use; unanchored or overly broad regex patterns can match more text than intended.
-- Predict row grain and NULL/order behavior before executing each example.
-- LIKE/ILIKE patterns
SELECT
  customer_id,
  full_name,
  email
FROM
  customers
WHERE
  email ILIKE '%@example.com' ESCAPE '\'
  AND full_name ILIKE 'customer %' ESCAPE '\'
ORDER BY
  customer_id
LIMIT 20;

-- Regex with ~ and ~*
SELECT
  product_id,
  name,
  category
FROM
  products
WHERE
  name ~ '^Product [0-9]{2,3}$'
ORDER BY
  product_id
LIMIT 20;

-- Full-text search (basic)
-- Ensure textsearch configs are available (Postgres built-in)
SELECT
  p.product_id,
  p.name
FROM
  products p
WHERE
  to_tsvector('english', p.name || ' ' || p.category) @@ to_tsquery('english', 'electronics | sports')
ORDER BY
  p.product_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Find customer names beginning with `Customer 1` case-insensitively.
--    Hint: `ILIKE 'Customer 1%'` uses `%` for any suffix.
--    Inputs: For sql-29 Exercise 1, read the 500 rows of `customers` and keep those whose `full_name` starts with `Customer 1` under the case-insensitive `ILIKE 'Customer 1%'` prefix test.
--    Expected result/shape: For sql-29 Exercise 1, expected output: exactly 111 rows, IDs 1, 10 through 19, and 100 through 199, because the prefix also matches longer numbers that start with 1. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
--    Verify: For sql-29 Exercise 1, confirm that `WHERE NOT full_name ILIKE 'Customer 1%'` returns the other 389 customers, and that case-sensitive `LIKE 'Customer 1%'` also returns 111 because every seeded name is capitalized the same way; then compare `'customer 1' ILIKE 'Customer 1%'` (true) with `'customer 1' LIKE 'Customer 1%'` (false), and note that `'Customer 21'` does not match.
--    Hint ladder, rung 1: For sql-29 Exercise 1, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
-- 2. [Query writing] Find emails that match the course's simple lowercase example.com pattern.
--    Hint: Anchor both ends and escape the literal dot in the POSIX regex.
--    Inputs: For sql-29 Exercise 2, read `customers` and keep rows whose `email` matches the case-sensitive regular expression `^customer[0-9]+@example[.]com$`, anchored at both ends with the dot written as `[.]`.
--    Expected result/shape: For sql-29 Exercise 2, expected output: exactly 500 rows, every customer from 1 to 500, since no seeded email is NULL or off-pattern. The final columns are `customer_id`, and `email`. The final order is `c.customer_id`.
--    Verify: For sql-29 Exercise 2, confirm that `WHERE email !~ '^customer[0-9]+@example[.]com$'` returns 0 rows; then test the pattern on literals: `'Customer7@example.com'` fails because `~` is case-sensitive, `'customer7@example.com.au'` fails because of `$`, and `'customer7@exampleXcom'` fails with `[.]` but matches if the dot is left unescaped.
--    Hint ladder, rung 1: For sql-29 Exercise 2, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
-- 3. [Query writing] Return event paths under `/p/` using JSON extraction and an anchored pattern.
--    Hint: Extract path text, then anchor the literal prefix.
--    Inputs: For sql-29 Exercise 3, read the 20000 `events` rows, extract `metadata ->> 'path'` as text, and keep paths that start with `/p/` under `LIKE '/p/%'`.
--    Expected result/shape: For sql-29 Exercise 3, expected output: exactly 6667 rows, event IDs from 1 to 19997, with only two distinct paths: `/p/1` (3333 rows) and `/p/2` (3334 rows). The final columns are `event_id`, and `path`. The final order is `e.event_id`.
--    Verify: For sql-29 Exercise 3, confirm with `SELECT metadata ->> 'path', COUNT(*) FROM events GROUP BY 1` that the other 13333 rows carry `/`, `/cart`, `/help`, or `/search` and none has a NULL path; then check the prefix rule on literals: `'/p/'` matches, while `'/p'`, `'/P/1'`, and `'/shop/p/1'` do not.
--    Hint ladder, rung 1: For sql-29 Exercise 3, inspect the source keys that survive `WHERE`; then check `e.event_id` before applying the row cap.
-- 4. [Prediction] Match literal percent and underscore characters in sample text and contrast them with wildcard behavior.
--    Hint: Declare an escape character and prefix each literal wildcard.
--    Inputs: For sql-29 Exercise 4, no table is read: the inline `VALUES` fixture holds `'100%'`, `'a_b'`, and `'plain'`, and the filter uses `LIKE '%\%%' ESCAPE '\'` and `LIKE '%\_%' ESCAPE '\'` so the escaped `%` and `_` are literal characters.
--    Expected result/shape: For sql-29 Exercise 4, expected output: exactly 2 rows, `100%` and `a_b`; `plain` is filtered out. The final columns are `value`. The final order is `value`.
--    Verify: For sql-29 Exercise 4, confirm 2 rows, then remove the escapes and confirm that `value LIKE '%%%' OR value LIKE '%_%'` returns all 3 rows, because unescaped `%` and `_` are wildcards; adding `'ab'`, `'50 percent'`, and `'a\b'` to the fixture still returns only the original 2 rows.
--    Hint ladder, rung 1: For sql-29 Exercise 4, inspect the source keys that survive `WHERE`; then check `value` before applying the row cap.
-- 5. [Debugging] Extract the captured numeric suffix from a valid customer name without replacing the entire string blindly.
--    Hint: First assert the anchored grammar, then use `substring(... FROM regex)`.
--    Inputs: For sql-29 Exercise 5, read from `customers`, keep only names that match the anchored pattern `^Customer [0-9]+$`, and extract the number with `substring(full_name FROM '^Customer ([0-9]+)$')::integer`.
--    Expected result/shape: For sql-29 Exercise 5, expected output: exactly 500 rows, one per customer, with `name_number` running from 1 to 500. The final columns are `customer_id`, and `name_number`. The final order is `c.customer_id`.
--    Verify: For sql-29 Exercise 5, confirm 500 rows, because every seeded name matches, and that `name_number` equals `customer_id` on every row; the same `substring` returns NULL for `'Customer 12a'` and 7 for `'Customer 7'`.
--    Hint ladder, rung 1: For sql-29 Exercise 5, run the `WHERE full_name ~ '^Customer [0-9]+$'` filter alone and count the matches before you add the extraction.
-- 6. [Extension] Classify emails as course example, other valid-looking, missing, or malformed using ordered patterns.
--    Hint: Handle NULL first, then most specific anchored pattern, then a bounded general pattern.
--    Inputs: For sql-29 Exercise 6, read from `customers` and classify each `email` with ordered `CASE` branches: `missing` for NULL, `course_example` for an address at `example.com`, `other_valid_looking` for any other `name@domain.tld`, otherwise `malformed`.
--    Expected result/shape: For sql-29 Exercise 6, expected output: exactly 500 rows, one per customer, all labeled `course_example` in this seed, so the `missing`, `other_valid_looking`, and `malformed` branches are reached only by the fixture in the check. The final columns are `customer_id`, `email`, and `email_class`. The final order is `c.customer_id`.
--    Verify: For sql-29 Exercise 6, confirm 500 rows, one per customer, all `course_example` on the seed; then run the same `CASE` on `VALUES (NULL), ('ann@example.com'), ('ann@school.org'), ('ann@examplexcom'), ('not-an-email')` and expect `missing`, `course_example`, `other_valid_looking`, `malformed`, and `malformed`.
--    Hint ladder, rung 1: For sql-29 Exercise 6, test the `CASE` on the five sample values first; the `IS NULL` branch must come first and the `example[.]com` branch before the general one.
ROLLBACK;
