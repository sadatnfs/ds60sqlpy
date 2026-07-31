# Day 59 Solution — Integrated Stakeholder Analytics


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day59_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day59_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are KPI contract, Funnel denominator, Scale hypothesis. Its worked-model focus is:
Choose one KPI and write its contract before SQL. Build its lowest stable grain, add dimensions only after reconciliation, and return numerator/denominator beside any rate. Present the stakeholder table together with its control total and a limitation; repeat that evidence pattern for Finance and Marketing.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

Day 59 is a capstone checkpoint, not a pair of discrete exercises. Its
deliverables are a reconciled KPI suite, performance evidence, stakeholder
queries, and a large-scale design note. The canonical executable checkpoint is
[`day59_solutions.sql`](day59_solutions.sql).

## Deliverable 1 — Business KPI suite

### LTV by signup cohort and segment

```sql
SET search_path TO training, public;

WITH customer_ltv AS (
  SELECT c.customer_id,
         c.country,
         COALESCE(c.segment, 'standard') AS segment,
         date_trunc('month', c.created_at)::date AS cohort_month,
         COALESCE(SUM(o.total_amount), 0) AS ltv
  FROM customers c
  LEFT JOIN orders o USING (customer_id)
  GROUP BY c.customer_id, c.country, c.segment, date_trunc('month', c.created_at)
)
SELECT cohort_month,
       segment,
       COUNT(*) AS customers,
       ROUND(AVG(ltv), 2) AS avg_ltv,
       ROUND(SUM(ltv), 2) AS total_ltv
FROM customer_ltv
GROUP BY cohort_month, segment
ORDER BY cohort_month DESC, total_ltv DESC;
```

Expected grain: one row per `(cohort_month, segment)`, including customers with
zero orders.

### Ninety-day conversion funnel

```sql
SET search_path TO training, public;

WITH activity AS (
  SELECT c.customer_id,
         BOOL_OR(e.event_type = 'page_view') AS viewed,
         BOOL_OR(e.event_type = 'add_to_cart') AS added,
         BOOL_OR(e.event_type = 'checkout') AS checked_out,
         EXISTS (
           SELECT 1
           FROM orders o
           WHERE o.customer_id = c.customer_id
             AND o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
         ) AS bought
  FROM customers c
  LEFT JOIN events e
    ON e.customer_id = c.customer_id
   AND e.event_time >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY c.customer_id
)
SELECT COUNT(*) FILTER (WHERE viewed) AS viewers,
       COUNT(*) FILTER (WHERE added) AS adders,
       COUNT(*) FILTER (WHERE checked_out) AS checkouts,
       COUNT(*) FILTER (WHERE bought) AS buyers,
       ROUND(
         COUNT(*) FILTER (WHERE bought)::numeric
           / NULLIF(COUNT(*) FILTER (WHERE viewed), 0),
         4
       ) AS viewer_to_buyer_rate
FROM activity;
```

Expected shape: one row. Every funnel stage is measured at customer grain, but
the synthetic data does not enforce strict stage ordering.

### Product-pair affinity

The learner script already supplies the runnable market-basket query. Its
deliverable is the 20 most frequent distinct product pairs. Deduplicate
`(order_id, product_id)` first and enforce `a.product_id < b.product_id`; this
prevents self-pairs and reversed duplicates. The metric is co-occurrence count,
despite the starter comment saying “revenue.”

## Deliverable 2 — Performance evidence

```sql
BEGIN;
SET search_path TO training, public;

CREATE INDEX idx_orders_customer_date_day59_solution
  ON orders(customer_id, order_date) INCLUDE (total_amount);

EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, SUM(total_amount) AS revenue
FROM orders
WHERE order_date >= CURRENT_TIMESTAMP - interval '180 days'
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 50;

ROLLBACK;
```

Save the actual plan, execution time, buffer counts, and result reconciliation.
The compact seed may correctly use a sequential scan; index presence does not
guarantee index use.

## Deliverable 3 — Stakeholder queries

### Finance: YTD budget versus actual

