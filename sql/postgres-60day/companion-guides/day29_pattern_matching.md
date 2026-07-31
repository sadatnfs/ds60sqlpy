# Day 29 — Pattern Matching: LIKE/ILIKE, SIMILAR TO, and Regular Expressions (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 28 — JSONB and XML](day28_json_xml.md)
- **Artifacts:** [learner SQL](../day29_pattern_matching.sql) ·
  [solution reasoning](../solutions/day29_solutions.md) ·
  [executable solution](../solutions/day29_solutions.sql)

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

2. Open **SQL-29 — Pattern Matching** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-29/lesson/workspace/sql/postgres-60day/day29_pattern_matching.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day29_pattern_matching.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day29_pattern_matching.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Wildcard, Anchor, Sargable predicate. Its worked SQL reads or creates `customers`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Compare email ~ 'customer1[0-9]{2}' with the anchored email ~ '^customer1[0-9]{2}@example\\.com$'. Add surrounding text to a test value and show why an unanchored validation can accept only a matching substring.
The expected contract is that Matching customer rows in stable ID order. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day29_pattern_matching.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT customer_id, full_name, email
FROM customers
WHERE email ILIKE '%@example.com' ESCAPE '\'
  AND full_name ILIKE 'customer %' ESCAPE '\'
ORDER BY customer_id
LIMIT 20;
```

**How to read it:** Example 1: Start with `customers` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows. The final `SELECT` displays `customer_id`, `full_name`, and `email`. `ORDER BY` determines presentation order and the final `LIMIT 20` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `customer_id`, capped at 20 rows with columns `customer_id`, `full_name`, and `email` from `customers`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT product_id, name, category
FROM products
WHERE name ~ '^Product [0-9]{2,3}$'
ORDER BY product_id
LIMIT 20;
```

**How to read it:** Example 2: Start with `products` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows. The final `SELECT` displays `product_id`, `name`, and `category`. `ORDER BY` determines presentation order and the final `LIMIT 20` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per `product_id`, and `category`, capped at 20 rows with columns `product_id`, `name`, and `category` from `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Select the simplest matching operator that expresses a search or validation.
- Anchor validation patterns and reason about index support.

## Vocabulary and concepts

- **Wildcard:** `%` or `_` in a `LIKE` pattern.
- **Anchor:** `^` or `$`, which binds a regular expression to a string boundary.
- **Sargable predicate:** a search condition an index can support directly.

## Worked example / walkthrough

Compare `email ~ 'customer1[0-9]{2}'` with the anchored
`email ~ '^customer1[0-9]{2}@example\\.com$'`. Add surrounding text to a test
value and show why an unanchored validation can accept only a matching
substring.

## Practice assumptions and review method

- **Focus:** Choose literal, wildcard, or regular-expression matching from the text grammar and make case, escaping, and anchoring explicit.
- **Assumptions:** PostgreSQL `LIKE` is case-sensitive, `ILIKE` is case-insensitive, and POSIX regex operators use `~`/`~*`. Collation can affect text behavior.
- **Failure to watch for:** Leading wildcards can prevent ordinary b-tree use; unanchored or overly broad regex patterns can match more text than intended.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Choose literal, wildcard, or regular-expression matching from the text grammar and make case, escaping, and anchoring explicit.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Find customer names beginning with `Customer 1` case-insensitively.
   **Progressive hint:** `ILIKE 'Customer 1%'` uses `%` for any suffix.
   **Inputs/evidence:** For sql-29 Exercise 1, read from `customers`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-29 Exercise 1, expected output: Matching customer rows in stable ID order. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
   **Verify:** For sql-29 Exercise 1, run an anti-check that counts rows where NOT ((c.full_name ILIKE 'Customer 1%')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`. Add one row for which `(c.full_name ILIKE 'Customer 1%')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
2. **Query writing:** Find emails that match the course's simple lowercase example.com pattern.
   **Progressive hint:** Anchor both ends and escape the literal dot in the POSIX regex.
   **Inputs/evidence:** For sql-29 Exercise 2, read from `customers`. Build the answer toward `customer_id`, and `email`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-29 Exercise 2, expected output: Only matching non-null email rows. The final columns are `customer_id`, and `email`. The final order is `c.customer_id`.
   **Verify:** For sql-29 Exercise 2, run an anti-check that counts rows where NOT ((c.email ~ '^customer[0-9]+@example[.]com$')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `email` against `customers`. Add one row for which `(c.email ~ '^customer[0-9]+@example[.]com$')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
