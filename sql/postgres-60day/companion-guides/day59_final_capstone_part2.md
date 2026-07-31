# Day 59 — Final Capstone, Part 2: Stakeholder Analytics

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 58 — capstone ingestion and data quality](day58_final_capstone_part1.md)
- **Artifacts:** [learner SQL](../day59_final_capstone_part2.sql) ·
  [solution reasoning](../solutions/day59_solutions.md) ·
  [executable solution](../solutions/day59_solutions.sql)

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

2. Open **SQL-59 — Final Capstone Part2** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-59/lesson/workspace/sql/postgres-60day/day59_final_capstone_part2.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day59_final_capstone_part2.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day59_final_capstone_part2.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is KPI contract, Funnel denominator, Scale hypothesis. Its worked SQL reads or creates `orders`, `order_items`, `customers`, `events`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Choose one KPI and write its contract before SQL. Build its lowest stable grain, add dimensions only after reconciliation, and return numerator/denominator beside any rate. Present the stakeholder table together with its control total and a limitation; repeat that evidence pattern for Finance and Marketing.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `customer_id`, `order_id`, and `order_date`, capped at 100 rows with columns `customer_id`, `order_id`, `order_value`, `order_date`, `first_order_month`, and `ltv` from `orders`, `order_items`, and `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `segment`, `cohort_month`, `avg_ltv`, and `customers`. Independently group `orders`, `order_items`, `order_values`, `customers`, and `ltv` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day59_final_capstone_part2.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH order_values AS (
  SELECT o.customer_id, o.order_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value,
         o.order_date
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id, o.order_date
), ltv AS (
  SELECT customer_id,
         date_trunc('month', MIN(order_date))::date AS first_order_month,
         SUM(order_value) AS ltv
  FROM order_values
  GROUP BY customer_id
), cohort AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month,
         COALESCE(c.segment,'standard') AS segment
  FROM customers c
)
SELECT cohort.segment,
       cohort.cohort_month,
       ROUND(AVG(ltv.ltv),2) AS avg_ltv,
       COUNT(*) AS customers
FROM ltv
JOIN cohort ON cohort.customer_id = ltv.customer_id
GROUP BY cohort.segment, cohort.cohort_month
ORDER BY cohort.cohort_month DESC, avg_ltv DESC
LIMIT 100;
```

**How to read it:** Example 1: Start with `orders`, `order_items`, and `customers` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `segment`, `cohort_month`, `avg_ltv`, and `customers`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `customer_id`, `order_id`, and `order_date`, capped at 100 rows with columns `customer_id`, `order_id`, `order_value`, `order_date`, `first_order_month`, and `ltv` from `orders`, `order_items`, and `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
WITH ev AS (
  SELECT e.customer_id,
         MAX(CASE WHEN e.event_type='page_view'  THEN 1 ELSE 0 END) AS page_view,
         MAX(CASE WHEN e.event_type='add_to_cart' THEN 1 ELSE 0 END) AS add_to_cart,
         MAX(CASE WHEN e.event_type='checkout'   THEN 1 ELSE 0 END) AS checkout
  FROM events e
  WHERE e.event_time >= now() - interval '90 days'
  GROUP BY e.customer_id
), buyers AS (
  SELECT DISTINCT o.customer_id
  FROM orders o
  WHERE o.order_date >= now() - interval '90 days'
)
SELECT 
  SUM(page_view)    AS viewers,
  SUM(add_to_cart)  AS adders,
  SUM(checkout)     AS checkouts,
  (SELECT COUNT(*) FROM buyers) AS buyers
FROM ev;
```

