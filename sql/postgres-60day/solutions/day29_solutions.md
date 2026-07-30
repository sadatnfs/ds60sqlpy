# Day 29 solutions — Pattern Matching: LIKE/ILIKE, SIMILAR TO, and Regular Expressions

These answers align one-for-one with [day29_pattern_matching.sql](../day29_pattern_matching.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Choose literal, wildcard, or regular-expression matching from the text grammar and make case, escaping, and anchoring explicit.
- **Assumptions:** PostgreSQL `LIKE` is case-sensitive, `ILIKE` is case-insensitive, and POSIX regex operators use `~`/`~*`. Collation can affect text behavior.
- **Primary pitfall:** Leading wildcards can prevent ordinary b-tree use; unanchored or overly broad regex patterns can match more text than intended.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Find customer names beginning with `Customer 1` case-insensitively.

**Reasoning:** `ILIKE 'Customer 1%'` uses `%` for any suffix.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name
FROM customers AS c
WHERE c.full_name ILIKE 'Customer 1%'
ORDER BY c.customer_id;
```

**Expected shape:** Matching customer rows in stable ID order.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Find emails that match the course's simple lowercase example.com pattern.

**Reasoning:** Anchor both ends and escape the literal dot in the POSIX regex.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.email
FROM customers AS c
WHERE c.email ~ '^customer[0-9]+@example[.]com$'
ORDER BY c.customer_id;
```

**Expected shape:** Only matching non-null email rows.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Return event paths under `/p/` using JSON extraction and an anchored pattern.

**Reasoning:** Extract path text, then anchor the literal prefix.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT e.event_id,
       e.metadata ->> 'path' AS path
FROM events AS e
WHERE e.metadata ->> 'path' LIKE '/p/%'
ORDER BY e.event_id;
```

**Expected shape:** Events whose path begins `/p/`.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Match literal percent and underscore characters in sample text and contrast them with wildcard behavior.

**Reasoning:** Declare an escape character and prefix each literal wildcard.

**Clause-by-clause reading:**

- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT value
FROM (VALUES ('100%'), ('a_b'), ('plain')) AS sample(value)
WHERE value LIKE '%\%%' ESCAPE '\'
   OR value LIKE '%\_%' ESCAPE '\'
ORDER BY value;
```

**Expected shape:** Only the two rows containing the requested literal symbols.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Extract the captured numeric suffix from a valid customer name without replacing the entire string blindly.

**Reasoning:** First assert the anchored grammar, then use `substring(... FROM regex)`.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       substring(c.full_name FROM '^Customer ([0-9]+)$')::integer AS name_number
FROM customers AS c
WHERE c.full_name ~ '^Customer [0-9]+$'
ORDER BY c.customer_id;
```

**Expected shape:** One row per valid course customer name.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Classify emails as course example, other valid-looking, missing, or malformed using ordered patterns.

**Reasoning:** Handle NULL first, then most specific anchored pattern, then a bounded general pattern.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
- pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
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
```

**Expected shape:** One row per customer with one classification.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
