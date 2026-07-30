-- Day 12: String functions
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
-- 2. [Query writing] Extract the email domain and count customers by domain, preserving missing emails.
--    Hint: `split_part` parses the second component; CASE keeps NULL distinct.
-- 3. [Query writing] Create an ordered comma-separated list of department employee names.
--    Hint: Put `ORDER BY` inside `string_agg` so concatenation order is deliberate.
-- 4. [Prediction] Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled.
--    Hint: Use a POSIX whitespace class and the global regex flag.
-- 5. [Debugging] Safely find customer names containing a literal percent or underscore rather than treating them as wildcards.
--    Hint: Escape wildcard characters and declare the escape character.
-- 6. [Extension] Parse the numeric suffix from names like `Customer 42`, returning NULL for nonmatching text.
--    Hint: Use a captured regex replacement only after a match predicate establishes the format.

ROLLBACK;
