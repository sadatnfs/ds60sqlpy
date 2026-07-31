# Day 29 solutions — Pattern Matching: LIKE/ILIKE, SIMILAR TO, and Regular Expressions


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day29_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day29_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Wildcard, Anchor, Sargable predicate. Its worked-model focus is:
Compare email ~ 'customer1[0-9]{2}' with the anchored email ~ '^customer1[0-9]{2}@example\\.com$'. Add surrounding text to a test value and show why an unanchored validation can accept only a matching substring.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 1, read from `customers`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-29 Exercise 1, expected output: Matching customer rows in stable ID order. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
- **Independent verification:** For sql-29 Exercise 1, run an anti-check that counts rows where NOT ((c.full_name ILIKE 'Customer 1%')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`. Add one row for which `(c.full_name ILIKE 'Customer 1%')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
- **Intermediate relation check:** For sql-29 Exercise 1, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-29 Exercise 1, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`, and `full_name` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-29 Exercise 1, the chosen form is justified by this lesson-specific rationale: `ILIKE 'Customer 1%'` uses `%` for any suffix. Evaluate another form against the concrete expected result (Matching customer rows in stable ID order) and the verification above.
- **Edge case:** Add one row for which `(c.full_name ILIKE 'Customer 1%')` is true and one for which it is false; verify only the matching `customer_id` value is returned.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 2, read from `customers`. Build the answer toward `customer_id`, and `email`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-29 Exercise 2, expected output: Only matching non-null email rows. The final columns are `customer_id`, and `email`. The final order is `c.customer_id`.
- **Independent verification:** For sql-29 Exercise 2, run an anti-check that counts rows where NOT ((c.email ~ '^customer[0-9]+@example[.]com$')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `email` against `customers`. Add one row for which `(c.email ~ '^customer[0-9]+@example[.]com$')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
- **Intermediate relation check:** For sql-29 Exercise 2, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-29 Exercise 2, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`, and `email` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-29 Exercise 2, the chosen form is justified by this lesson-specific rationale: Anchor both ends and escape the literal dot in the POSIX regex. Evaluate another form against the concrete expected result (Only matching non-null email rows) and the verification above.
- **Edge case:** Add one row for which `(c.email ~ '^customer[0-9]+@example[.]com$')` is true and one for which it is false; verify only the matching `customer_id` value is returned.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 3, read from `events`. Build the answer toward `event_id`, and `path`; keep `event_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-29 Exercise 3, expected output: Events whose path begins `/p/`. The final columns are `event_id`, and `path`. The final order is `e.event_id`.
- **Independent verification:** For sql-29 Exercise 3, run an anti-check that counts rows where NOT ((e.metadata ->> 'path' LIKE '/p/%')); require unique `event_id` where the expected grain is one row per key and confirm the projected `event_id`, and `path` against `events`. Add one row for which `(e.metadata ->> 'path' LIKE '/p/%')` is true and one for which it is false; verify only the matching `event_id` value is returned.
- **Intermediate relation check:** For sql-29 Exercise 3, inspect the source keys that survive `WHERE`; then check `e.event_id` before applying the row cap.
- **Clause check:** For sql-29 Exercise 3, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `events`, preserve one row per `event_id`, and finish with `event_id`, and `path` ordered by `e.event_id`.
- **Alternative/trade-off:** For sql-29 Exercise 3, the chosen form is justified by this lesson-specific rationale: Extract path text, then anchor the literal prefix. Evaluate another form against the concrete expected result (Events whose path begins `/p/`) and the verification above.
- **Edge case:** Add one row for which `(e.metadata ->> 'path' LIKE '/p/%')` is true and one for which it is false; verify only the matching `event_id` value is returned.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `value`; keep `value` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-29 Exercise 4, expected output: Only the two rows containing the requested literal symbols. The final columns are `value`. The final order is `value`.
- **Independent verification:** For sql-29 Exercise 4, run an anti-check that counts rows where NOT ((value LIKE '%\%%' ESCAPE '\' OR value LIKE '%\_%' ESCAPE '\')); require unique `value` where the expected grain is one row per key and confirm the projected `value` against the inline `VALUES` fixture. Add one row for which `(value LIKE '%\%%' ESCAPE '\' OR value LIKE '%\_%' ESCAPE '\')` is true and one for which it is false; verify only the matching `value` value is returned.
- **Intermediate relation check:** For sql-29 Exercise 4, inspect the source keys that survive `WHERE`; then check `value` before applying the row cap.
- **Clause check:** For sql-29 Exercise 4, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `value`, and finish with `value` ordered by `value`.
- **Alternative/trade-off:** For sql-29 Exercise 4, the chosen form is justified by this lesson-specific rationale: Declare an escape character and prefix each literal wildcard. Evaluate another form against the concrete expected result (Only the two rows containing the requested literal symbols) and the verification above.
- **Edge case:** Add one row for which `(value LIKE '%\%%' ESCAPE '\' OR value LIKE '%\_%' ESCAPE '\')` is true and one for which it is false; verify only the matching `value` value is returned.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 5, read from `customers`. Compute `customer_id`, and `name_number` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-29 Exercise 5, expected output: One row per valid course customer name. The final columns are `customer_id`, and `name_number`. The final order is `c.customer_id`.
- **Independent verification:** For sql-29 Exercise 5, evaluate each of `name_number` in a separate control `SELECT` over `customers` using `(c.full_name ~ '^Customer [0-9]+$')`; require one final row and compare every value. Add one row for which `(c.full_name ~ '^Customer [0-9]+$')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
- **Intermediate relation check:** For sql-29 Exercise 5, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-29 Exercise 5, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve exactly one summary row, and finish with `customer_id`, and `name_number` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-29 Exercise 5, the chosen form is justified by this lesson-specific rationale: First assert the anchored grammar, then use `substring(... FROM regex)`. Evaluate another form against the concrete expected result (One row per valid course customer name) and the verification above.
- **Edge case:** Add one row for which `(c.full_name ~ '^Customer [0-9]+$')` is true and one for which it is false; verify only the matching `customer_id` value is returned.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 6, read from `customers`. Compute `customer_id`, `email`, and `email_class` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-29 Exercise 6, expected output: One row per customer with one classification. The final columns are `customer_id`, `email`, and `email_class`. The final order is `c.customer_id`.
- **Independent verification:** For sql-29 Exercise 6, evaluate each of `email`, and `email_class` in a separate control `SELECT` over `customers`; require one final row and compare every value. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-29 Exercise 6, check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-29 Exercise 6, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve exactly one summary row, and finish with `customer_id`, `email`, and `email_class` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-29 Exercise 6, the chosen form is justified by this lesson-specific rationale: Handle NULL first, then most specific anchored pattern, then a bounded general pattern. Evaluate another form against the concrete expected result (One row per customer with one classification) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
