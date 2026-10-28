# Day 14: Numeric Types, Casting, and Precision (Companion Guide)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-14**. The
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
   `.learning/sql/sql-14/lesson/workspace/sql/postgres-60day/day14_numeric_and_casting.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-14
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
- **Prerequisites:** [Day 13; date, time, and time zones](day13_date_time_functions.md)
- **Artifacts:** [learner SQL](../day14_numeric_and_casting.sql) ·
  [solution reasoning](../solutions/day14_solutions.md) ·
  [executable solution](../solutions/day14_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Exact numeric, Scale, Type coercion. Its worked SQL reads or creates `orders`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Evaluate 1 / 3, 1::numeric / 3, and ROUND(1::numeric / NULLIF(3, 0), 2). Explain the result type at each step and why guarding the denominator belongs before rounding.
The expected contract is that One row per product. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day14_numeric_and_casting.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
SELECT order_id,
       total_amount,
       round(total_amount, 0) AS rounded,
       cast(total_amount AS int) AS as_int
FROM orders
ORDER BY total_amount DESC, order_id
LIMIT 50;
```

**How to read it:** Example 1: Start with `orders` in `FROM`/`JOIN`. The final `SELECT` displays `order_id`, `total_amount`, `rounded`, and `as_int`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `order_id`, capped at 50 rows with columns `order_id`, `total_amount`, `rounded`, and `as_int` from `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT p.category,
       SUM(oi.quantity) AS qty,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)) / NULLIF(SUM(oi.quantity),0), 2) AS avg_price
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY avg_price DESC, p.category;
```

**How to read it:** Example 2: Start with `order_items`, and `products` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `category`, `qty`, and `avg_price`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `category` with columns `category`, `qty`, and `avg_price` from `order_items`, and `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Choose numeric types that preserve required precision.
- Cast deliberately and guard division, rounding, overflow, and malformed text.

## Vocabulary and concepts

- **Exact numeric:** `numeric`/`decimal`, which stores decimal values without
  binary floating-point approximation.
- **Scale:** digits to the right of the decimal point.
- **Type coercion:** PostgreSQL's conversion of values to a compatible type.

## Worked example / walkthrough

Evaluate `1 / 3`, `1::numeric / 3`, and
`ROUND(1::numeric / NULLIF(3, 0), 2)`. Explain the result type at each step and
why guarding the denominator belongs before rounding.

## Practice assumptions and review method

- **Focus:** Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.
- **Assumptions:** Money is exact `numeric`; division casts denominators to numeric where fractions matter. NULL/zero denominators return NULL through `NULLIF`.
- **Failure to watch for:** Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Calculate product gross margin amount and percentage, returning NULL percentage for zero price.
   **Progressive hint:** Keep exact numeric arithmetic and guard the denominator with `NULLIF`.
   **Inputs/evidence:** For sql-14 Exercise 1, read from `products`. Build the answer toward `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate`; keep `product_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-14 Exercise 1, expected output: One row per product. The final columns are `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate`. The final order is `margin_rate DESC NULLS LAST, p.product_id`.
   **Verify:** For sql-14 Exercise 1, reselect the returned keys directly from the source; require unique `product_id` where the expected grain is one row per key and confirm the projected `product_id`, `price`, `cost`, `margin_amount`, and `margin_rate` against `products`. Repeat with `NULL` in `product_id`, and `price` and state whether the row is kept, rejected, or classified.
2. **Query writing:** Safely cast a set of text values to numeric only when they match a numeric grammar.
   **Progressive hint:** Validate with a regex before casting; otherwise return NULL.
   **Inputs/evidence:** For sql-14 Exercise 2, read from the inline `VALUES` fixture. Build the answer toward `raw_value`, and `parsed_numeric`; keep `parsed_numeric` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-14 Exercise 2, expected output: One row per sample text. The final columns are `raw_value`, and `parsed_numeric`.
   **Verify:** For sql-14 Exercise 2, reselect the returned keys directly from the source; require unique `parsed_numeric` where the expected grain is one row per key and confirm the projected `raw_value`, and `parsed_numeric` against the inline `VALUES` fixture. Add one source row with a new `parsed_numeric`; verify the result gains exactly one row carrying that `parsed_numeric` value.
