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
--    Inputs: For sql-29 Exercise 1, read from `customers`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-29 Exercise 1, expected output: Matching customer rows in stable ID order. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
--    Verify: For sql-29 Exercise 1, run an anti-check that counts rows where NOT ((c.full_name ILIKE 'Customer 1%')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`. Add one row for which `(c.full_name ILIKE 'Customer 1%')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
--    Hint ladder, rung 1: For sql-29 Exercise 1, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
-- 2. [Query writing] Find emails that match the course's simple lowercase example.com pattern.
--    Hint: Anchor both ends and escape the literal dot in the POSIX regex.
--    Inputs: For sql-29 Exercise 2, read from `customers`. Build the answer toward `customer_id`, and `email`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-29 Exercise 2, expected output: Only matching non-null email rows. The final columns are `customer_id`, and `email`. The final order is `c.customer_id`.
--    Verify: For sql-29 Exercise 2, run an anti-check that counts rows where NOT ((c.email ~ '^customer[0-9]+@example[.]com$')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `email` against `customers`. Add one row for which `(c.email ~ '^customer[0-9]+@example[.]com$')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
--    Hint ladder, rung 1: For sql-29 Exercise 2, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
-- 3. [Query writing] Return event paths under `/p/` using JSON extraction and an anchored pattern.
--    Hint: Extract path text, then anchor the literal prefix.
--    Inputs: For sql-29 Exercise 3, read from `events`. Build the answer toward `event_id`, and `path`; keep `event_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-29 Exercise 3, expected output: Events whose path begins `/p/`. The final columns are `event_id`, and `path`. The final order is `e.event_id`.
--    Verify: For sql-29 Exercise 3, run an anti-check that counts rows where NOT ((e.metadata ->> 'path' LIKE '/p/%')); require unique `event_id` where the expected grain is one row per key and confirm the projected `event_id`, and `path` against `events`. Add one row for which `(e.metadata ->> 'path' LIKE '/p/%')` is true and one for which it is false; verify only the matching `event_id` value is returned.
--    Hint ladder, rung 1: For sql-29 Exercise 3, inspect the source keys that survive `WHERE`; then check `e.event_id` before applying the row cap.
-- 4. [Prediction] Match literal percent and underscore characters in sample text and contrast them with wildcard behavior.
--    Hint: Declare an escape character and prefix each literal wildcard.
--    Inputs: For sql-29 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `value`; keep `value` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-29 Exercise 4, expected output: Only the two rows containing the requested literal symbols. The final columns are `value`. The final order is `value`.
--    Verify: For sql-29 Exercise 4, run an anti-check that counts rows where NOT ((value LIKE '%\%%' ESCAPE '\' OR value LIKE '%\_%' ESCAPE '\')); require unique `value` where the expected grain is one row per key and confirm the projected `value` against the inline `VALUES` fixture. Add one row for which `(value LIKE '%\%%' ESCAPE '\' OR value LIKE '%\_%' ESCAPE '\')` is true and one for which it is false; verify only the matching `value` value is returned.
--    Hint ladder, rung 1: For sql-29 Exercise 4, inspect the source keys that survive `WHERE`; then check `value` before applying the row cap.
-- 5. [Debugging] Extract the captured numeric suffix from a valid customer name without replacing the entire string blindly.
--    Hint: First assert the anchored grammar, then use `substring(... FROM regex)`.
--    Inputs: For sql-29 Exercise 5, read from `customers`, keep only names that match the anchored pattern `^Customer [0-9]+$`, and extract the number with `substring(full_name FROM '^Customer ([0-9]+)$')::integer`.
--    Expected result/shape: For sql-29 Exercise 5, expected output: One row per valid course customer name. The final columns are `customer_id`, and `name_number`. The final order is `c.customer_id`.
--    Verify: For sql-29 Exercise 5, confirm 500 rows, because every seeded name matches, and that `name_number` equals `customer_id` on every row; the same `substring` returns NULL for `'Customer 12a'` and 7 for `'Customer 7'`.
--    Hint ladder, rung 1: For sql-29 Exercise 5, run the `WHERE full_name ~ '^Customer [0-9]+$'` filter alone and count the matches before you add the extraction.
-- 6. [Extension] Classify emails as course example, other valid-looking, missing, or malformed using ordered patterns.
--    Hint: Handle NULL first, then most specific anchored pattern, then a bounded general pattern.
--    Inputs: For sql-29 Exercise 6, read from `customers` and classify each `email` with ordered `CASE` branches: `missing` for NULL, `course_example` for an address at `example.com`, `other_valid_looking` for any other `name@domain.tld`, otherwise `malformed`.
--    Expected result/shape: For sql-29 Exercise 6, expected output: One row per customer with one classification. The final columns are `customer_id`, `email`, and `email_class`. The final order is `c.customer_id`.
--    Verify: For sql-29 Exercise 6, confirm 500 rows, one per customer, all `course_example` on the seed; then run the same `CASE` on `VALUES (NULL), ('ann@example.com'), ('ann@school.org'), ('ann@examplexcom'), ('not-an-email')` and expect `missing`, `course_example`, `other_valid_looking`, `malformed`, and `malformed`.
--    Hint ladder, rung 1: For sql-29 Exercise 6, test the `CASE` on the five sample values first; the `IS NULL` branch must come first and the `example[.]com` branch before the general one.
ROLLBACK;
