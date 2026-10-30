# Day 59: Final Capstone, Part 2: Stakeholder Analytics

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-59**. The
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
   `.learning/sql/sql-59/lesson/workspace/sql/postgres-60day/day59_final_capstone_part2.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-59
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 58; capstone ingestion and data quality](day58_final_capstone_part1.md)
- **Artifacts:** [learner SQL](../day59_final_capstone_part2.sql) ·
  [solution reasoning](../solutions/day59_solutions.md) ·
  [executable solution](../solutions/day59_solutions.sql)

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

These worked excerpts come from `sql/postgres-60day/day59_final_capstone_part2.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
WITH order_values AS (
  SELECT
    o.customer_id,
    o.order_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value,
    o.order_date
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.customer_id,
    o.order_id,
    o.order_date
),
ltv AS (
  SELECT
    customer_id,
    date_trunc('month', MIN(order_date))::date AS first_order_month,
    SUM(order_value) AS ltv
  FROM
    order_values
  GROUP BY
    customer_id
),
cohort AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at)::date AS cohort_month,
    COALESCE(c.segment, 'standard') AS segment
  FROM
    customers c
)
SELECT
  cohort.segment,
  cohort.cohort_month,
  ROUND(AVG(ltv.ltv), 2) AS avg_ltv,
  COUNT(*) AS customers
FROM
  ltv
  JOIN cohort ON cohort.customer_id = ltv.customer_id
GROUP BY
  cohort.segment,
  cohort.cohort_month
ORDER BY
  cohort.cohort_month DESC,
  avg_ltv DESC
LIMIT 100;
```

**How to read it:** Example 1: Start with `orders`, `order_items`, and `customers` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `segment`, `cohort_month`, `avg_ltv`, and `customers`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `customer_id`, `order_id`, and `order_date`, capped at 100 rows with columns `customer_id`, `order_id`, `order_value`, `order_date`, `first_order_month`, and `ltv` from `orders`, `order_items`, and `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
WITH viewed_stage AS (
  SELECT
    c.customer_id,
    MIN(e.event_time) FILTER (WHERE e.event_type = 'page_view') AS viewed_at
  FROM
    customers c
    LEFT JOIN events e ON e.customer_id = c.customer_id
      AND e.event_time >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY
    c.customer_id
),
added_stage AS (
  SELECT
    viewed.customer_id,
    viewed.viewed_at,
    MIN(event.event_time) AS added_at
  FROM
    viewed_stage viewed
    LEFT JOIN events event ON event.customer_id = viewed.customer_id
      AND event.event_type = 'add_to_cart'
      AND event.event_time >= viewed.viewed_at
  GROUP BY
    viewed.customer_id,
    viewed.viewed_at
),
checkout_stage AS (
  SELECT
    added.customer_id,
    added.viewed_at,
    added.added_at,
    MIN(event.event_time) AS checkout_at
  FROM
    added_stage added
    LEFT JOIN events event ON event.customer_id = added.customer_id
      AND event.event_type = 'checkout'
      AND event.event_time >= added.added_at
  GROUP BY
    added.customer_id,
    added.viewed_at,
    added.added_at
),
purchase_stage AS (
  SELECT
    checkout.customer_id,
    checkout.viewed_at,
    checkout.added_at,
    checkout.checkout_at,
    MIN(customer_order.order_date) AS purchased_at
  FROM
    checkout_stage checkout
    LEFT JOIN orders customer_order ON customer_order.customer_id = checkout.customer_id
      AND customer_order.order_date >= checkout.checkout_at
      AND customer_order.order_date >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY
    checkout.customer_id,
    checkout.viewed_at,
    checkout.added_at,
    checkout.checkout_at
),
activity AS (
  SELECT
    customer_id,
    viewed_at IS NOT NULL AS viewed,
    added_at IS NOT NULL
    AND added_at >= viewed_at AS added,
    checkout_at IS NOT NULL
    AND checkout_at >= added_at AS checked_out,
    purchased_at IS NOT NULL
    AND purchased_at >= checkout_at AS bought
  FROM
    purchase_stage
)
SELECT
  COUNT(*) FILTER (WHERE viewed) AS viewers,
  COUNT(*) FILTER (WHERE added) AS adders,
  COUNT(*) FILTER (WHERE checked_out) AS checkouts,
  COUNT(*) FILTER (WHERE bought) AS buyers
FROM
  activity;
