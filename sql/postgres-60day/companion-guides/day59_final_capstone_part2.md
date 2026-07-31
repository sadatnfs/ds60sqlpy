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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-59/day59_final_capstone_part2.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
KPI contract, Funnel denominator, Scale hypothesis. Its worked SQL reads or creates `orders`, `order_items`, `customers`, `events`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Choose one KPI and write its contract before SQL. Build its lowest stable grain, add dimensions only after reconciliation, and return numerator/denominator beside any rate. Present the stakeholder table together with its control total and a limitation; repeat that evidence pattern for Finance and Marketing.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Deliver stakeholder-specific metrics with documented grain, denominator,
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
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Add funnel conversion rates and retain buyers without events.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Reconcile order totals, line revenue, and payments before KPI selection.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. Add direct attribution and reconcile purchases.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Compare customer/date and date/customer index orders.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
6. Write a complete metric contract for one KPI.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
7. Publish product-pair support, confidence, and lift with a minimum count.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
8. Assemble named cross-domain control totals for stakeholder sign-off.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Add a one-page metric dictionary and before/after evidence table.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day59_final_capstone_part2.md
- Answer-free learner SQL: sql/postgres-60day/day59_final_capstone_part2.sql

The lesson concepts include KPI contract, Funnel denominator, Scale hypothesis. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Choose one KPI and write its contract before SQL. Build its lowest stable grain, add dimensions only after reconciliation, and return numerator/denominator beside any rate. Present the stakeholder table together with its control total and a limitation; repeat that evidence pattern for Finance and Marketing.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-59/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
