# Day 20 — FIRST_VALUE, LAST_VALUE, NTH_VALUE (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 19 — running aggregates](day19_running_aggregates.md)
- **Artifacts:** [learner SQL](../day20_first_last_value.sql) ·
  [solution reasoning](../solutions/day20_solutions.md) ·
  [executable solution](../solutions/day20_solutions.sql)

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

2. Open **SQL-20 — First Last Value** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-20/lesson/workspace/sql/postgres-60day/day20_first_last_value.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day20_first_last_value.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day20_first_last_value.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Boundary value, Current-row frame, Full-partition frame. Its worked SQL reads or creates `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Order a customer's orders by date and compare default LASTVALUE(totalamount) with the same function over ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING. The default often returns the current row's value; the full frame exposes the true final value.
The expected contract is that One row per order with constant first/last values per customer. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day20_first_last_value.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount,
       FIRST_VALUE(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS first_order_amount,
       LAST_VALUE(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS last_order_amount
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 100;
```

**How to read it:** Example 1: Start with `orders` in `FROM`/`JOIN`; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `customer_id`, `order_id`, `order_date`, `total_amount`, `first_order_amount`, and `last_order_amount`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `customer_id`, and `order_id`, capped at 100 rows with columns `customer_id`, `order_id`, `order_date`, `total_amount`, `first_order_amount`, and `last_order_amount` from `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
WITH per_cust AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         o.total_amount,
         FIRST_VALUE(o.total_amount) OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date, o.order_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
         ) AS first_amt
  FROM orders o
)
SELECT *, ROUND(total_amount - first_amt, 2) AS delta_from_first
FROM per_cust
ORDER BY customer_id, order_date, order_id
LIMIT 100;
```

**How to read it:** Example 2: Start with `orders` in `FROM`/`JOIN`; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `*`, and `delta_from_first`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per `*`, capped at 100 rows with columns `*`, and `delta_from_first` from `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Retrieve boundary values from a deliberately framed ordered partition.
- Diagnose the common `LAST_VALUE` default-frame surprise.

## Vocabulary and concepts

- **Boundary value:** the first, last, or Nth value under a declared ordering.
- **Current-row frame:** a frame whose upper boundary stops at the current row.
- **Full-partition frame:** a frame extending through
  `UNBOUNDED FOLLOWING`.

## Worked example / walkthrough

Order a customer's orders by date and compare default
`LAST_VALUE(total_amount)` with the same function over
`ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`. The default often
returns the current row's value; the full frame exposes the true final value.

## Practice assumptions and review method

- **Focus:** Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.
- **Assumptions:** First/last refer to ordered rows, not minimum/maximum values unless ordering states that. Ties need unique keys for deterministic row identity.
- **Failure to watch for:** The default `LAST_VALUE` frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Show every order with the customer's first and last order timestamps.
   **Progressive hint:** Use one full-partition frame from unbounded preceding through unbounded following.
   **Inputs/evidence:** For sql-20 Exercise 1, read from `orders`. Compute `order_id`, `customer_id`, `order_date`, `first_order_date`, and `last_order_date` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-20 Exercise 1, expected output: One row per order with constant first/last values per customer. The final columns are `order_id`, `customer_id`, `order_date`, `first_order_date`, and `last_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-20 Exercise 1, evaluate each of `order_date`, `first_order_date`, and `last_order_date` in a separate control `SELECT` over `orders`; require one final row and compare every value. Tie two rows on `o.customer_id` and give them different `o.order_id` values; verify `o.customer_id, o.order_date, o.order_id` chooses a stable first/last row.
2. **Query writing:** Show each product with the cheapest and most expensive price in its category.
   **Progressive hint:** Order by price and use a full frame; values tie without needing row identity.
   **Inputs/evidence:** For sql-20 Exercise 2, read from `products`. Compute `product_id`, `category`, `price`, `category_min_price`, and `category_max_price` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-20 Exercise 2, expected output: One row per product. The final columns are `product_id`, `category`, `price`, `category_min_price`, and `category_max_price`. The final order is `p.category, p.price, p.product_id`.
   **Verify:** For sql-20 Exercise 2, evaluate each of `category_min_price`, and `category_max_price` in a separate control `SELECT` over `products`; require one final row and compare every value. Add one source row with a new `product_id`; verify the result gains exactly one row carrying that `product_id` value.
