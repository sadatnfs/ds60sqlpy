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
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-46/lesson/workspace/sql/postgres-60day/day46_project1_ecommerce_part1.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. The key vocabulary for this lesson is LTV, Signup cohort, Lifecycle offset. Its worked SQL reads or creates `orders`, `order_items`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Collapse line items to order value, then orders to one customer LTV row. Left join from customers if zero-order customers belong in the population. Reconcile summed LTV with the chosen source total before assigning thresholds; segmenting at a duplicated order-line grain would bias both counts and value.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `customer_id`, `country`, and `segment`, capped at 100 rows with columns `customer_id`, `order_value`, `ltv`, `country`, `segment`, and `ltv_quartile` from `orders`, `order_items`, and `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `customer_id`, `country`, `segment`, `ltv`, and `ltv_quartile`. Independently group `orders`, `order_items`, `order_values`, `customers`, and `ltv` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

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

**How to read it:** Example 1: Start with `orders`, `order_items`, and `customers` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `customer_id`, `country`, `segment`, `ltv`, and `ltv_quartile`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `customer_id`, `country`, and `segment`, capped at 100 rows with columns `customer_id`, `order_value`, `ltv`, `country`, `segment`, and `ltv_quartile` from `orders`, `order_items`, and `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
SELECT date_trunc('month', created_at)::date AS cohort_month,
       COUNT(*) AS new_customers
FROM customers
GROUP BY 1
ORDER BY cohort_month DESC;
```

**How to read it:** Example 2: Start with `customers` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `cohort_month`, and `new_customers`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `cohort_month` with columns `cohort_month`, and `new_customers` from `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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
   **Inputs/evidence:** For sql-46 Exercise 1, read from `customers`, and `orders`. Build the answer toward `country`, `ltv_segment`, `customers`, `avg_ltv`, and `total_ltv`; keep `country`, and `ltv_segment` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-46 Exercise 1, expected output: one row per `(country, ltv_segment)`. The final columns are `country`, `ltv_segment`, `customers`, `avg_ltv`, and `total_ltv`. The final order is `country, avg_ltv DESC`.
   **Verify:** For sql-46 Exercise 1, independently aggregate `customers`, and `orders` by `country`, and `ltv_segment`; require one output row for every distinct `country`, and `ltv_segment` tuple and compare `customers`, `avg_ltv`, and `total_ltv` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customers`, `avg_ltv`, and `total_ltv` for the existing `country`, and `ltv_segment` tuple and verify the new tuple appears exactly once.
2. Calculate cohort revenue for offsets 0–12.
   **Inputs/evidence:** For sql-46 Exercise 2, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, and `revenue`; keep `cohort_month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-46 Exercise 2, expected output: one row per cohort and lifecycle month. The final columns are `cohort_month`, `month_offset`, and `revenue`. The final order is `cohort_month DESC, month_offset`.
   **Verify:** For sql-46 Exercise 2, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, and `revenue` values match those staged rows without unintended fanout or loss. Add one row for which `(month_offset BETWEEN 0 AND 12)` is true and one for which it is false; verify only the matching `cohort_month` value is returned.
3. Predict how `NTILE` labels change when unrelated customers arrive.
   **Inputs/evidence:** For sql-46 Exercise 3, read from `customers`, and `orders`. Build the answer toward `customer_id`, `ltv`, `population_quartile`, and `fixed_segment`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-46 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`, `ltv`, `population_quartile`, and `fixed_segment`. The final order is `ltv DESC, customer_id`.
   **Verify:** For sql-46 Exercise 3, choose one complete partition from `customers`, and `orders`; hand-calculate its first, middle, and final window values for `ltv`, `population_quartile`, and `fixed_segment`, then verify output keys remain `customer_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
4. Produce LTV, orders, AOV, and recency at customer grain.
   **Inputs/evidence:** For sql-46 Exercise 4, read from `orders`, and `customers`. Build the answer toward `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-46 Exercise 4, expected output: one row per `customer_id`. The final columns are `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order`. The final order is `ltv DESC, c.customer_id`.
   **Verify:** For sql-46 Exercise 4, project `customer_id` plus the raw source columns from `orders`, and `customers` at each join stage; record row count and distinct `customer_id`, then assert the final `customer_id`, `order_count`, `ltv`, `average_order_value`, and `days_since_last_order` values match those staged rows without unintended fanout or loss. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
5. Repair payment/item fanout in LTV.
   **Inputs/evidence:** For sql-46 Exercise 5, read from `orders`, and `order_items`. Build the answer toward `customer_id`, and `line_ltv`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-46 Exercise 5, expected output: one row per order before it becomes customer LTV. The final columns are `customer_id`, and `line_ltv`. The final order is `line_ltv DESC, customer_id`.
   **Verify:** For sql-46 Exercise 5, independently aggregate `orders`, and `order_items` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `line_ltv` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `line_ltv` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
6. Retain no-order customers with an explicit zero-LTV policy.
   **Inputs/evidence:** For sql-46 Exercise 6, read from `customers`, and `orders`. Build the answer toward `customer_id`, `ltv`, and `activity_status`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-46 Exercise 6, expected output: one row per `customer_id`. The final columns are `customer_id`, `ltv`, and `activity_status`. The final order is `c.customer_id`.
   **Verify:** For sql-46 Exercise 6, independently aggregate `customers`, and `orders` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `ltv`, and `activity_status` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `ltv`, and `activity_status` for the existing `customer_id` tuple and verify the new tuple appears exactly once.

Add a zero-order-customer test and state its segment.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Treat segment thresholds as business policy, not universal cutoffs.
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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

I have completed the direct catalog prerequisite: `sql-45`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day46_project1_ecommerce_part1.md
- Answer-free learner SQL: sql/postgres-60day/day46_project1_ecommerce_part1.sql

Key terms to teach in context: LTV, Signup cohort, Lifecycle offset. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Collapse line items to order value, then orders to one customer LTV row. Left join from customers if zero-order customers belong in the population. Reconcile summed LTV with the chosen source total before assigning thresholds; segmenting at a duplicated order-line grain would bias both counts and value.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-46/ working copy. Never point setup, reset, DDL, or DML
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