**How to read it:** Example 2: Start with `events`, and `orders` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays the columns written in the final `SELECT`. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `customer_id` with columns `customer_id`, `page_view`, `add_to_cart`, `checkout`, `viewers`, and `adders` from `events`, and `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

## Learning objectives

- Deliver stakeholder-specific metrics with an explicit row grain, denominator,
  scope, and reconciliation.
- Pair performance recommendations with representative evidence and operational
  ownership.

## Vocabulary and concepts

- **KPI contract:** metric name, formula, grain, population, window, exclusions,
  and owner.
- **Funnel denominator:** the eligible population used at each conversion step.
- **Scale hypothesis:** a design expected to help at larger volume but still
  requiring representative validation.

## Worked example / walkthrough

Choose one KPI and write its contract before SQL. Build its lowest stable grain,
add dimensions only after reconciliation, and return numerator/denominator
beside any rate. Present the stakeholder table together with its control total
and a limitation; repeat that evidence pattern for Finance and Marketing.

## Exercises

Complete these in the [learner SQL](../day59_final_capstone_part2.sql):

1. State every LTV CTE's grain and its grain transition.
   **Inputs/evidence:** For sql-59 Exercise 1, read from the inline `VALUES` fixture. Build the answer toward `step_name`, `row_grain`, and `key_columns`; keep `step_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-59 Exercise 1, expected output: one row per `step_name`. The final columns are `step_name`, `row_grain`, and `key_columns`.
   **Verify:** For sql-59 Exercise 1, reselect the returned keys directly from the source; require unique `step_name` where the expected grain is one row per key and confirm the projected `step_name`, `row_grain`, and `key_columns` against the inline `VALUES` fixture. Add one source row with a new `step_name`; verify the result gains exactly one row carrying that `step_name` value.
2. Add funnel conversion rates and retain buyers without events.
   **Inputs/evidence:** For sql-59 Exercise 2, read from `orders`, `customers`, and `events`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-59 Exercise 2, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
   **Verify:** For sql-59 Exercise 2, project `order_id` plus the raw source columns from `orders`, `customers`, and `events` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
3. Reconcile order totals, line revenue, and payments before KPI selection.
   **Inputs/evidence:** For sql-59 Exercise 3, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-59 Exercise 3, expected output: at most 50 rows keyed by `order_id`. The final columns are `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`. The final order is `o.order_id`.
   **Verify:** For sql-59 Exercise 3, assert no more than 50 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_id`. Rejoin the returned keys to `order_items`, `payments`, and `orders` to confirm `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header` came from the same source rows. Run with 50 minus one and 50 plus one eligible rows; require the output cap of 50 while retaining `o.order_id`.
4. Add direct attribution and reconcile purchases.
   **Inputs/evidence:** For sql-59 Exercise 4, read from `orders`, and `events`. Build the answer toward `attribution_bucket`, and `purchases`; keep `attribution_bucket`, and `purchases` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-59 Exercise 4, expected output: one row per `attribution_bucket`, and `purchases`. The final columns are `attribution_bucket`, and `purchases`. The final order is `purchases DESC, attribution_bucket`.
   **Verify:** For sql-59 Exercise 4, independently aggregate `orders`, and `events` by `attribution_bucket`, and `purchases`; require one output row for every distinct `attribution_bucket`, and `purchases` tuple and compare `row_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `attribution_bucket`, and `purchases` tuple and verify the new tuple appears exactly once.
5. Compare customer/date and date/customer index orders.
   **Inputs/evidence:** For sql-59 Exercise 5, run the underlying read-only query over `orders`, and `idx_orders_date_customer_day59_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-59 Exercise 5, expected output: one row per `customer_id`. The final columns are `customer_id`, and `revenue`.
   **Verify:** For sql-59 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
6. Write a complete metric contract for one KPI.
   **Inputs/evidence:** For sql-59 Exercise 6, read from the inline `VALUES` fixture. Build the answer toward `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`; keep `metric_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-59 Exercise 6, expected output: one row per `metric_name`. The final columns are `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`.
   **Verify:** For sql-59 Exercise 6, reselect the returned keys directly from the source; require unique `metric_name` where the expected grain is one row per key and confirm the projected `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner` against the inline `VALUES` fixture. Add one source row with a new `metric_name`; verify the result gains exactly one row carrying that `metric_name` value.
