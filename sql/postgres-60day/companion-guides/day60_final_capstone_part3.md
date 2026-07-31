# Day 60 — Final Capstone, Part 3: End-to-End Sign-off

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 59 — stakeholder analytics](day59_final_capstone_part2.md)
  and completed evidence from the full SQL track
- **Artifacts:** [learner SQL](../day60_final_capstone_part3.sql) ·
  [solution reasoning](../solutions/day60_solutions.md) ·
  [executable solution](../solutions/day60_solutions.sql)

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

2. Open **SQL-60 — Final Capstone Part3** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-60/lesson/workspace/sql/postgres-60day/day60_final_capstone_part3.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day60_final_capstone_part3.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day60_final_capstone_part3.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Acceptance criterion, Evidence bundle, Handoff. Its worked SQL reads or creates `customers`, `orders`, `order_items`, `expenses`, `budgets`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Take customer LTV through the final evidence loop: state one-customer grain and revenue scope, run the view query, reconcile summed LTV with SUM(orders.totalamount), capture the result and environment, and record any exception with owner and next action. Apply the same loop to each deliverable.
The first runnable example has a concrete contract: Example 1 returns one row per the primary/business key of `v_dq_customers` from `v_dq_customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `*`. Reselect the returned key columns from `v_dq_customers`, reject duplicate keys when the grain is one row per entity, and check the stated row cap and sort direction only when this example includes them.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day60_final_capstone_part3.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT * FROM v_dq_customers;
```

**How to read it:** Example 1: Start with `v_dq_customers` in `FROM`/`JOIN`. The final `SELECT` displays `*`. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per the primary/business key of `v_dq_customers` from `v_dq_customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
SELECT * FROM v_dq_orders;
```

**How to read it:** Example 2: Start with `v_dq_orders` in `FROM`/`JOIN`. The final `SELECT` displays `*`. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per the primary/business key of `v_dq_orders` from `v_dq_orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

## Learning objectives

- Apply explicit acceptance criteria to data quality, business metrics,
  performance evidence, and documentation.
- Produce a handoff that separates verified results, limitations, and future
  production work.

## Vocabulary and concepts

- **Acceptance criterion:** an observable condition required for sign-off.
- **Evidence bundle:** reproducible query, environment, output, reconciliation,
  and interpretation.
- **Handoff:** documentation that lets another person operate, verify, and
  extend the work safely.

## Worked example / walkthrough

Take customer LTV through the final evidence loop: state one-customer grain and
revenue scope, run the view query, reconcile summed LTV with
`SUM(orders.total_amount)`, capture the result and environment, and record any
exception with owner and next action. Apply the same loop to each deliverable.

## Exercises

Complete these in the [learner SQL](../day60_final_capstone_part3.sql):

1. Classify snapshot-independent versus clock-dependent outputs.
   **Inputs/evidence:** For sql-60 Exercise 1, read from the inline `VALUES` fixture. Build the answer toward `object_name`, and `clock_contract`; keep `object_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-60 Exercise 1, expected output: one row per `object_name`. The final columns are `object_name`, and `clock_contract`.
   **Verify:** For sql-60 Exercise 1, reselect the returned keys directly from the source; require unique `object_name` where the expected grain is one row per key and confirm the projected `object_name`, and `clock_contract` against the inline `VALUES` fixture. Add one source row with a new `object_name`; verify the result gains exactly one row carrying that `object_name` value.
2. Build a named, severity-aware sign-off check result.
   **Inputs/evidence:** For sql-60 Exercise 2, read from `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-60 Exercise 2, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`. The final order is `severity, check_name`.
   **Verify:** For sql-60 Exercise 2, project `order_id` plus the raw source columns from `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
3. Remove repeated `LAG` calls while preserving first-month NULL growth.
   **Inputs/evidence:** For sql-60 Exercise 3, read from `orders`, and `v_monthly_revenue_refactored_solution`. Build the answer toward `month`, `revenue`, `previous_month`, and `month_over_month_growth`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-60 Exercise 3, expected output: one row per `month`. The final columns are `month`, `revenue`, `previous_month`, and `month_over_month_growth`. The final order is `month`.
   **Verify:** For sql-60 Exercise 3, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month`, `revenue`, `previous_month`, and `month_over_month_growth` against `orders`, and `v_monthly_revenue_refactored_solution`. Repeat with `NULL` in `LAG` and state whether the row is kept, rejected, or classified.
