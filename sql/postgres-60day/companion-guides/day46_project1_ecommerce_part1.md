# Day 46 — E-commerce Project, Part 1: LTV and Cohorts

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 45 — optimization project](day45_phase3_optimization_project.md)
- **Artifacts:** [learner SQL](../day46_project1_ecommerce_part1.sql) ·
  [solution reasoning](../solutions/day46_solutions.md) ·
  [executable solution](../solutions/day46_solutions.sql)

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

2. Open **SQL-46 — Project1 Ecommerce Part1** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-46/day46_project1_ecommerce_part1.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day46_project1_ecommerce_part1.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day46_project1_ecommerce_part1.sql
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
LTV, Signup cohort, Lifecycle offset. Its worked SQL reads or creates `orders`, `order_items`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Collapse line items to order value, then orders to one customer LTV row. Left join from customers if zero-order customers belong in the population. Reconcile summed LTV with the chosen source total before assigning thresholds; segmenting at a duplicated order-line grain would bias both counts and value.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day46_project1_ecommerce_part1.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH order_values AS (
  SELECT o.customer_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
), ltv AS (
  SELECT customer_id, ROUND(SUM(order_value),2) AS ltv
  FROM order_values
  GROUP BY customer_id
)
SELECT c.customer_id, c.country, c.segment, l.ltv,
       NTILE(4) OVER (ORDER BY l.ltv DESC) AS ltv_quartile
FROM customers c
JOIN ltv l ON l.customer_id = c.customer_id
ORDER BY l.ltv DESC
LIMIT 100;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT date_trunc('month', created_at)::date AS cohort_month,
       COUNT(*) AS new_customers
FROM customers
GROUP BY 1
ORDER BY cohort_month DESC;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Calculate customer lifetime value (LTV) at one row per customer.
- Assign policy-driven segments and measure cohort revenue over lifecycle
  months.

## Vocabulary and concepts

- **LTV:** lifetime value under a stated revenue, margin, and refund definition.
- **Signup cohort:** customers grouped by their creation month.
- **Lifecycle offset:** elapsed whole months from cohort start to activity.

## Worked example / walkthrough

Collapse line items to order value, then orders to one customer LTV row. Left
join from customers if zero-order customers belong in the population. Reconcile
summed LTV with the chosen source total before assigning thresholds; segmenting
at a duplicated order-line grain would bias both counts and value.

## Exercises

Complete these in the [learner SQL](../day46_project1_ecommerce_part1.sql):

1. Define fixed LTV segments and analyze them by country.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
2. Calculate cohort revenue for offsets 0–12.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Predict how `NTILE` labels change when unrelated customers arrive.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Produce LTV, orders, AOV, and recency at customer grain.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Repair payment/item fanout in LTV.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. Retain no-order customers with an explicit zero-LTV policy.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.

Add a zero-order-customer test and state its segment.

## Self-check

- Does every customer contribute at most once to segmentation input?
- Are threshold ownership, refund/margin scope, and multi-year month offsets
  explicit?

## Next step

Continue to [Day 47 — cohort retention](day47_project1_ecommerce_part2.md).

## Deep dive and reference

## Project focus

- Calculate lifetime value at one row per customer.
- Assign explicit gold, silver, and bronze value segments.
- Measure cohort revenue over lifecycle months 0–12.

## How the learner script uses the current schema

The starter first collapses `order_items` to order value, then sums orders to
customer LTV and assigns `NTILE(4)` for exploration. Signup cohort is
`date_trunc('month', customers.created_at)`.

`orders.total_amount` is already reconciled from line-item net revenue by setup,
so it is also valid for customer LTV when the metric definition is gross booked
order value. The schema does not model a separate refund fact.

## Practice — match the learner prompts exactly

1. Choose and state numeric thresholds for gold, silver, and bronze LTV. Assign
   every customer, then report customer count, average LTV, and total LTV by
   `(country, ltv_segment)`.
2. Calculate revenue by signup `cohort_month` and lifecycle `month_offset` from
   0 through 12.

## Grain and date reasoning

- One customer must contribute once to the LTV segmentation input.
- Customers with no orders need a deliberate policy; a left join can retain
  them with zero LTV.
- A multi-year month offset must combine years and months from `age`; extracting
  only the month component wraps after 11.
- A missing cohort/offset row means no represented orders, not necessarily a
  stored zero.

## Validation and limits

- Treat segment thresholds as business policy, not universal cutoffs.
- Reconcile summed customer LTV to `SUM(orders.total_amount)`.
- Signup month defines cohort membership; order month defines lifecycle revenue.
- Synthetic data demonstrates the method, not a real customer-value benchmark.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-46 — Project1 Ecommerce Part1.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day46_project1_ecommerce_part1.md
- Answer-free learner SQL: sql/postgres-60day/day46_project1_ecommerce_part1.sql

The lesson concepts include LTV, Signup cohort, Lifecycle offset. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Collapse line items to order value, then orders to one customer LTV row. Left join from customers if zero-order customers belong in the population. Reconcile summed LTV with the chosen source total before assigning thresholds; segmenting at a duplicated order-line grain would bias both counts and value.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-46/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
