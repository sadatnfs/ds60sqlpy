-- Day 12: String functions
-- BEGINNER WORKFLOW - sql-12: String Functions
-- Guide: sql/postgres-60day/companion-guides/day12_string_functions.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-12.
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
-- Focus: Normalize and parse text with explicit locale/case assumptions, preserving original values when a transformation may be lossy.
-- Assumptions: Course emails use one `@`; Unicode/collation behavior can vary. Text ordering is deterministic only with an explicit sort and tie-breaker.
-- Pitfall: Regex is not a complete email or HTML parser; leading-wildcard searches may not use a normal b-tree index.
-- Predict row grain and NULL/order behavior before executing each example.
-- Clean emails and extract domains
SELECT
  customer_id,
  email,
  lower(trim(email)) AS email_clean,
  split_part(email, '@', 2) AS domain
FROM
  customers
ORDER BY
  customer_id
LIMIT 50;

-- Replace and substring
SELECT
  product_id,
  name,
  replace(name, 'Product', 'Item') AS renamed,
  substr(name, 1, 10) AS short_name
FROM
  products
ORDER BY
  product_id
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return normalized customer names and lowercase emails.
--    Hint: Use `btrim` for outer whitespace and `lower` for a declared case-normalized display value.
--    Inputs: For sql-12 Exercise 1, read from `customers`. Build the answer toward `customer_id`, `original_name`, `trimmed_name`, and `normalized_email`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-12 Exercise 1, expected output: One row per customer. The final columns are `customer_id`, `original_name`, `trimmed_name`, and `normalized_email`. The final order is `c.customer_id`.
--    Verify: For sql-12 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `original_name`, `trimmed_name`, and `normalized_email` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-12 Exercise 1, check `c.customer_id` before applying the row cap.
-- 2. [Query writing] Extract the email domain and count customers by domain, preserving missing emails.
--    Hint: `split_part` parses the second component; CASE keeps NULL distinct.
--    Inputs: For sql-12 Exercise 2, read from `customers`. Build the answer toward `email_domain`, and `customer_count`; keep `email_domain` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-12 Exercise 2, expected output: One row per domain label. The final columns are `email_domain`, and `customer_count`. The final order is `customer_count DESC, email_domain`.
--    Verify: For sql-12 Exercise 2, independently aggregate `customers` by `email_domain`; require one output row for every distinct `email_domain` tuple and compare `customer_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customer_count` for the existing `email_domain` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-12 Exercise 2, confirm the groups are `email_domain`; then check `customer_count DESC, email_domain` before applying the row cap.
-- 3. [Query writing] Create an ordered comma-separated list of department employee names.
--    Hint: Put `ORDER BY` inside `string_agg` so concatenation order is deliberate.
--    Inputs: For sql-12 Exercise 3, read from `departments` left-joined to `employees` and list each department's employee names with `string_agg(e.full_name, ', ' ORDER BY e.full_name, e.employee_id)`.
--    Expected result/shape: For sql-12 Exercise 3, expected output: One row per department. The final columns are `department_id`, `department_name`, and `employees`. The final order is `d.department_id`.
--    Verify: For sql-12 Exercise 3, confirm 6 rows, one per `department_id`, matching `SELECT COUNT(*) FROM departments`; for one department, compare the number of names in `employees` with `SELECT COUNT(*) FROM employees WHERE department_id = <that id>` (17 for departments 1 to 4 and 16 for departments 5 and 6).
--    Hint ladder, rung 1: For sql-12 Exercise 3, start from `departments`, `LEFT JOIN` employees, and check that grouping by `department_id` and `name` still returns 6 rows.
-- 4. [Prediction] Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled.
--    Hint: Use a POSIX whitespace class and the global regex flag.
--    Inputs: For sql-12 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `source_text`, and `normalized_text`; keep `source_text` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-12 Exercise 4, expected output: Three input/output rows. The final columns are `source_text`, and `normalized_text`.
--    Verify: For sql-12 Exercise 4, reselect the returned keys directly from the source; require unique `source_text` where the expected grain is one row per key and confirm the projected `source_text`, and `normalized_text` against the inline `VALUES` fixture. Add one source row with a new `source_text`; verify the result gains exactly one row carrying that `source_text` value.
--    Hint ladder, rung 1: For sql-12 Exercise 4, select `source_text` from the inline `VALUES` fixture before adding derived columns.
-- 5. [Debugging] Safely find customer names containing a literal percent or underscore rather than treating them as wildcards.
--    Hint: Escape wildcard characters and declare the escape character.
--    Inputs: For sql-12 Exercise 5, read from `customers`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-12 Exercise 5, expected output: Rows only when the literal character occurs. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
--    Verify: For sql-12 Exercise 5, run an anti-check that counts rows where NOT ((c.full_name LIKE '%\%%' ESCAPE '\' OR c.full_name LIKE '%\_%' ESCAPE '\')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`. Add one row for which `(c.full_name LIKE '%\%%' ESCAPE '\' OR c.full_name LIKE '%\_%' ESCAPE '\')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
--    Hint ladder, rung 1: For sql-12 Exercise 5, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
-- 6. [Extension] Parse the numeric suffix from names like `Customer 42`, returning NULL for nonmatching text.
--    Hint: Use a captured regex replacement only after a match predicate establishes the format.
--    Inputs: For sql-12 Exercise 6, read from `customers`. Build the answer toward `customer_id`, `full_name`, and `parsed_customer_number`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-12 Exercise 6, expected output: One row per customer with a numeric suffix. The final columns are `customer_id`, `full_name`, and `parsed_customer_number`. The final order is `c.customer_id`.
--    Verify: For sql-12 Exercise 6, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `full_name`, and `parsed_customer_number` against `customers`. Repeat with `NULL` in `customer_id`, and `full_name` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-12 Exercise 6, check `c.customer_id` before applying the row cap.
ROLLBACK;
