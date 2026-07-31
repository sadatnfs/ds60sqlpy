# Day 12 solutions — String Functions and Text Processing


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day12_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day12_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Normalization, Delimiter, Regular expression. Its worked-model focus is:
Compare a raw email with lower(trim(email)). Use the normalized expression for duplicate grouping, but keep the original column visible so a reviewer can audit what changed. Explain why silently overwriting the raw value would lose evidence.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 1, read from `customers`. Build the answer toward `customer_id`, `original_name`, `trimmed_name`, and `normalized_email`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-12 Exercise 1, expected output: One row per customer. The final columns are `customer_id`, `original_name`, `trimmed_name`, and `normalized_email`. The final order is `c.customer_id`.
- **Independent verification:** For sql-12 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `original_name`, `trimmed_name`, and `normalized_email` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-12 Exercise 1, check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-12 Exercise 1, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`, `original_name`, `trimmed_name`, and `normalized_email` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-12 Exercise 1, the chosen form is justified by this lesson-specific rationale: Use `btrim` for outer whitespace and `lower` for a declared case-normalized display value. Evaluate another form against the concrete expected result (One row per customer) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 2, read from `customers`. Build the answer toward `email_domain`, and `customer_count`; keep `email_domain` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-12 Exercise 2, expected output: One row per domain label. The final columns are `email_domain`, and `customer_count`. The final order is `customer_count DESC, email_domain`.
- **Independent verification:** For sql-12 Exercise 2, independently aggregate `customers` by `email_domain`; require one output row for every distinct `email_domain` tuple and compare `customer_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customer_count` for the existing `email_domain` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-12 Exercise 2, confirm the groups are `email_domain`; then check `customer_count DESC, email_domain` before applying the row cap.
- **Clause check:** For sql-12 Exercise 2, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `email_domain`, and finish with `email_domain`, and `customer_count` ordered by `customer_count DESC, email_domain`.
- **Alternative/trade-off:** For sql-12 Exercise 2, the chosen form is justified by this lesson-specific rationale: `split_part` parses the second component; CASE keeps NULL distinct. Evaluate another form against the concrete expected result (One row per domain label) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `customer_count` for the existing `email_domain` tuple and verify the new tuple appears exactly once.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 3, read from `departments`, and `employees`. Build the answer toward `department_id`, `department_name`, and `employees`; keep `department_id`, and `name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-12 Exercise 3, expected output: One row per department. The final columns are `department_id`, `department_name`, and `employees`. The final order is `d.department_id`.
- **Independent verification:** For sql-12 Exercise 3, independently aggregate `departments`, and `employees` by `department_id`, and `name`; require one output row for every distinct `department_id`, and `name` tuple and compare `employees` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `employees` for the existing `department_id`, and `name` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-12 Exercise 3, start with the first relation in `departments`, and `employees`; after each join, record total rows and distinct `department_id`, and `name` so the exact fanout or loss is visible.
- **Clause check:** For sql-12 Exercise 3, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `departments`, and `employees`, preserve one row per `department_id`, and `name`, and finish with `department_id`, `department_name`, and `employees` ordered by `d.department_id`.
- **Alternative/trade-off:** For sql-12 Exercise 3, the chosen form is justified by this lesson-specific rationale: Put `ORDER BY` inside `string_agg` so concatenation order is deliberate. Evaluate another form against the concrete expected result (One row per department) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `employees` for the existing `department_id`, and `name` tuple and verify the new tuple appears exactly once.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `source_text`, and `normalized_text`; keep `source_text` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-12 Exercise 4, expected output: Three input/output rows. The final columns are `source_text`, and `normalized_text`.
- **Independent verification:** For sql-12 Exercise 4, reselect the returned keys directly from the source; require unique `source_text` where the expected grain is one row per key and confirm the projected `source_text`, and `normalized_text` against the inline `VALUES` fixture. Add one source row with a new `source_text`; verify the result gains exactly one row carrying that `source_text` value.
- **Intermediate relation check:** For sql-12 Exercise 4, select `source_text` from the inline `VALUES` fixture before adding derived columns.
- **Clause check:** For sql-12 Exercise 4, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `source_text`, and finish with `source_text`, and `normalized_text`.
- **Alternative/trade-off:** For sql-12 Exercise 4, the chosen form is justified by this lesson-specific rationale: Use a POSIX whitespace class and the global regex flag. Evaluate another form against the concrete expected result (Three input/output rows) and the verification above.
- **Edge case:** Add one source row with a new `source_text`; verify the result gains exactly one row carrying that `source_text` value.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 5, read from `customers`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-12 Exercise 5, expected output: Rows only when the literal character occurs. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
- **Independent verification:** For sql-12 Exercise 5, run an anti-check that counts rows where NOT ((c.full_name LIKE '%\%%' ESCAPE '\' OR c.full_name LIKE '%\_%' ESCAPE '\')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`. Add one row for which `(c.full_name LIKE '%\%%' ESCAPE '\' OR c.full_name LIKE '%\_%' ESCAPE '\')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
- **Intermediate relation check:** For sql-12 Exercise 5, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-12 Exercise 5, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`, and `full_name` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-12 Exercise 5, the chosen form is justified by this lesson-specific rationale: Escape wildcard characters and declare the escape character. Evaluate another form against the concrete expected result (Rows only when the literal character occurs) and the verification above.
- **Edge case:** Add one row for which `(c.full_name LIKE '%\%%' ESCAPE '\' OR c.full_name LIKE '%\_%' ESCAPE '\')` is true and one for which it is false; verify only the matching `customer_id` value is returned.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 6, read from `customers`. Build the answer toward `customer_id`, `full_name`, and `parsed_customer_number`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-12 Exercise 6, expected output: One row per customer with a numeric suffix. The final columns are `customer_id`, `full_name`, and `parsed_customer_number`. The final order is `c.customer_id`.
- **Independent verification:** For sql-12 Exercise 6, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `full_name`, and `parsed_customer_number` against `customers`. Repeat with `NULL` in `customer_id`, and `full_name` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-12 Exercise 6, check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-12 Exercise 6, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`, `full_name`, and `parsed_customer_number` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-12 Exercise 6, the chosen form is justified by this lesson-specific rationale: Use a captured regex replacement only after a match predicate establishes the format. Evaluate another form against the concrete expected result (One row per customer with a numeric suffix) and the verification above.
- **Edge case:** Repeat with `NULL` in `customer_id`, and `full_name` and state whether the row is kept, rejected, or classified.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