```sql
SET search_path TO training, public;

WITH actual AS (
  SELECT category, SUM(amount) AS actual
  FROM expenses
  WHERE expense_date >= date_trunc('year', CURRENT_DATE)
  GROUP BY category
), budget AS (
  SELECT category, SUM(amount) AS budget
  FROM budgets
  WHERE period >= date_trunc('year', CURRENT_DATE)
  GROUP BY category
)
SELECT COALESCE(a.category, b.category) AS category,
       ROUND(COALESCE(b.budget, 0), 2) AS budget,
       ROUND(COALESCE(a.actual, 0), 2) AS actual,
       ROUND(COALESCE(a.actual, 0) - COALESCE(b.budget, 0), 2) AS variance
FROM actual a
FULL OUTER JOIN budget b USING (category)
ORDER BY category;
```

Expected grain: one row per category found in actuals or budget.

### Marketing: campaign-assisted purchases

The learner query anchors on each customer's first order and counts distinct
customers with a campaign touch in the preceding seven days. Document that
definition: it is first-purchase assistance, not all-purchase event attribution
from Day 48. Multiple campaigns can assist one customer, so campaign rows are
not additive.

## Deliverable 4 — Large-scale design note

For a hypothetical 100M-row deployment, record:

- candidate range partition keys (`orders.order_date`, `events.event_time`);
- proof that critical predicates constrain those keys for pruning;
- local/partial indexes on hot recent partitions;
- retention and partition-maintenance ownership; and
- an observed representative-scale plan, not an assumed benefit.

## Capstone checkpoint limits

- Days 59–60 provide sign-off criteria rather than neatly isolated exercises.
- The current executable solution selects representative KPI, finance, and
  performance checks; the learner starter contains the product-pair and
  marketing queries that must also be discussed in the final write-up.
- All DDL in the solution transaction rolls back. Production changes require a
  separate reviewed migration.

## Exercise 1 — Make every grain transition explicit

The executable `grain_map` states the key and row meaning for order values,
customer LTV, and cohort/segment summary. A lower-grain join after aggregation
would invalidate the metric.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 1, read from the inline `VALUES` fixture. Build the answer toward `step_name`, `row_grain`, and `key_columns`; keep `step_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-59 Exercise 1, expected output: one row per `step_name`. The final columns are `step_name`, `row_grain`, and `key_columns`.
- **Independent verification:** For sql-59 Exercise 1, reselect the returned keys directly from the source; require unique `step_name` where the expected grain is one row per key and confirm the projected `step_name`, `row_grain`, and `key_columns` against the inline `VALUES` fixture. Add one source row with a new `step_name`; verify the result gains exactly one row carrying that `step_name` value.
- **Intermediate relation check:** For sql-59 Exercise 1, select `step_name` from the inline `VALUES` fixture before adding derived columns.
- **Clause check:** For sql-59 Exercise 1, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `step_name`, and finish with `step_name`, `row_grain`, and `key_columns`.
- **Alternative/trade-off:** For sql-59 Exercise 1, the chosen form is justified by this lesson-specific rationale: The executable `grain_map` states the key and row meaning for order values, customer LTV, and cohort/segment summary. Evaluate another form against the concrete expected result (one row per `step_name`) and the verification above.
- **Edge case:** Add one source row with a new `step_name`; verify the result gains exactly one row carrying that `step_name` value.

## Exercise 2 — Calculate funnel rates with a stable population

Start from all customers, left-join recent events, and use EXISTS for recent
purchases. Buyers without a page-view stay visible. Each rate divides by the
preceding stage with `NULLIF` protection.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 2, read from `orders`, `customers`, and `events`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-59 Exercise 2, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
- **Independent verification:** For sql-59 Exercise 2, project `order_id` plus the raw source columns from `orders`, `customers`, and `events` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-59 Exercise 2, run `activity`, and `counts` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-59 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `GROUP BY`, and `SELECT`. Read only those operations: begin at `orders`, `customers`, and `events`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
- **Alternative/trade-off:** For sql-59 Exercise 2, the chosen form is justified by this lesson-specific rationale: Start from all customers, left-join recent events, and use EXISTS for recent purchases. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 3 — Reconcile candidate money measures

Line values and payments each aggregate to `order_id` before joining orders.
The answer retains stored total, calculated line total, paid amount, and both
differences so stakeholders can choose a named measure.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 3, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-59 Exercise 3, expected output: at most 50 rows keyed by `order_id`. The final columns are `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`. The final order is `o.order_id`.
- **Independent verification:** For sql-59 Exercise 3, assert no more than 50 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_id`. Rejoin the returned keys to `order_items`, `payments`, and `orders` to confirm `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header` came from the same source rows. Run with 50 minus one and 50 plus one eligible rows; require the output cap of 50 while retaining `o.order_id`.
- **Intermediate relation check:** For sql-59 Exercise 3, run `lines`, and `paid` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-59 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `order_items`, `payments`, and `orders`, preserve one row per `order_id`, and finish with `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header` ordered by `o.order_id`.
- **Alternative/trade-off:** For sql-59 Exercise 3, the chosen form is justified by this lesson-specific rationale: Line values and payments each aggregate to `order_id` before joining orders. Evaluate another form against the concrete expected result (at most 50 rows keyed by `order_id`) and the verification above.
- **Edge case:** Run with 50 minus one and 50 plus one eligible rows; require the output cap of 50 while retaining `o.order_id`.

