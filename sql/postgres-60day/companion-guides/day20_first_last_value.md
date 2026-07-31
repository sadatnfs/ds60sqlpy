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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-20/day20_first_last_value.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
Boundary value, Current-row frame, Full-partition frame. Its worked SQL reads or creates `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Order a customer's orders by date and compare default LASTVALUE(totalamount) with the same function over ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING. The default often returns the current row's value; the full frame exposes the true final value.
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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per order with constant first/last values per customer.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per order with constant first/last values per customer.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected shape:** One row per order with constant first/last values per customer.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. **Query writing:** Show each product with the cheapest and most expensive price in its category.
   **Progressive hint:** Order by price and use a full frame; values tie without needing row identity.
   **Expected shape:** One row per product.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Query writing:** Compare every payment with the first and last payment amount for its order.
   **Progressive hint:** Partition by order, order by timestamp/payment ID, and keep the full frame.
   **Expected shape:** One row per payment.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. **Prediction:** Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.
   **Progressive hint:** The default ends at the current row; explicit following reaches the true last row.
   **Expected shape:** Three rows showing default current value and full-frame 30.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. **Debugging:** Return one first and one last order per customer without using window output as an accidental duplicate report.
   **Progressive hint:** Compute first/last IDs with full-frame windows, then select distinct customer-level output.
   **Expected shape:** One row per customer with orders.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. **Extension:** Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.
   **Progressive hint:** `DISTINCT ON` keeps the first row under its mandatory leading order keys.
   **Expected shape:** At most one latest order per customer.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day20_first_last_value.md
- Answer-free learner SQL: sql/postgres-60day/day20_first_last_value.sql

The lesson concepts include Boundary value, Current-row frame, Full-partition frame. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Order a customer's orders by date and compare default LASTVALUE(totalamount) with the same function over ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING. The default often returns the current row's value; the full frame exposes the true final value.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-20/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
