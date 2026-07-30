-- Day 29 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Choose literal, wildcard, or regular-expression matching from the text grammar and make case, escaping, and anchoring explicit.
-- Assumptions: PostgreSQL `LIKE` is case-sensitive, `ILIKE` is case-insensitive, and POSIX regex operators use `~`/`~*`. Collation can affect text behavior.
-- Pitfall: Leading wildcards can prevent ordinary b-tree use; unanchored or overly broad regex patterns can match more text than intended.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Find customer names beginning with `Customer 1` case-insensitively.
-- Why: `ILIKE 'Customer 1%'` uses `%` for any suffix.
-- Expected: Matching customer rows in stable ID order.
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
WHERE c.full_name ILIKE 'Customer 1%'
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Find emails that match the course's simple lowercase example.com pattern.
-- Why: Anchor both ends and escape the literal dot in the POSIX regex.
-- Expected: Only matching non-null email rows.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.email
FROM customers AS c
WHERE c.email ~ '^customer[0-9]+@example[.]com$'
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Return event paths under `/p/` using JSON extraction and an anchored pattern.
-- Why: Extract path text, then anchor the literal prefix.
-- Expected: Events whose path begins `/p/`.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT e.event_id,
       e.metadata ->> 'path' AS path
FROM events AS e
WHERE e.metadata ->> 'path' LIKE '/p/%'
ORDER BY e.event_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Match literal percent and underscore characters in sample text and contrast them with wildcard behavior.
-- Why: Declare an escape character and prefix each literal wildcard.
-- Expected: Only the two rows containing the requested literal symbols.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT value
FROM (VALUES ('100%'), ('a_b'), ('plain')) AS sample(value)
WHERE value LIKE '%\%%' ESCAPE '\'
   OR value LIKE '%\_%' ESCAPE '\'
ORDER BY value;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Extract the captured numeric suffix from a valid customer name without replacing the entire string blindly.
-- Why: First assert the anchored grammar, then use `substring(... FROM regex)`.
-- Expected: One row per valid course customer name.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       substring(c.full_name FROM '^Customer ([0-9]+)$')::integer AS name_number
FROM customers AS c
WHERE c.full_name ~ '^Customer [0-9]+$'
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Classify emails as course example, other valid-looking, missing, or malformed using ordered patterns.
-- Why: Handle NULL first, then most specific anchored pattern, then a bounded general pattern.
-- Expected: One row per customer with one classification.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
-- - pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.email,
       CASE
         WHEN c.email IS NULL THEN 'missing'
         WHEN c.email ~* '^[a-z0-9._%+-]+@example[.]com$' THEN 'course_example'
         WHEN c.email ~* '^[a-z0-9._%+-]+@[a-z0-9.-]+[.][a-z]{2,}$' THEN 'other_valid_looking'
         ELSE 'malformed'
       END AS email_class
FROM customers AS c
ORDER BY c.customer_id;

-- No course answer persists changes or temporary objects.
ROLLBACK;
