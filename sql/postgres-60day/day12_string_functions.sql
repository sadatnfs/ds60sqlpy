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
--    Inputs: For sql-12 Exercise 1, read `full_name` and `email` from the 500 `customers` rows, wrapping the name in `btrim` and the email in `lower`.
--    Expected result/shape: For sql-12 Exercise 1, return 500 rows, one per customer, from customer 1 (`Customer 1`, `customer1@example.com`) to customer 500; on the fixture no name has extra spaces and no email has uppercase letters, so the cleaned columns match the originals. The final columns are `customer_id`, `original_name`, `trimmed_name`, and `normalized_email`. The final order is `c.customer_id`.
--    Verify: For sql-12 Exercise 1, confirm 500 rows and 0 rows where `full_name <> btrim(full_name)` or `email <> lower(email)`. Inside a rolled-back transaction, set customer 1's name to `' Customer 1 '` and email to `Customer1@EXAMPLE.com`; the row must still show `Customer 1` and `customer1@example.com` in the cleaned columns.
--    Hint ladder, rung 1: For sql-12 Exercise 1, check `c.customer_id` before applying the row cap.
-- 2. [Query writing] Extract the email domain and count customers by domain, preserving missing emails.
--    Hint: `split_part` parses the second component; CASE keeps NULL distinct.
--    Inputs: For sql-12 Exercise 2, take the part of each `customers.email` after `@` with `split_part`, lower-case it, label a `NULL` email as `(missing)`, and count customers per resulting domain.
--    Expected result/shape: For sql-12 Exercise 2, return one row, `example.com` with 500 customers, because every fixture email uses that domain and none is `NULL`. The final columns are `email_domain`, and `customer_count`. The final order is `customer_count DESC, email_domain`.
--    Verify: For sql-12 Exercise 2, confirm the single count equals `SELECT COUNT(*) FROM customers` (500). Inside a rolled-back transaction, set customer 1's email to `Customer1@EXAMPLE.com` and customer 2's email to `NULL`; the result must become two rows, `example.com` 499 and `(missing)` 1, so the uppercase domain still groups with the rest.
--    Hint ladder, rung 1: For sql-12 Exercise 2, confirm the groups are `email_domain`; then check `customer_count DESC, email_domain` before applying the row cap.
-- 3. [Query writing] Create an ordered comma-separated list of department employee names.
--    Hint: Put `ORDER BY` inside `string_agg` so concatenation order is deliberate.
--    Inputs: For sql-12 Exercise 3, read from `departments` left-joined to `employees` and list each department's employee names with `string_agg(e.full_name, ', ' ORDER BY e.full_name, e.employee_id)`.
--    Expected result/shape: For sql-12 Exercise 3, return 6 rows, `Sales` through `Operations`; names are sorted as text, so department 1's list runs `Employee 1, Employee 13, Employee 19, ...` with `Employee 7` after `Employee 67`. The final columns are `department_id`, `department_name`, and `employees`. The final order is `d.department_id`.
--    Verify: For sql-12 Exercise 3, confirm 6 rows, one per `department_id`, matching `SELECT COUNT(*) FROM departments`; for one department, compare the number of names in `employees` with `SELECT COUNT(*) FROM employees WHERE department_id = <that id>` (17 for departments 1 to 4 and 16 for departments 5 and 6).
--    Hint ladder, rung 1: For sql-12 Exercise 3, start from `departments`, `LEFT JOIN` employees, and check that grouping by `department_id` and `name` still returns 6 rows.
-- 4. [Prediction] Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled.
--    Hint: Use a POSIX whitespace class and the global regex flag.
--    Inputs: For sql-12 Exercise 4, normalize three strings in an inline `VALUES` fixture (`Data Tools` with two spaces on each side and three between the words, `E'one\ttwo'`, and `E'line1\nline2'`) with `regexp_replace(source_text, '[[:space:]]+', ' ', 'g')` wrapped in `btrim`.
--    Expected result/shape: For sql-12 Exercise 4, return 3 rows with `normalized_text` values `Data Tools`, `one two`, and `line1 line2`; the query has no `ORDER BY`. The final columns are `source_text`, and `normalized_text`.
--    Verify: For sql-12 Exercise 4, confirm 3 rows with no tab, newline, or double space left in `normalized_text`. Change the pattern to `' +'` and the tab row must come back unchanged; drop `btrim` and the first row must keep one space at each end of `Data Tools`.
--    Hint ladder, rung 1: For sql-12 Exercise 4, select `source_text` from the inline `VALUES` fixture before adding derived columns.
-- 5. [Debugging] Safely find customer names containing a literal percent or underscore rather than treating them as wildcards.
--    Hint: Escape wildcard characters and declare the escape character.
--    Inputs: For sql-12 Exercise 5, search the 500 `customers.full_name` values for a literal `%` or `_` with `LIKE '%\%%' ESCAPE '\'` and `LIKE '%\_%' ESCAPE '\'`.
--    Expected result/shape: For sql-12 Exercise 5, return 0 rows, because every fixture name has the form `Customer N`. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
--    Verify: For sql-12 Exercise 5, confirm the unescaped pattern `LIKE '%_%'` matches all 500 names, because `_` alone is a one-character wildcard. Inside a rolled-back transaction, rename customer 3 to `Customer_3`; the escaped query must return exactly that 1 row.
--    Hint ladder, rung 1: For sql-12 Exercise 5, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
-- 6. [Extension] Parse the numeric suffix from names like `Customer 42`, returning NULL for nonmatching text.
--    Hint: Use a captured regex replacement only after a match predicate establishes the format.
--    Inputs: For sql-12 Exercise 6, test each of the 500 `customers.full_name` values against `'^Customer [0-9]+$'` and, only when it matches, cast `substring(full_name FROM '([0-9]+)$')` to `integer`.
--    Expected result/shape: For sql-12 Exercise 6, return 500 rows, one per customer, where `parsed_customer_number` equals `customer_id`, from 1 to 500. The final columns are `customer_id`, `full_name`, and `parsed_customer_number`. The final order is `c.customer_id`.
--    Verify: For sql-12 Exercise 6, confirm 500 rows where `parsed_customer_number = customer_id`. Inside a rolled-back transaction, rename customer 3 to `Customer_3` and customer 4 to `Customer 4b`; both rows must stay in the result with a `NULL` `parsed_customer_number` instead of raising a cast error.
--    Hint ladder, rung 1: For sql-12 Exercise 6, check `c.customer_id` before applying the row cap.
ROLLBACK;
