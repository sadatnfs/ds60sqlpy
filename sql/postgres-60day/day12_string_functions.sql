-- Day 12: String functions
-- BEGINNER WORKFLOW — sql-12: String Functions
-- Guide: sql/postgres-60day/companion-guides/day12_string_functions.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-12/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
ORDER BY product_id
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return normalized customer names and lowercase emails.
--    Hint: Use `btrim` for outer whitespace and `lower` for a declared case-normalized display value.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 returns a table-shaped answer to “Query writing: Return normalized customer names and lowercase emails” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `original_name`, `trimmed_name`, `normalized_email`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Use btrim for outer whitespace and lower for a declared case-normalized display value.
-- 2. [Query writing] Extract the email domain and count customers by domain, preserving missing emails.
--    Hint: `split_part` parses the second component; CASE keeps NULL distinct.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Query writing: Extract the email domain and count customers by domain, preserving missing emails” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `email_domain`, `customer_count`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: splitpart parses the second component; CASE keeps NULL distinct.
-- 3. [Query writing] Create an ordered comma-separated list of department employee names.
--    Hint: Put `ORDER BY` inside `string_agg` so concatenation order is deliberate.
--    Inputs: Use `departments`, `employees` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 must make “Query writing: Create an ordered comma-separated list of department employee names” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `department_name`, `employees`, `d`, `e`.
--    Verify: For Exercise 3, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `department_name`, `employees`, `d`, `e`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Put ORDER BY inside stringagg so concatenation order is deliberate.
-- 4. [Prediction] Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled.
--    Hint: Use a POSIX whitespace class and the global regex flag.
--    Inputs: Use `customers`, `products` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Prediction: Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `normalized_text`, `sample`.
--    Verify: For Exercise 4, run the two forms over the identical rows in `customers`, `products`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Start with the guide's first rung: Use a POSIX whitespace class and the global regex flag.
-- 5. [Debugging] Safely find customer names containing a literal percent or underscore rather than treating them as wildcards.
--    Hint: Escape wildcard characters and declare the escape character.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 returns a table-shaped answer to “Debugging: Safely find customer names containing a literal percent or underscore rather than treating them as wildcards” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `wildcards`, `evidence`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 5, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Start with the guide's first rung: Escape wildcard characters and declare the escape character.
-- 6. [Extension] Parse the numeric suffix from names like `Customer 42`, returning NULL for nonmatching text.
--    Hint: Use a captured regex replacement only after a match predicate establishes the format.
--    Inputs: Use `customers` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Extension: Parse the numeric suffix from names like Customer 42, returning NULL for nonmatching text” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `parsed_customer_number`, `c`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `parsed_customer_number`, `c`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: Start with the guide's first rung: Use a captured regex replacement only after a match predicate establishes the format.

ROLLBACK;