3. **Query writing:** Show order-item net revenue rounded only after summing.
   **Progressive hint:** Aggregate exact line expressions first; round the final display value.
   **Inputs/evidence:** For sql-14 Exercise 3, read from `order_items`. Build the answer toward `order_id`, and `net_order_revenue`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-14 Exercise 3, expected output: One row per order. The final columns are `order_id`, and `net_order_revenue`. The final order is `oi.order_id`.
   **Verify:** For sql-14 Exercise 3, independently aggregate `order_items` by `order_id`; require one output row for every distinct `order_id` tuple and compare `net_order_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `net_order_revenue` for the existing `order_id` tuple and verify the new tuple appears exactly once.
4. **Prediction:** Compare integer division with numeric division for 1 divided by 4.
   **Progressive hint:** At least one operand must be numeric to preserve the fraction.
   **Inputs/evidence:** For sql-14 Exercise 4, read from `orders`, `order_items`, and `products`. Compute `integer_division`, and `numeric_division` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-14 Exercise 4, expected output: One row showing 0 and 0.25. The final columns are `integer_division`, and `numeric_division`.
   **Verify:** For sql-14 Exercise 4, evaluate each of `integer_division`, and `numeric_division` in a separate control `SELECT` over `orders`, `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
5. **Debugging:** Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders.
   **Progressive hint:** Aggregate payment amount and count distinct order IDs at one common scope.
   **Inputs/evidence:** For sql-14 Exercise 5, read from `payments`. Build the answer toward `average_paid_amount_per_order`; keep `payment_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-14 Exercise 5, expected output: Exactly one summary row. The final columns are `average_paid_amount_per_order`.
   **Verify:** For sql-14 Exercise 5, reselect the returned keys directly from the source; require unique `payment_id` where the expected grain is one row per key and confirm the projected `average_paid_amount_per_order` against `payments`. Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.
6. **Extension:** Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference.
   **Progressive hint:** This diagnostic makes the consequence of early rounding visible.
   **Inputs/evidence:** For sql-14 Exercise 6, read from `order_items`. Build the answer toward `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference`; keep `order_item_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-14 Exercise 6, expected output: One row with two totals and their signed difference. The final columns are `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference`.
   **Verify:** For sql-14 Exercise 6, reselect the returned keys directly from the source; require unique `order_item_id` where the expected grain is one row per key and confirm the projected `sum_of_rounded_lines`, `rounded_exact_total`, and `rounding_difference` against `order_items`. Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
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

- Can you justify the type used for money-like values and ratios?
- Are division-by-zero and `NULL` behavior visible rather than silently
  misleading?

## Next step

Continue to [Day 15; Phase 1 project](day15_phase1_project.md).

## Deep dive and reference

Learning objectives
- Use integer, numeric/decimal, and floating types appropriately
- Control rounding and formatting; avoid integer division pitfalls
- Cast safely between types; handle NULLs and invalid text

Core concepts and deep dive
- Types: integer (fast, bounded), numeric(p,s) (exact decimal), double precision (approximate). Use numeric for money.
- Division: integer/int division truncates; cast to numeric for fractional results.
- Rounding: ROUND(x,2), CEIL/FLOOR; formatting with to_char for presentation.
- Casting: CAST(text AS numeric) or ::numeric; use to_number(text, format) for messy text.

Examples
- Compute gross_margin_pct = (price-cost)/NULLIF(price,0) casting to numeric with scale.
- Parse '1,234.50' with to_number and compare to numeric cast behavior.

Pitfalls
- Silent rounding when casting to narrower numeric precision.
- Dividing by zero; use NULLIF(den,0) to avoid errors.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Numeric types: https://www.postgresql.org/docs/current/datatype-numeric.html

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-14 — Numeric and Casting.

I have completed the direct catalog prerequisite: `sql-13`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day14_numeric_and_casting.md
- Answer-free learner SQL: sql/postgres-60day/day14_numeric_and_casting.sql

Key terms to teach in context: Exact numeric, Scale, Type coercion. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Evaluate 1 / 3, 1::numeric / 3, and ROUND(1::numeric / NULLIF(3, 0), 2). Explain the result type at each step and why guarding the denominator belongs before rounding.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-14/ working copy. Never point setup, reset, DDL, or DML
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