## Exercise 4 — Include direct attribution

Start from purchases and choose at most one latest qualifying touch with a
LATERAL query. Missing touches become `(direct)`, so attribution counts
reconcile to the purchase population.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 4, read from `orders`, and `events`. Build the answer toward `attribution_bucket`, and `purchases`; keep `attribution_bucket`, and `purchases` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-59 Exercise 4, expected output: one row per `attribution_bucket`, and `purchases`. The final columns are `attribution_bucket`, and `purchases`. The final order is `purchases DESC, attribution_bucket`.
- **Independent verification:** For sql-59 Exercise 4, independently aggregate `orders`, and `events` by `attribution_bucket`, and `purchases`; require one output row for every distinct `attribution_bucket`, and `purchases` tuple and compare `row_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `attribution_bucket`, and `purchases` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-59 Exercise 4, start with the first relation in `orders`, and `events`; after each join, record total rows and distinct `attribution_bucket`, and `purchases` so the exact fanout or loss is visible.
- **Clause check:** For sql-59 Exercise 4, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `orders`, and `events`, preserve one row per `attribution_bucket`, and `purchases`, and finish with `attribution_bucket`, and `purchases` ordered by `purchases DESC, attribution_bucket`.
- **Alternative/trade-off:** For sql-59 Exercise 4, the chosen form is justified by this lesson-specific rationale: Start from purchases and choose at most one latest qualifying touch with a LATERAL query. Evaluate another form against the concrete expected result (one row per `attribution_bucket`, and `purchases`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `attribution_bucket`, and `purchases` tuple and verify the new tuple appears exactly once.

## Exercise 5 — Compare index column order

`(customer_id, order_date)` supports one customer's history; `(order_date,
customer_id)` better anchors a global date-bound scan. EXPLAIN evidence is
environment-specific and both indexes add write cost.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 5, run the underlying read-only query over `orders`, and `idx_orders_date_customer_day59_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-59 Exercise 5, expected output: one row per `customer_id`. The final columns are `customer_id`, and `revenue`.
- **Independent verification:** For sql-59 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-59 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.
- **Clause check:** For sql-59 Exercise 5, the solution actually uses `FROM`, `WHERE`, `GROUP BY`, and `SELECT`. Read only those operations: begin at `orders`, and `idx_orders_date_customer_day59_solution`, preserve one row per `customer_id`, and finish with `customer_id`, and `revenue`.
- **Alternative/trade-off:** For sql-59 Exercise 5, the chosen form is justified by this lesson-specific rationale: `(customer_id, order_date)` supports one customer's history; `(order_date, customer_id)` better anchors a global date-bound scan. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 6 — Publish a metric contract