4. Mark an incomplete current month separately.
   **Inputs/evidence:** For sql-60 Exercise 4, read from `v_monthly_revenue_refactored_solution`. Build the answer toward `month`, `revenue`, and `is_incomplete_month`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-60 Exercise 4, expected output: one row per `month`. The final columns are `month`, `revenue`, and `is_incomplete_month`. The final order is `month DESC`.
   **Verify:** For sql-60 Exercise 4, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month`, `revenue`, and `is_incomplete_month` against `v_monthly_revenue_refactored_solution`. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
5. Capture and document before/after JSON plan evidence.
   **Inputs/evidence:** For sql-60 Exercise 5, run the underlying read-only query over `v_monthly_revenue_refactored_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-60 Exercise 5, expected output: at most 12 rows keyed by `plan_node`. The final columns are `plan_node`, `estimated_rows`, `actual_rows`, `loops`, and `buffers`. The final order is `month DESC`.
   **Verify:** For sql-60 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
6. Produce a release checklist covering operations and known limits.
   **Inputs/evidence:** For sql-60 Exercise 6, read from the inline `VALUES` fixture. Build the answer toward `item`, `evidence`, and `owner`; keep `evidence` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-60 Exercise 6, expected output: one row per `evidence`. The final columns are `item`, `evidence`, and `owner`.
   **Verify:** For sql-60 Exercise 6, reselect the returned keys directly from the source; require unique `evidence` where the expected grain is one row per key and confirm the projected `item`, `evidence`, and `owner` against the inline `VALUES` fixture. Add one source row with a new `evidence`; verify the result gains exactly one row carrying that `evidence` value.
7. Map metric lineage from source tables through validation.
   **Inputs/evidence:** For sql-60 Exercise 7, read from the inline `VALUES` fixture. Build the answer toward `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`; keep `metric_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-60 Exercise 7, expected output: one row per `metric_name`. The final columns are `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`.
   **Verify:** For sql-60 Exercise 7, reselect the returned keys directly from the source; require unique `metric_name` where the expected grain is one row per key and confirm the projected `metric_name`, `source_tables`, `transformation_grain`, and `validation_query` against the inline `VALUES` fixture. Add one source row with a new `metric_name`; verify the result gains exactly one row carrying that `metric_name` value.
8. Reconcile every dashboard subtotal to a simple control.
   **Inputs/evidence:** For sql-60 Exercise 8, read from `v_monthly_revenue_refactored_solution`, and `orders`. Compute `dashboard_total`, `source_total`, and `difference` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-60 Exercise 8, expected output: exactly one aggregate summary row. The final columns are `dashboard_total`, `source_total`, and `difference`.
   **Verify:** For sql-60 Exercise 8, evaluate each of `dashboard_total`, and `source_total` in a separate control `SELECT` over `v_monthly_revenue_refactored_solution`, and `orders`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
9. Test empty, one-row, NULL-heavy, and duplicate-key fixtures.
   **Inputs/evidence:** For sql-60 Exercise 9, read from `edge_fixture`. Build the answer toward `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows`; keep `fixture_rows` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-60 Exercise 9, expected output: one row per `fixture_rows`. The final columns are `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows`.
   **Verify:** For sql-60 Exercise 9, reselect the returned keys directly from the source; require unique `fixture_rows` where the expected grain is one row per key and confirm the projected `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows` against `edge_fixture`. Repeat with `NULL` in `fixture_rows`, and `null_email_rows` and state whether the row is kept, rejected, or classified.
10. Return `PASS`/`FAIL`/`NOT_RUN` for every acceptance criterion.
   **Inputs/evidence:** For sql-60 Exercise 10, read from `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders`. Build the answer toward `criterion`, and `result`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-60 Exercise 10, expected output: one row per `order_id`. The final columns are `criterion`, and `result`. The final order is `criterion`.
   **Verify:** For sql-60 Exercise 10, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `criterion`, and `result` against `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

