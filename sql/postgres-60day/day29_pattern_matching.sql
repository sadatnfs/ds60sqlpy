-- Day 29: Advanced Filtering & Pattern Matching
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Choose literal, wildcard, or regular-expression matching from the text grammar and make case, escaping, and anchoring explicit.
-- Assumptions: PostgreSQL `LIKE` is case-sensitive, `ILIKE` is case-insensitive, and POSIX regex operators use `~`/`~*`. Collation can affect text behavior.
-- Pitfall: Leading wildcards can prevent ordinary b-tree use; unanchored or overly broad regex patterns can match more text than intended.
-- Predict row grain and NULL/order behavior before executing each example.

-- LIKE/ILIKE patterns
SELECT customer_id, full_name, email
FROM customers
WHERE email ILIKE '%@example.com' ESCAPE '\'
  AND full_name ILIKE 'customer %' ESCAPE '\'
ORDER BY customer_id
LIMIT 20;

-- Regex with ~ and ~*
SELECT product_id, name, category
FROM products
WHERE name ~ '^Product [0-9]{2,3}$'
ORDER BY product_id
LIMIT 20;

-- Full-text search (basic)
-- Ensure textsearch configs are available (Postgres built-in)
SELECT p.product_id, p.name
FROM products p
WHERE to_tsvector('english', p.name || ' ' || p.category)
      @@ to_tsquery('english', 'electronics | sports')
ORDER BY p.product_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Find customer names beginning with `Customer 1` case-insensitively.
--    Hint: `ILIKE 'Customer 1%'` uses `%` for any suffix.
-- 2. [Query writing] Find emails that match the course's simple lowercase example.com pattern.
--    Hint: Anchor both ends and escape the literal dot in the POSIX regex.
-- 3. [Query writing] Return event paths under `/p/` using JSON extraction and an anchored pattern.
--    Hint: Extract path text, then anchor the literal prefix.
-- 4. [Prediction] Match literal percent and underscore characters in sample text and contrast them with wildcard behavior.
--    Hint: Declare an escape character and prefix each literal wildcard.
-- 5. [Debugging] Extract the captured numeric suffix from a valid customer name without replacing the entire string blindly.
--    Hint: First assert the anchored grammar, then use `substring(... FROM regex)`.
-- 6. [Extension] Classify emails as course example, other valid-looking, missing, or malformed using ordered patterns.
--    Hint: Handle NULL first, then most specific anchored pattern, then a bounded general pattern.

ROLLBACK;