The answer records metric name, grain, numerator, denominator, UTC window, NULL
policy, exclusions, and owner as queryable values. This prevents silent semantic
changes between teams.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 6, read from the inline `VALUES` fixture. Build the answer toward `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`; keep `metric_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-59 Exercise 6, expected output: one row per `metric_name`. The final columns are `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`.
- **Independent verification:** For sql-59 Exercise 6, reselect the returned keys directly from the source; require unique `metric_name` where the expected grain is one row per key and confirm the projected `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner` against the inline `VALUES` fixture. Add one source row with a new `metric_name`; verify the result gains exactly one row carrying that `metric_name` value.
- **Intermediate relation check:** For sql-59 Exercise 6, select `metric_name` from the inline `VALUES` fixture before adding derived columns.
- **Clause check:** For sql-59 Exercise 6, the solution actually uses `WITH`, `FROM`, and `SELECT`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `metric_name`, and finish with `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`.
- **Alternative/trade-off:** For sql-59 Exercise 6, the chosen form is justified by this lesson-specific rationale: The answer records metric name, grain, numerator, denominator, UTC window, NULL policy, exclusions, and owner as queryable values. Evaluate another form against the concrete expected result (one row per `metric_name`) and the verification above.
- **Edge case:** Add one source row with a new `metric_name`; verify the result gains exactly one row carrying that `metric_name` value.

## Exercise 7 — Publish defensible basket metrics

Distinct baskets feed support, confidence, and lift. A minimum pair count limits
noise, and product IDs resolve ordering ties deterministically.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 7, read from `order_items`. Build the answer toward `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift`; keep `order_item_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-59 Exercise 7, expected output: at most 20 rows keyed by `order_item_id`. The final columns are `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift`. The final order is `lift DESC, together DESC, product_a, product_b`.
- **Independent verification:** For sql-59 Exercise 7, assert no more than 20 rows, no duplicate `order_item_id`, and no adjacent pair that violates `lift DESC, together DESC, product_a, product_b`. Rejoin the returned keys to `order_items` to confirm `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `lift DESC, together DESC, product_a, product_b`.
- **Intermediate relation check:** For sql-59 Exercise 7, run `baskets`, `totals`, `product_baskets`, and `pairs` one at a time. Record each CTE's row count and `order_item_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-59 Exercise 7, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `order_items`, preserve one row per `order_item_id`, and finish with `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift` ordered by `lift DESC, together DESC, product_a, product_b`.
- **Alternative/trade-off:** For sql-59 Exercise 7, the chosen form is justified by this lesson-specific rationale: Distinct baskets feed support, confidence, and lift. Evaluate another form against the concrete expected result (at most 20 rows keyed by `order_item_id`) and the verification above.
- **Edge case:** Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `lift DESC, together DESC, product_a, product_b`.

## Exercise 8 — Assemble cross-domain controls

Named counts and money totals provide a small sign-off surface for customer,
order, line, and payment domains. Any non-equivalence must be explained by a
declared metric definition rather than hidden.

### Reasoning and verification

- **Inputs/evidence:** For sql-59 Exercise 8, read from `customers`, `orders`, `order_items`, and `payments`. Build the answer toward `control_name`, and `observed_value`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-59 Exercise 8, expected output: one row per `customer_id`. The final columns are `control_name`, and `observed_value`. The final order is `control_name`.
- **Independent verification:** For sql-59 Exercise 8, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `control_name`, and `observed_value` against `customers`, `orders`, `order_items`, and `payments`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-59 Exercise 8, check `control_name` before applying the row cap.
- **Clause check:** For sql-59 Exercise 8, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, `orders`, `order_items`, and `payments`, preserve one row per `customer_id`, and finish with `control_name`, and `observed_value` ordered by `control_name`.
- **Alternative/trade-off:** For sql-59 Exercise 8, the chosen form is justified by this lesson-specific rationale: Named counts and money totals provide a small sign-off surface for customer, order, line, and payment domains. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