3. **Query writing:** Return event paths under `/p/` using JSON extraction and an anchored pattern.
   **Progressive hint:** Extract path text, then anchor the literal prefix.
   **Inputs/evidence:** For sql-29 Exercise 3, read from `events`. Build the answer toward `event_id`, and `path`; keep `event_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-29 Exercise 3, expected output: Events whose path begins `/p/`. The final columns are `event_id`, and `path`. The final order is `e.event_id`.
   **Verify:** For sql-29 Exercise 3, run an anti-check that counts rows where NOT ((e.metadata ->> 'path' LIKE '/p/%')); require unique `event_id` where the expected grain is one row per key and confirm the projected `event_id`, and `path` against `events`. Add one row for which `(e.metadata ->> 'path' LIKE '/p/%')` is true and one for which it is false; verify only the matching `event_id` value is returned.
4. **Prediction:** Match literal percent and underscore characters in sample text and contrast them with wildcard behavior.
   **Progressive hint:** Declare an escape character and prefix each literal wildcard.
   **Inputs/evidence:** For sql-29 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `value`; keep `value` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-29 Exercise 4, expected output: Only the two rows containing the requested literal symbols. The final columns are `value`. The final order is `value`.
   **Verify:** For sql-29 Exercise 4, run an anti-check that counts rows where NOT ((value LIKE '%\%%' ESCAPE '\' OR value LIKE '%\_%' ESCAPE '\')); require unique `value` where the expected grain is one row per key and confirm the projected `value` against the inline `VALUES` fixture. Add one row for which `(value LIKE '%\%%' ESCAPE '\' OR value LIKE '%\_%' ESCAPE '\')` is true and one for which it is false; verify only the matching `value` value is returned.
5. **Debugging:** Extract the captured numeric suffix from a valid customer name without replacing the entire string blindly.
   **Progressive hint:** First assert the anchored grammar, then use `substring(... FROM regex)`.
   **Inputs/evidence:** For sql-29 Exercise 5, read from `customers`. Compute `customer_id`, and `name_number` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-29 Exercise 5, expected output: One row per valid course customer name. The final columns are `customer_id`, and `name_number`. The final order is `c.customer_id`.
   **Verify:** For sql-29 Exercise 5, evaluate each of `name_number` in a separate control `SELECT` over `customers` using `(c.full_name ~ '^Customer [0-9]+$')`; require one final row and compare every value. Add one row for which `(c.full_name ~ '^Customer [0-9]+$')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
6. **Extension:** Classify emails as course example, other valid-looking, missing, or malformed using ordered patterns.
   **Progressive hint:** Handle NULL first, then most specific anchored pattern, then a bounded general pattern.
   **Inputs/evidence:** For sql-29 Exercise 6, read from `customers`. Compute `customer_id`, `email`, and `email_class` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-29 Exercise 6, expected output: One row per customer with one classification. The final columns are `customer_id`, `email`, and `email_class`. The final order is `c.customer_id`.
   **Verify:** For sql-29 Exercise 6, evaluate each of `email`, and `email_class` in a separate control `SELECT` over `customers`; require one final row and compare every value. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Leading wildcards can prevent ordinary b-tree use; unanchored or overly broad regex patterns can match more text than intended.
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

- Is the pattern a substring search or a whole-value validation?
- Could a leading wildcard or function-wrapped column prevent ordinary B-tree
  index use?

## Next step

Continue to [Day 30 — Phase 2 project](day30_phase2_project.md).

## Deep dive and reference

Learning objectives
- Use LIKE/ILIKE for simple wildcard matching and understand index implications
- Apply SIMILAR TO and POSIX regular expressions (~, ~*, !~, !~*) for complex patterns
- Build robust text filters, validators, and extractors; know when to use trigram/FTS

Why this matters
User inputs, product codes, and free text require flexible matching. Good patterns minimize false matches and run fast on large tables.

Core concepts and deep dive
- LIKE/ILIKE
  - % any-length wildcard; _ single char; ILIKE is case-insensitive (Postgres extension)
  - Index use: prefix patterns (foo%) can use btree indexes; leading wildcard (%foo) cannot; consider pg_trgm or re-architecture
- SIMILAR TO
  - SQL standard regex-like; less commonly used in Postgres; prefer POSIX regex operators
- POSIX regex operators
  - ~ match case-sensitive; ~* case-insensitive; !~ negation; supports anchors ^$, character classes, quantifiers
  - SUBSTRING(str FROM 'regex') to extract; REGEXP_REPLACE for cleanup
- Performance aids
  - pg_trgm extension + GIN index for ILIKE/regex with wildcards on large text columns
  - Functional indexes on LOWER(col) to support case-insensitive equality
- Validation vs search
  - Validation uses ^...$ anchored patterns; search may be substring (no anchors)

Patterns
- Email-like validation: email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
- Domain filters: LOWER(email) LIKE '%@example.com'
- Product-name matching: `name ~ '^Product [0-9]{2,3}$'`

Pitfalls
- Unanchored regex in validation allows partial matches; use anchors
- Locale issues in case-folding; consider citext for equality semantics
- Regex backtracking on catastrophic patterns; keep patterns simple and specific

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Pattern matching: https://www.postgresql.org/docs/current/functions-matching.html
- pg_trgm: https://www.postgresql.org/docs/current/pgtrgm.html

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-29 — Pattern Matching.

I have completed the direct catalog prerequisite: `sql-28`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day29_pattern_matching.md
- Answer-free learner SQL: sql/postgres-60day/day29_pattern_matching.sql

Key terms to teach in context: Wildcard, Anchor, Sargable predicate. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Compare email ~ 'customer1[0-9]{2}' with the anchored email ~ '^customer1[0-9]{2}@example\\.com$'. Add surrounding text to a test value and show why an unanchored validation can accept only a matching substring.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-29/ working copy. Never point setup, reset, DDL, or DML
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