3. **Query writing:** Compare every payment with the first and last payment amount for its order.
   **Progressive hint:** Partition by order, order by timestamp/payment ID, and keep the full frame.
   **Inputs/evidence:** For sql-20 Exercise 3, read from `payments`. Compute `payment_id`, `order_id`, `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-20 Exercise 3, expected output: One row per payment. The final columns are `payment_id`, `order_id`, `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount`. The final order is `p.order_id, p.payment_date, p.payment_id`.
   **Verify:** For sql-20 Exercise 3, evaluate each of `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount` in a separate control `SELECT` over `payments`; require one final row and compare every value. Tie two rows on `p.order_id` and give them different `p.payment_id` values; verify `p.order_id, p.payment_date, p.payment_id` chooses a stable first/last row.
4. **Prediction:** Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.
   **Progressive hint:** The default ends at the current row; explicit following reaches the true last row.
   **Inputs/evidence:** For sql-20 Exercise 4, read from the inline `VALUES` fixture. Build the answer toward `value`, `default_last_value`, and `partition_last_value`; keep `value` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-20 Exercise 4, expected output: Three rows showing default current value and full-frame 30. The final columns are `value`, `default_last_value`, and `partition_last_value`. The final order is `value`.
   **Verify:** For sql-20 Exercise 4, choose one complete partition from the inline `VALUES` fixture; hand-calculate its first, middle, and final window values for `value`, `default_last_value`, and `partition_last_value`, then verify output keys remain `value`. Use a one-row partition and a partition tied on `value`; verify `value` and `value` preserve the intended first/last row.
5. **Debugging:** Return one first and one last order per customer without using window output as an accidental duplicate report.
   **Progressive hint:** Compute first/last IDs with full-frame windows, then select distinct customer-level output.
   **Inputs/evidence:** For sql-20 Exercise 5, read from `orders`. Compute `customer_id`, `first_order_id`, and `last_order_id` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-20 Exercise 5, expected output: One row per customer with orders. The final columns are `customer_id`, `first_order_id`, and `last_order_id`. The final order is `customer_id`.
   **Verify:** For sql-20 Exercise 5, evaluate each of `first_order_id`, and `last_order_id` in a separate control `SELECT` over `orders`; require one final row and compare every value. Tie two rows on `customer_id` and give them different `customer_id` values; verify `customer_id` chooses a stable first/last row.
6. **Extension:** Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.
   **Progressive hint:** `DISTINCT ON` keeps the first row under its mandatory leading order keys.
   **Inputs/evidence:** For sql-20 Exercise 6, read from `orders`. Build the answer toward `customer_id`, `order_id`, `order_date`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-20 Exercise 6, expected output: At most one latest order per customer. The final columns are `customer_id`, `order_id`, `order_date`, and `total_amount`. The final order is `o.customer_id, o.order_date DESC, o.order_id DESC`.
   **Verify:** For sql-20 Exercise 6, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `customer_id`, `order_id`, `order_date`, and `total_amount` against `orders`. Tie two rows on `o.customer_id` and give them different `o.order_id DESC` values; verify `o.customer_id, o.order_date DESC, o.order_id DESC` chooses a stable first/last row.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** The default LASTVALUE frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.
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

- Does “last” mean last so far or last in the complete partition?
- What should `NTH_VALUE` return when fewer than N rows exist?

## Next step

Continue to [Day 21 — distribution functions](day21_distribution_functions.md).

## Deep dive and reference

Learning objectives
- Extract first/last values within ordered partitions
- Use frame clauses to avoid surprising LAST_VALUE behavior
- Compute baselines and end-of-period values side-by-side

Why this matters
Anchoring a row against a starting or ending value supports normalization (e.g., index to 100), growth from baseline, and end-of-period reporting.

Core concepts and deep dive
- FIRST_VALUE(expr) OVER (PARTITION BY k ORDER BY t ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) reliably gives the partition’s first value.
- LAST_VALUE requires an appropriate frame; default frame returns current row’s value. Use ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING to get the true last value.
- NTH_VALUE(expr, n) generalizes to the nth ordered value.

Patterns
- Normalize to first: x / NULLIF(FIRST_VALUE(x) OVER (...),0).
- Compare current to last: current - LAST_VALUE(x) OVER (... ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING).

Pitfalls
- Forgetting to extend the frame for LAST_VALUE yields row’s current, not partition last.
- Non-deterministic ordering for duplicates; add tiebreakers.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- FIRST/LAST/NTH: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW-TABLE

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-20 — First Last Value.

I have completed the direct catalog prerequisite: `sql-19`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day20_first_last_value.md
- Answer-free learner SQL: sql/postgres-60day/day20_first_last_value.sql

Key terms to teach in context: Boundary value, Current-row frame, Full-partition frame. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Order a customer's orders by date and compare default LASTVALUE(totalamount) with the same function over ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING. The default often returns the current row's value; the full frame exposes the true final value.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-20/ working copy. Never point setup, reset, DDL, or DML
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
