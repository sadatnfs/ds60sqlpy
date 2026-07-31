# Day 12 — String Functions and Text Processing (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 11 — CASE expressions](day11_case_expressions.md)
- **Artifacts:** [learner SQL](../day12_string_functions.sql) ·
  [solution reasoning](../solutions/day12_solutions.md) ·
  [executable solution](../solutions/day12_solutions.sql)

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-12 — String Functions** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-12/lesson/workspace/sql/postgres-60day/day12_string_functions.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day12_string_functions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day12_string_functions.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Normalization, Delimiter, Regular expression. Its worked SQL reads or creates `customers`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Compare a raw email with lower(trim(email)). Use the normalized expression for duplicate grouping, but keep the original column visible so a reviewer can audit what changed. Explain why silently overwriting the raw value would lose evidence.
The expected contract is that One row per customer. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day12_string_functions.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT customer_id,
       email,
       lower(trim(email)) AS email_clean,
       split_part(email, '@', 2) AS domain
FROM customers
ORDER BY customer_id
LIMIT 50;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per customer.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT product_id,
       name,
       replace(name, 'Product', 'Item') AS renamed,
       substr(name, 1, 10) AS short_name
FROM products
ORDER BY product_id
LIMIT 50;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per customer.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Normalize, split, concatenate, replace, and extract text with explicit
  assumptions.
- Distinguish display cleanup from a safe persistent data-quality rule.

## Vocabulary and concepts

- **Normalization:** converting equivalent text forms to one comparison form.
- **Delimiter:** a character or string separating parts of a value.
- **Regular expression:** a pattern language for matching or replacing text.

## Worked example / walkthrough

Compare a raw email with `lower(trim(email))`. Use the normalized expression for
duplicate grouping, but keep the original column visible so a reviewer can
audit what changed. Explain why silently overwriting the raw value would lose
evidence.

## Practice assumptions and review method

- **Focus:** Normalize and parse text with explicit locale/case assumptions, preserving original values when a transformation may be lossy.
- **Assumptions:** Course emails use one `@`; Unicode/collation behavior can vary. Text ordering is deterministic only with an explicit sort and tie-breaker.
- **Failure to watch for:** Regex is not a complete email or HTML parser; leading-wildcard searches may not use a normal b-tree index.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Normalize and parse text with explicit locale/case assumptions, preserving original values when a transformation may be lossy.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Return normalized customer names and lowercase emails.
   **Progressive hint:** Use `btrim` for outer whitespace and `lower` for a declared case-normalized display value.
   **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: Return normalized customer names and lowercase emails” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `original_name`, `trimmed_name`, `normalized_email`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
2. **Query writing:** Extract the email domain and count customers by domain, preserving missing emails.
   **Progressive hint:** `split_part` parses the second component; CASE keeps NULL distinct.
   **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Extract the email domain and count customers by domain, preserving missing emails” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `email_domain`, `customer_count`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 2, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
3. **Query writing:** Create an ordered comma-separated list of department employee names.
   **Progressive hint:** Put `ORDER BY` inside `string_agg` so concatenation order is deliberate.
   **Expected result/shape:** Exercise 3 must make “Query writing: Create an ordered comma-separated list of department employee names” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `department_name`, `employees`, `d`, `e`.
   **Verify:** For Exercise 3, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `department_name`, `employees`, `d`, `e`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
4. **Prediction:** Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled.
   **Progressive hint:** Use a POSIX whitespace class and the global regex flag.
   **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `normalized_text`, `sample`.
   **Verify:** For Exercise 4, run the two forms over the identical rows in `customers`, `products`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
5. **Debugging:** Safely find customer names containing a literal percent or underscore rather than treating them as wildcards.
   **Progressive hint:** Escape wildcard characters and declare the escape character.
   **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Debugging: Safely find customer names containing a literal percent or underscore rather than treating them as wildcards” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `wildcards`, `evidence`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 5, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
6. **Extension:** Parse the numeric suffix from names like `Customer 42`, returning NULL for nonmatching text.
   **Progressive hint:** Use a captured regex replacement only after a match predicate establishes the format.
   **Expected result/shape:** Exercise 6 must make “Extension: Parse the numeric suffix from names like Customer 42, returning NULL for nonmatching text” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `parsed_customer_number`, `c`.
   **Verify:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `parsed_customer_number`, `c`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Regex is not a complete email or HTML parser; leading-wildcard searches may not use a normal b-tree index.
- **Unexpected row count:** display keys before aggregates, count rows after
  each join/filter stage, and find the first stage whose grain differs from the
  contract. Do not hide fanout with `DISTINCT`.
- **Unexpected `NULL` or missing row:** decide whether the fact is unknown,
  inapplicable, zero, or absent before using `COALESCE`; inspect outer-join
  predicate placement and empty-input aggregate behavior.
- **Unstable top/first/last output:** add `ORDER BY` with a unique final
  tie-breaker before `LIMIT` or order-sensitive windows/aggregates.
- **`psql` stops on an error:** fix the first error shown by
  `ON_ERROR_STOP`, restore the declared transaction/setup state, and rerun the
  complete file. A later successful statement does not validate a partial run.

## Self-check

- Do text transformations define behavior for `NULL` and malformed input?
- Can the normalized output be traced back to the original value?

## Next step

Continue to [Day 13 — date, time, and time zones](day13_date_time_functions.md).

## Deep dive and reference

Learning objectives
- Clean and standardize text: TRIM, UPPER/LOWER, REPLACE, REGEXP_REPLACE
- Parse text: SPLIT_PART, SUBSTRING, POSITION, regular expressions
- Compare case-insensitively: ILIKE, citext, trigram similarity (pg_trgm)

Core concepts and deep dive
- Normalization: trim whitespace, unify case, collapse repeated spaces with regex.
- Parsing: SPLIT_PART(email,'@',2) to get domain; SUBSTRING with regex for flexible extraction.
- Regular expressions: ~ (match), ~* (case-insensitive), !~ (not match); capture groups in SUBSTRING.
- Performance: Function on column may prevent index use; consider functional indexes or store normalized columns.

Examples
- Standardize emails: lower(trim(email)).
- Extract an email domain: `split_part(email, '@', 2)`.
- Build labels from `products.category`, `products.name`, and formatted
  `products.price`.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- String functions: https://www.postgresql.org/docs/current/functions-string.html
- Regex: https://www.postgresql.org/docs/current/functions-matching.html
- pg_trgm: https://www.postgresql.org/docs/current/pgtrgm.html

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-12 — String Functions.

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day12_string_functions.md
- Answer-free learner SQL: sql/postgres-60day/day12_string_functions.sql

Key terms to teach in context: Normalization, Delimiter, Regular expression. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Compare a raw email with lower(trim(email)). Use the normalized expression for duplicate grouping, but keep the original column visible so a reviewer can audit what changed. Explain why silently overwriting the raw value would lose evidence.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-12/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
