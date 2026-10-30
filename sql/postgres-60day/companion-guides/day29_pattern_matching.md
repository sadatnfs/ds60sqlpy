# Day 29: Pattern Matching: LIKE/ILIKE, SIMILAR TO, and Regular Expressions (Companion Guide)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-29**. The
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
   `.learning/sql/sql-29/lesson/workspace/sql/postgres-60day/day29_pattern_matching.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-29
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 28; JSONB and XML](day28_json_xml.md)
- **Artifacts:** [learner SQL](../day29_pattern_matching.sql) ·
  [solution reasoning](../solutions/day29_solutions.md) ·
  [executable solution](../solutions/day29_solutions.sql)

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

These worked excerpts come from `sql/postgres-60day/day29_pattern_matching.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
SELECT
  customer_id,
  full_name,
  email
FROM
  customers
WHERE
  email ILIKE '%@example.com' ESCAPE '\'
  AND full_name ILIKE 'customer %' ESCAPE '\'
ORDER BY
  customer_id
LIMIT 20;
```

**How to read it:** Example 1: Start with `customers` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows. The final `SELECT` displays `customer_id`, `full_name`, and `email`. `ORDER BY` determines presentation order and the final `LIMIT 20` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `customer_id`, capped at 20 rows with columns `customer_id`, `full_name`, and `email` from `customers`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT
  product_id,
  name,
  category
FROM
  products
WHERE
  name ~ '^Product [0-9]{2,3}$'
ORDER BY
  product_id
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

Continue to [Day 30; Phase 2 project](day30_phase2_project.md).

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

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

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
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