```

**How to read it:** `viewed_stage` retains one row per customer and records the
earliest recent page view. Each later `LEFT JOIN` searches only at or after its
prior timestamp. A customer who checks out before adding to cart therefore does
not enter the ordered checkout population. `activity` turns the four timestamps
into nested Boolean populations, and aggregate `FILTER` returns one summary row.
This is different from independently asking whether each event happened at any
time; independent reach can increase between stages and is not a funnel.

**Expected result/shape:** Exactly one row with `viewers`, `adders`, `checkouts`,
and `buyers`. The invariant is `buyers <= checkouts <= adders <= viewers`.
Inspect one customer's four timestamps before trusting the aggregate, and add a
counterexample whose checkout precedes add-to-cart; that checkout must not count.

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
   **Inputs/evidence:** For sql-59 Exercise 2, derive `viewed_at`, `added_at`, `checkout_at`, and `purchased_at` per customer over the same trailing-90-day window.
   **Expected result/shape:** For sql-59 Exercise 2, expected output: exactly one summary row with ordered stage counts, `buyers_without_view`, and three conversion rates whose denominators are the preceding ordered populations.
   **Verify:** For sql-59 Exercise 2, require `added_at >= viewed_at`, `checkout_at >= added_at`, and `purchased_at >= checkout_at`. Prove `buyers <= checkouts <= adders <= viewers`; every nonzero stage rate must be between zero and one.
3. Reconcile order totals, line revenue, and payments before KPI selection.
   **Inputs/evidence:** For sql-59 Exercise 3, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-59 Exercise 3, expected output: at most 50 rows keyed by `order_id`. The final columns are `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`. The final order is `o.order_id`.
   **Verify:** For sql-59 Exercise 3, assert no more than 50 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_id`. Rejoin the returned keys to `order_items`, `payments`, and `orders` to confirm `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header` came from the same source rows. Run with 50 minus one and 50 plus one eligible rows; require the output cap of 50 while retaining `o.order_id`.
4. Add direct attribution and reconcile purchases.
   **Inputs/evidence:** For sql-59 Exercise 4, start from `orders` and choose at most one event whose `event_type` is in the declared marketing-touch whitelist (`page_view`, `add_to_cart`, `checkout`), whose campaign metadata is present, and whose timestamp is in the preceding seven-day half-open window.
   **Expected result/shape:** For sql-59 Exercise 4, expected output: one row per `attribution_bucket`, with `purchases`; every order contributes to exactly one campaign bucket or `(direct)`. The final order is `purchases DESC, attribution_bucket`.
   **Verify:** For sql-59 Exercise 4, assert that `SUM(purchases)` equals `COUNT(*)` from `orders`. Add a tagged non-touch event and prove the attribution result is unchanged; then add two qualifying touches for one order and prove the latest timestamp, with `event_id` as tie-breaker, wins exactly once.
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

Continue to [Day 60; end-to-end sign-off](day60_final_capstone_part3.md).

## Deep dive and reference

Day 59 is a capstone checkpoint, not a pair of discrete exercises. It combines
KPI definitions, performance evidence, stakeholder outputs, and scale planning.

## Deliverable 1: KPI suite

- LTV by signup cohort and customer segment, with customer count, average LTV,
  and total LTV.
- A 90-day customer-grain funnel for page view, add to cart, checkout, and
  purchase/order conversion, with explicit denominators.
- The top 20 distinct product pairs from order baskets, ranked by co-occurrence
  count (`together`), not by attributed pair revenue.

## Deliverable 2: Performance evidence

Create candidate indexes only inside the rollback-only experiment, then capture
`EXPLAIN (ANALYZE, BUFFERS)` for the recent customer-revenue query. Save result
reconciliation, timing, buffers, row estimates, and plan choice. The compact
seed may correctly use a sequential scan.

## Deliverable 3: Stakeholder outputs

- Finance: current-year budget, actual expense, and variance by category.
- Marketing: campaign touches within seven days before each customer's first
  order, counted as distinct assisted customers. Only the declared touch types
  (`page_view`, `add_to_cart`, and `checkout`) qualify; a campaign tag on an
  unrelated event must not create marketing credit.

The marketing definition differs from Day 48's all-purchase event attribution.
Multiple campaigns can assist one customer, so campaign rows are not additive.

## Deliverable 4: Large-scale design note

For a hypothetical 100M-row workload, identify candidate time partitions for
orders/events, prove partition-key filters for pruning, describe local/partial
indexes, and assign retention/maintenance ownership. Do not claim a benefit
without a representative plan.

## Sign-off limits

Record metric grain, time window, exclusions, reconciliation, and consumer for
every KPI. All candidate DDL rolls back; production changes require a separate
reviewed migration.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

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
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