Link every sign-off claim to executable evidence.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: Take customer LTV through the final evidence loop: state one-customer grain and revenue scope, run the view query, reconcile summed LTV with SUM(orders.totalamount), capture the result and environment, and record any exception with owner and next action. Apply the same loop to each deliverable.
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

- Does every sign-off claim have reproducible evidence and a named limitation
  or owner where applicable?
- Are tutorial views and indexes still rollback-only unless a separate reviewed
  migration explicitly persists them?

## Next step

Review any weak SQL areas, then combine both languages in the
[Python and PostgreSQL engineering bridge](../../../bridge/README.md). The
bridge expects at least Python Day 15 and SQL Day 15.

## Deep dive and reference

Day 60 defines acceptance criteria rather than discrete exercises. The final
submission connects reusable DQ checks, business views, stakeholder outputs,
performance evidence, and a written handoff.

## Deliverable 1 — Data quality

- `v_dq_customers`: total rows plus invalid email, country, and name counts.
- `v_dq_orders`: total rows plus negative totals and missing customers.
- Document every nonzero result with remediation, owner, and severity.

## Deliverable 2 — Core business views

- Customer LTV at one row per customer, retaining zero-order customers with a
  `LEFT JOIN` from `customers` to `orders` and `COALESCE(..., 0)`.
- Treat `orders.total_amount` as the authoritative revenue measure in this
  capstone. Do not recompute LTV from `order_items`: a line-based total can omit
  header-only orders or disagree with header-level adjustments.
- Monthly order revenue with previous month and safely divided month-over-month
  growth.
- Reconcile summed customer LTV to summed `orders.total_amount`; expected
  difference on the seed is zero.

## Deliverable 3 — Stakeholder outputs

- Finance: current-year budget versus actual by month/category.
- Marketing: active customers by signup cohort and lifecycle month 0–6. Select
  the six latest *distinct* signup months before expanding the lifecycle grid.
  Count every signup once in `cohort_size`, count a customer at most once per
  activity month, and report
  `active_customers / NULLIF(cohort_size, 0)` as `retention_rate`. Keeping the
  numerator and denominator visible makes the percentage auditable.
- Operations: an actual plan for recent units by product category.

## Deliverable 4 — Performance sign-off

Capture before/after `EXPLAIN (ANALYZE, BUFFERS)` for critical queries and record
dataset size, PostgreSQL version, indexes, timing, buffers, correctness check,
and decision. The requested under-10-second goal applies to the measured learner
machine/dataset; the compact seed does not prove production-scale performance.

## Deliverable 5 — Written handoff

Document DQ exceptions, model grain, join rationale, KPI definitions,
reconciliation, freshness-versus-speed tradeoffs, known limitations, and next
steps. Evidence must support every sign-off claim.

## State and safety

The learner file ends with `ROLLBACK`; its views and indexes do not persist.
Replace it with `COMMIT` only as a deliberate reviewed migration. Days 59–60 are
capstone criteria/checkpoints, so measured evidence and documentation are part
of the deliverable, not optional stretch work.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-60 — Final Capstone Part3.

I have completed the direct catalog prerequisite: `sql-59`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day60_final_capstone_part3.md
- Answer-free learner SQL: sql/postgres-60day/day60_final_capstone_part3.sql

Key terms to teach in context: Acceptance criterion, Evidence bundle, Handoff. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Take customer LTV through the final evidence loop: state one-customer grain and revenue scope, run the view query, reconcile summed LTV with SUM(orders.totalamount), capture the result and environment, and record any exception with owner and next action. Apply the same loop to each deliverable.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-60/ working copy. Never point setup, reset, DDL, or DML
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
