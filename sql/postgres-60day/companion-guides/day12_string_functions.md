# Day 12: String Functions and Text Processing (Companion Guide)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-12**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-12/lesson/workspace/sql/postgres-60day/day12_string_functions.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-12
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 11; CASE expressions](day11_case_expressions.md)
- **Artifacts:** [learner SQL](../day12_string_functions.sql) ·
  [solution reasoning](../solutions/day12_solutions.md) ·
  [executable solution](../solutions/day12_solutions.sql)

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

These worked excerpts come from `sql/postgres-60day/day12_string_functions.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
SELECT
  customer_id,
  email,
  lower(trim(email)) AS email_clean,
  split_part(email, '@', 2) AS domain
FROM
  customers
ORDER BY
  customer_id
LIMIT 50;
```

**How to read it:** Example 1: Start with `customers` in `FROM`/`JOIN`. The final `SELECT` displays `customer_id`, `email`, `email_clean`, and `domain`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `customer_id`, capped at 50 rows with columns `customer_id`, `email`, `email_clean`, and `domain` from `customers`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT
  product_id,
  name,
  replace(name, 'Product', 'Item') AS renamed,
  substr(name, 1, 10) AS short_name
FROM
  products
ORDER BY
  product_id
LIMIT 50;
```

**How to read it:** Example 2: Start with `products` in `FROM`/`JOIN`. The final `SELECT` displays `product_id`, `name`, `renamed`, and `short_name`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per `product_id`, capped at 50 rows with columns `product_id`, `name`, `renamed`, and `short_name` from `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

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
   **Inputs/evidence:** For sql-12 Exercise 1, read from `customers`. Build the answer toward `customer_id`, `original_name`, `trimmed_name`, and `normalized_email`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-12 Exercise 1, expected output: One row per customer. The final columns are `customer_id`, `original_name`, `trimmed_name`, and `normalized_email`. The final order is `c.customer_id`.
   **Verify:** For sql-12 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `original_name`, `trimmed_name`, and `normalized_email` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
2. **Query writing:** Extract the email domain and count customers by domain, preserving missing emails.
   **Progressive hint:** `split_part` parses the second component; CASE keeps NULL distinct.
   **Inputs/evidence:** For sql-12 Exercise 2, read from `customers`. Build the answer toward `email_domain`, and `customer_count`; keep `email_domain` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-12 Exercise 2, expected output: One row per domain label. The final columns are `email_domain`, and `customer_count`. The final order is `customer_count DESC, email_domain`.
   **Verify:** For sql-12 Exercise 2, independently aggregate `customers` by `email_domain`; require one output row for every distinct `email_domain` tuple and compare `customer_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customer_count` for the existing `email_domain` tuple and verify the new tuple appears exactly once.
3. **Query writing:** Create an ordered comma-separated list of department employee names.
   **Progressive hint:** Put `ORDER BY` inside `string_agg` so concatenation order is deliberate.
   **Inputs/evidence:** For sql-12 Exercise 3, read from `departments`, and `employees`. Build the answer toward `department_id`, `department_name`, and `employees`; keep `department_id`, and `name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-12 Exercise 3, expected output: One row per department. The final columns are `department_id`, `department_name`, and `employees`. The final order is `d.department_id`.
   **Verify:** For sql-12 Exercise 3, independently aggregate `departments`, and `employees` by `department_id`, and `name`; require one output row for every distinct `department_id`, and `name` tuple and compare `employees` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `employees` for the existing `department_id`, and `name` tuple and verify the new tuple appears exactly once.
4. **Prediction:** Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled.
   **Progressive hint:** Use a POSIX whitespace class and the global regex flag.
   **Inputs/evidence:** For sql-12 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `source_text`, and `normalized_text`; keep `source_text` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-12 Exercise 4, expected output: Three input/output rows. The final columns are `source_text`, and `normalized_text`.
   **Verify:** For sql-12 Exercise 4, reselect the returned keys directly from the source; require unique `source_text` where the expected grain is one row per key and confirm the projected `source_text`, and `normalized_text` against the inline `VALUES` fixture. Add one source row with a new `source_text`; verify the result gains exactly one row carrying that `source_text` value.
5. **Debugging:** Safely find customer names containing a literal percent or underscore rather than treating them as wildcards.
   **Progressive hint:** Escape wildcard characters and declare the escape character.
   **Inputs/evidence:** For sql-12 Exercise 5, read from `customers`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-12 Exercise 5, expected output: Rows only when the literal character occurs. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
   **Verify:** For sql-12 Exercise 5, run an anti-check that counts rows where NOT ((c.full_name LIKE '%\%%' ESCAPE '\' OR c.full_name LIKE '%\_%' ESCAPE '\')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`. Add one row for which `(c.full_name LIKE '%\%%' ESCAPE '\' OR c.full_name LIKE '%\_%' ESCAPE '\')` is true and one for which it is false; verify only the matching `customer_id` value is returned.
6. **Extension:** Parse the numeric suffix from names like `Customer 42`, returning NULL for nonmatching text.
   **Progressive hint:** Use a captured regex replacement only after a match predicate establishes the format.
   **Inputs/evidence:** For sql-12 Exercise 6, read from `customers`. Build the answer toward `customer_id`, `full_name`, and `parsed_customer_number`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-12 Exercise 6, expected output: One row per customer with a numeric suffix. The final columns are `customer_id`, `full_name`, and `parsed_customer_number`. The final order is `c.customer_id`.
   **Verify:** For sql-12 Exercise 6, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `full_name`, and `parsed_customer_number` against `customers`. Repeat with `NULL` in `customer_id`, and `full_name` and state whether the row is kept, rejected, or classified.

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

Continue to [Day 13; date, time, and time zones](day13_date_time_functions.md).

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

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-12 — String Functions.

I have completed the direct catalog prerequisite: `sql-11`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day12_string_functions.md
- Answer-free learner SQL: sql/postgres-60day/day12_string_functions.sql

Key terms to teach in context: Normalization, Delimiter, Regular expression. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Compare a raw email with lower(trim(email)). Use the normalized expression for duplicate grouping, but keep the original column visible so a reviewer can audit what changed. Explain why silently overwriting the raw value would lose evidence.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
