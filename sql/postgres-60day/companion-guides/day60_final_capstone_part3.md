# Day 60: Final Capstone, Part 3: End-to-End Sign-off

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 59; stakeholder analytics](day59_final_capstone_part2.md)
  and completed evidence from the full SQL track
- **Artifacts:** [learner SQL](../day60_final_capstone_part3.sql) ·
  [solution reasoning](../solutions/day60_solutions.md) ·
  [executable solution](../solutions/day60_solutions.sql)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-60**. The
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
   `.learning/sql/sql-60/lesson/workspace/sql/postgres-60day/day60_final_capstone_part3.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-60
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

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

## Deliverable 1: Data quality

- `v_dq_customers`: total rows plus invalid email, country, and name counts.
- `v_dq_orders`: total rows plus negative totals and missing customers.
- Document every nonzero result with remediation, owner, and severity.

## Deliverable 2: Core business views

- Customer LTV at one row per customer, retaining zero-order customers with a
  `LEFT JOIN` from `customers` to `orders` and `COALESCE(..., 0)`.
- Treat `orders.total_amount` as the authoritative revenue measure in this
  capstone. Do not recompute LTV from `order_items`: a line-based total can omit
  header-only orders or disagree with header-level adjustments.
- Monthly order revenue with previous month and safely divided month-over-month
  growth.
- Reconcile summed customer LTV to summed `orders.total_amount`; expected
  difference on the seed is zero.

## Deliverable 3: Stakeholder outputs

- Finance: current-year budget versus actual by month/category.
- Marketing: active customers by signup cohort and lifecycle month 0–6. Select
  the six latest *distinct* signup months before expanding the lifecycle grid.
  Count every signup once in `cohort_size`, count a customer at most once per
  activity month, and report
  `active_customers / NULLIF(cohort_size, 0)` as `retention_rate`. Keeping the
  numerator and denominator visible makes the percentage auditable.
- Operations: an actual plan for recent units by product category.

## Deliverable 4: Performance sign-off

Capture before/after `EXPLAIN (ANALYZE, BUFFERS)` for critical queries and record
dataset size, PostgreSQL version, indexes, timing, buffers, correctness check,
and decision. The requested under-10-second goal applies to the measured learner
machine/dataset; the compact seed does not prove production-scale performance.

## Deliverable 5: Written handoff

Document DQ exceptions, model grain, join rationale, KPI definitions,
reconciliation, freshness-versus-speed tradeoffs, known limitations, and next
steps. Evidence must support every sign-off claim.

## State and safety

The learner file ends with `ROLLBACK`; its views and indexes do not persist.
Replace it with `COMMIT` only as a deliberate reviewed migration. Days 59–60 are
capstone criteria/checkpoints, so measured evidence and documentation are part
of the deliverable, not optional stretch work.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

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
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
