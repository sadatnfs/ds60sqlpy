# Day 12 solutions — String Functions and Text Processing

These answers align one-for-one with [day12_string_functions.sql](../day12_string_functions.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Normalize and parse text with explicit locale/case assumptions, preserving original values when a transformation may be lossy.
- **Assumptions:** Course emails use one `@`; Unicode/collation behavior can vary. Text ordering is deterministic only with an explicit sort and tie-breaker.
- **Primary pitfall:** Regex is not a complete email or HTML parser; leading-wildcard searches may not use a normal b-tree index.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Return normalized customer names and lowercase emails.

**Reasoning:** Use `btrim` for outer whitespace and `lower` for a declared case-normalized display value.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name AS original_name,
       btrim(c.full_name) AS trimmed_name,
       lower(c.email) AS normalized_email
FROM customers AS c
ORDER BY c.customer_id;
```

**Expected shape:** One row per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Extract the email domain and count customers by domain, preserving missing emails.

**Reasoning:** `split_part` parses the second component; CASE keeps NULL distinct.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT CASE
         WHEN c.email IS NULL THEN '(missing)'
         ELSE lower(split_part(c.email, '@', 2))
       END AS email_domain,
       COUNT(*) AS customer_count
FROM customers AS c
GROUP BY email_domain
ORDER BY customer_count DESC, email_domain;
```

**Expected shape:** One row per domain label.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Create an ordered comma-separated list of department employee names.

**Reasoning:** Put `ORDER BY` inside `string_agg` so concatenation order is deliberate.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT d.department_id,
       d.name AS department_name,
       string_agg(e.full_name, ', ' ORDER BY e.full_name, e.employee_id) AS employees
FROM departments AS d
LEFT JOIN employees AS e
  ON e.department_id = d.department_id
GROUP BY d.department_id, d.name
ORDER BY d.department_id;
```

**Expected shape:** One row per department.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Prediction

**Prompt:** Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled.

**Reasoning:** Use a POSIX whitespace class and the global regex flag.

**Clause-by-clause reading:**

- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.

```sql
SELECT source_text,
       btrim(regexp_replace(source_text, '[[:space:]]+', ' ', 'g')) AS normalized_text
FROM (VALUES
  ('  Data   Tools  '),
  (E'one\ttwo'),
  (E'line1\nline2')
) AS sample(source_text);
```

**Expected shape:** Three input/output rows.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Debugging

**Prompt:** Safely find customer names containing a literal percent or underscore rather than treating them as wildcards.

**Reasoning:** Escape wildcard characters and declare the escape character.

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
WHERE c.full_name LIKE '%\%%' ESCAPE '\'
   OR c.full_name LIKE '%\_%' ESCAPE '\'
ORDER BY c.customer_id;
```

**Expected shape:** Rows only when the literal character occurs.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Parse the numeric suffix from names like `Customer 42`, returning NULL for nonmatching text.

**Reasoning:** Use a captured regex replacement only after a match predicate establishes the format.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
- pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name,
       CASE
         WHEN c.full_name ~ '^Customer [0-9]+$'
           THEN substring(c.full_name FROM '([0-9]+)$')::integer
         ELSE NULL
       END AS parsed_customer_number
FROM customers AS c
ORDER BY c.customer_id;
```

**Expected shape:** One row per customer with a numeric suffix.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
