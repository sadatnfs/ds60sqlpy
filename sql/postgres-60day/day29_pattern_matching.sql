-- Day 29: Advanced Filtering & Pattern Matching
-- BEGINNER WORKFLOW — sql-29: Pattern Matching
-- Guide: sql/postgres-60day/companion-guides/day29_pattern_matching.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-29/ copy, and prints the full
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
--    Inputs: Use only the declared lesson objects (customers, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 2. [Query writing] Find emails that match the course's simple lowercase example.com pattern.
--    Hint: Anchor both ends and escape the literal dot in the POSIX regex.
--    Inputs: Use only the declared lesson objects (customers, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 3. [Query writing] Return event paths under `/p/` using JSON extraction and an anchored pattern.
--    Hint: Extract path text, then anchor the literal prefix.
--    Inputs: Use only the declared lesson objects (customers, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 4. [Prediction] Match literal percent and underscore characters in sample text and contrast them with wildcard behavior.
--    Hint: Declare an escape character and prefix each literal wildcard.
--    Inputs: Use only the declared lesson objects (customers, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 5. [Debugging] Extract the captured numeric suffix from a valid customer name without replacing the entire string blindly.
--    Hint: First assert the anchored grammar, then use `substring(... FROM regex)`.
--    Inputs: Use only the declared lesson objects (customers, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
-- 6. [Extension] Classify emails as course example, other valid-looking, missing, or malformed using ordered patterns.
--    Hint: Handle NULL first, then most specific anchored pattern, then a bounded general pattern.
--    Inputs: Use only the declared lesson objects (customers, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.

ROLLBACK;
