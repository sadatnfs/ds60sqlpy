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

- **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: Return normalized customer names and lowercase emails” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `original_name`, `trimmed_name`, `normalized_email`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 1: Query writing Prompt: Return normalized customer names and lowercase emails. Why: Use btrim for outer whitespace and lower for a declared case-normalized display value. Expected: One row per customer. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Extract the email domain and count customers by domain, preserving missing emails” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `email_domain`, `customer_count`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 2, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 2: Query writing Prompt: Extract the email domain and count customers by domain, preserving missing emails. Why: splitpart parses the second component; CASE keeps NULL distinct. Expected: One row per domain label. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - CASE: encodes ordered business conditions; the first true branch wins and ELSE defines the remainder. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 3 must make “Query writing: Create an ordered comma-separated list of department employee names” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `department_name`, `employees`, `d`, `e`.
- **Independent verification:** For Exercise 3, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `department_name`, `employees`, `d`, `e`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 3: Query writing Prompt: Create an ordered comma-separated list of department employee names. Why: Put ORDER BY inside stringagg so concatenation order is deliberate. Expected: One row per department. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - JOIN ... ON: combines relations and may multiply rows; the match predicate and each input's grain must agree. - GROUP BY: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `normalized_text`, `sample`.
- **Independent verification:** For Exercise 4, run the two forms over the identical rows in `customers`, `products`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 4: Prediction Prompt: Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled. Why: Use a POSIX whitespace class and the global regex flag. Expected: Three input/output rows. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - VALUES: constructs a small relation explicitly, which makes examples and expected cardinality inspectable. - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Debugging: Safely find customer names containing a literal percent or underscore rather than treating them as wildcards” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `wildcards`, `evidence`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 5, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 5: Debugging Prompt: Safely find customer names containing a literal percent or underscore rather than treating them as wildcards. Why: Escape wildcard characters and declare the escape character. Expected: Rows only when the literal character occurs. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - WHERE: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass. - pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** Exercise 6 must make “Extension: Parse the numeric suffix from names like Customer 42, returning NULL for nonmatching text” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `parsed_customer_number`, `c`.
- **Independent verification:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `parsed_customer_number`, `c`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 6: Extension Prompt: Parse the numeric suffix from names like Customer 42, returning NULL for nonmatching text. Why: Use a captured regex replacement only after a match predicate establishes the format. Expected: One row per customer with a numeric suffix. Review the selected keys, grain, NULL behavior, and ordering before treating the output as evidence. Clause-by-clause reading: - SELECT: defines the output columns at the query's final grain; aliases document the meaning of derived values. - FROM: establishes the starting relation and therefore the initial row grain. - CASE: encodes ordered business conditions; the first true branch wins and ELSE defines the remainder. - pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics. - ORDER BY: defines presentation or ranking order; a unique final key makes tied values deterministic.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