7. Publish product-pair support, confidence, and lift with a minimum count.
   **Inputs/evidence:** For sql-59 Exercise 7, read from `order_items`. Build the answer toward `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift`; keep `order_item_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-59 Exercise 7, expected output: at most 20 rows keyed by `order_item_id`. The final columns are `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift`. The final order is `lift DESC, together DESC, product_a, product_b`.
   **Verify:** For sql-59 Exercise 7, assert no more than 20 rows, no duplicate `order_item_id`, and no adjacent pair that violates `lift DESC, together DESC, product_a, product_b`. Rejoin the returned keys to `order_items` to confirm `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `lift DESC, together DESC, product_a, product_b`.
8. Assemble named cross-domain control totals for stakeholder sign-off.
   **Inputs/evidence:** For sql-59 Exercise 8, read from `customers`, `orders`, `order_items`, and `payments`. Build the answer toward `control_name`, and `observed_value`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-59 Exercise 8, expected output: one row per `customer_id`. The final columns are `control_name`, and `observed_value`. The final order is `control_name`.
   **Verify:** For sql-59 Exercise 8, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `control_name`, and `observed_value` against `customers`, `orders`, `order_items`, and `payments`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

Add a one-page metric dictionary and before/after evidence table.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: Choose one KPI and write its contract before SQL. Build its lowest stable grain, add dimensions only after reconciliation, and return numerator/denominator beside any rate. Present the stakeholder table together with its control total and a limitation; repeat that evidence pattern for Finance and Marketing.
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

- Can another analyst reproduce every KPI from its written contract?
- Are campaign counts, pair counts, and funnel rates prevented from being
  summed across non-additive rows?

## Next step

Continue to [Day 60 — end-to-end sign-off](day60_final_capstone_part3.md).

## Deep dive and reference

Day 59 is a capstone checkpoint, not a pair of discrete exercises. It combines
KPI definitions, performance evidence, stakeholder outputs, and scale planning.

## Deliverable 1 — KPI suite

- LTV by signup cohort and customer segment, with customer count, average LTV,
  and total LTV.
- A 90-day customer-grain funnel for page view, add to cart, checkout, and
  purchase/order conversion, with explicit denominators.
- The top 20 distinct product pairs from order baskets, ranked by co-occurrence
  count (`together`), not by attributed pair revenue.

## Deliverable 2 — Performance evidence

Create candidate indexes only inside the rollback-only experiment, then capture
`EXPLAIN (ANALYZE, BUFFERS)` for the recent customer-revenue query. Save result
reconciliation, timing, buffers, row estimates, and plan choice. The compact
seed may correctly use a sequential scan.

## Deliverable 3 — Stakeholder outputs

- Finance: current-year budget, actual expense, and variance by category.
- Marketing: campaign touches within seven days before each customer's first
  order, counted as distinct assisted customers.

The marketing definition differs from Day 48's all-purchase event attribution.
Multiple campaigns can assist one customer, so campaign rows are not additive.

## Deliverable 4 — Large-scale design note

For a hypothetical 100M-row workload, identify candidate time partitions for
orders/events, prove partition-key filters for pruning, describe local/partial
indexes, and assign retention/maintenance ownership. Do not claim a benefit
without a representative plan.

## Sign-off limits

Record metric grain, time window, exclusions, reconciliation, and consumer for
every KPI. All candidate DDL rolls back; production changes require a separate
reviewed migration.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-59 — Final Capstone Part2.

I have completed the direct catalog prerequisite: `sql-58`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day59_final_capstone_part2.md
- Answer-free learner SQL: sql/postgres-60day/day59_final_capstone_part2.sql

Key terms to teach in context: KPI contract, Funnel denominator, Scale hypothesis. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Choose one KPI and write its contract before SQL. Build its lowest stable grain, add dimensions only after reconciliation, and return numerator/denominator beside any rate. Present the stakeholder table together with its control total and a limitation; repeat that evidence pattern for Finance and Marketing.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-59/ working copy. Never point setup, reset, DDL, or DML
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
