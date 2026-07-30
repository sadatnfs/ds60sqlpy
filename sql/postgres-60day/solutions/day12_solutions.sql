-- Day 12 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Normalize and parse text with explicit locale/case assumptions, preserving original values when a transformation may be lossy.
-- Assumptions: Course emails use one `@`; Unicode/collation behavior can vary. Text ordering is deterministic only with an explicit sort and tie-breaker.
-- Pitfall: Regex is not a complete email or HTML parser; leading-wildcard searches may not use a normal b-tree index.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Return normalized customer names and lowercase emails.
-- Why: Use `btrim` for outer whitespace and `lower` for a declared case-normalized display value.
-- Expected: One row per customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name AS original_name,
       btrim(c.full_name) AS trimmed_name,
       lower(c.email) AS normalized_email
FROM customers AS c
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Extract the email domain and count customers by domain, preserving missing emails.
-- Why: `split_part` parses the second component; CASE keeps NULL distinct.
-- Expected: One row per domain label.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT CASE
         WHEN c.email IS NULL THEN '(missing)'
         ELSE lower(split_part(c.email, '@', 2))
       END AS email_domain,
       COUNT(*) AS customer_count
FROM customers AS c
GROUP BY email_domain
ORDER BY customer_count DESC, email_domain;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Create an ordered comma-separated list of department employee names.
-- Why: Put `ORDER BY` inside `string_agg` so concatenation order is deliberate.
-- Expected: One row per department.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT d.department_id,
       d.name AS department_name,
       string_agg(e.full_name, ', ' ORDER BY e.full_name, e.employee_id) AS employees
FROM departments AS d
LEFT JOIN employees AS e
  ON e.department_id = d.department_id
GROUP BY d.department_id, d.name
ORDER BY d.department_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled.
-- Why: Use a POSIX whitespace class and the global regex flag.
-- Expected: Three input/output rows.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
SELECT source_text,
       btrim(regexp_replace(source_text, '[[:space:]]+', ' ', 'g')) AS normalized_text
FROM (VALUES
  ('  Data   Tools  '),
  (E'one\ttwo'),
  (E'line1\nline2')
) AS sample(source_text);

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Safely find customer names containing a literal percent or underscore rather than treating them as wildcards.
-- Why: Escape wildcard characters and declare the escape character.
-- Expected: Rows only when the literal character occurs.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name
FROM customers AS c
WHERE c.full_name LIKE '%\%%' ESCAPE '\'
   OR c.full_name LIKE '%\_%' ESCAPE '\'
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Parse the numeric suffix from names like `Customer 42`, returning NULL for nonmatching text.
-- Why: Use a captured regex replacement only after a match predicate establishes the format.
-- Expected: One row per customer with a numeric suffix.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
-- - pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name,
       CASE
         WHEN c.full_name ~ '^Customer [0-9]+$'
           THEN substring(c.full_name FROM '([0-9]+)$')::integer
         ELSE NULL
       END AS parsed_customer_number
FROM customers AS c
ORDER BY c.customer_id;

-- No course answer persists changes or temporary objects.
ROLLBACK;
