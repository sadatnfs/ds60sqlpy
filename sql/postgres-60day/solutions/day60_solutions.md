# Day 60 Solution — End-to-End Capstone Sign-off


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day60_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day60_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Acceptance criterion, Evidence bundle, Handoff. Its worked-model focus is:
Take customer LTV through the final evidence loop: state one-customer grain and revenue scope, run the view query, reconcile summed LTV with SUM(orders.totalamount), capture the result and environment, and record any exception with owner and next action. Apply the same loop to each deliverable.

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

Day 60 has acceptance criteria, not discrete exercises. The final submission
must connect data quality, transformation, analytics, performance evidence, and
documented tradeoffs. The executable reference is
[`day60_solutions.sql`](day60_solutions.sql).

## Success criteria

Sign off only when:

1. critical queries complete in under 10 seconds **on the learner's measured
   dataset and machine**;
2. data-quality checks pass or every exception has an owner and explanation;
3. business totals reconcile across views and source tables; and
4. the write-up records grain, assumptions, before/after plans, compromises,
   known limits, and next steps.

The compact seed makes the 10-second target easy; it does not prove
production-scale performance.

## Deliverable 1 — Reusable DQ views

The learner creates `v_dq_customers` and `v_dq_orders`. The reference solution
uses a suffixed customer view so it cannot collide with a learner's view:

```sql
BEGIN;
SET search_path TO training, public;

CREATE VIEW v_dq_customers_solution AS
SELECT COUNT(*) AS total_rows,
       COUNT(*) FILTER (
         WHERE email IS NULL
            OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
       ) AS invalid_email,
       COUNT(*) FILTER (WHERE country !~ '^[A-Z]{2}$') AS invalid_country,
       COUNT(*) FILTER (WHERE trim(full_name) = '') AS invalid_name
FROM customers;

SELECT * FROM v_dq_customers_solution;

SELECT COUNT(*) AS total_rows,
       COUNT(*) FILTER (WHERE total_amount < 0) AS negative_amounts,
       COUNT(*) FILTER (WHERE customer_id IS NULL) AS missing_customer
FROM orders;

ROLLBACK;
```

Expected shape: one customer summary row and one order summary row. The course
seed should report zero failures.

## Deliverable 2 — Core business views and reconciliation

```sql
BEGIN;
SET search_path TO training, public;

CREATE VIEW v_customer_ltv_solution AS
SELECT c.customer_id,
       c.country,
       COALESCE(SUM(o.total_amount), 0)::numeric(14,2) AS ltv
FROM customers c
LEFT JOIN orders o USING (customer_id)
GROUP BY c.customer_id, c.country;

CREATE VIEW v_monthly_revenue_solution AS
WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
)
SELECT month,
       revenue,
       LAG(revenue) OVER (ORDER BY month) AS previous_month,
       ROUND(
         (revenue - LAG(revenue) OVER (ORDER BY month))
           / NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
         4
       ) AS month_over_month_growth
FROM monthly;

SELECT (SELECT ROUND(SUM(ltv), 2) FROM v_customer_ltv_solution)
         AS customer_ltv_total,
       (SELECT ROUND(SUM(total_amount), 2) FROM orders) AS order_total,
       (SELECT ROUND(SUM(ltv), 2) FROM v_customer_ltv_solution)
         - (SELECT ROUND(SUM(total_amount), 2) FROM orders) AS difference;

ROLLBACK;
```

Expected reconciliation: `difference = 0.00`. The monthly view has one row per
represented order month; it does not manufacture missing months.

## Deliverable 3 — Stakeholder-ready outputs

The learner file contains three runnable outputs:

- Finance: YTD actual, budget, and variance at `(month, category)` grain.
- Marketing: active customers by signup cohort and lifecycle month 0–6. A full
  retention rate additionally needs the cohort-size denominator from Day 47.
- Operations: an `EXPLAIN` of recent units by product category.

For each output, record the consumer, business definition, result grain,
freshness expectation, and at least one reconciliation or sanity check.

## Deliverable 4 — Performance sign-off

```sql
BEGIN;
SET search_path TO training, public;

CREATE INDEX idx_orders_date_day60_solution ON orders(order_date);
CREATE INDEX idx_orders_customer_day60_solution ON orders(customer_id);
CREATE INDEX idx_order_items_order_day60_solution ON order_items(order_id);
CREATE INDEX idx_expenses_date_day60_solution ON expenses(expense_date);
CREATE INDEX idx_budgets_period_day60_solution ON budgets(period);

CREATE VIEW v_monthly_revenue_solution AS
WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
)
SELECT month,
       revenue,
       LAG(revenue) OVER (ORDER BY month) AS previous_month,
       ROUND(
         (revenue - LAG(revenue) OVER (ORDER BY month))
           / NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
         4
       ) AS month_over_month_growth
FROM monthly;

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM v_monthly_revenue_solution
ORDER BY month DESC
LIMIT 12;

ROLLBACK;
```

Capture actual execution time and buffers before and after candidate indexes.
The transaction rolls back both views and indexes.

## Deliverable 5 — Written sign-off

The final write-up must cover:

- DQ exceptions and remediation;
- source entities, analytical grain, and join rationale;
- KPI definitions and reconciliation evidence;
- before/after `EXPLAIN (ANALYZE, BUFFERS)` evidence;
- freshness versus performance tradeoffs;
- known limitations and next steps; and
- whether the learner-file success criteria were met on the measured setup.

Do not replace evidence with “an index should help.” A complete capstone records
the query, dataset size, environment, plan, timing, correctness check, and
decision.

## Safety and state assumptions

- Both learner and solution files end with `ROLLBACK`; replace it with `COMMIT`
  only in a deliberate migration after reviewing object names and ownership.
- `CREATE VIEW` without `OR REPLACE` is intentional in the reference transaction
  and expects a clean course setup.
- Days 59–60 are sign-off checkpoints, so some deliverables are documentation
  and measured evidence rather than new SQL exercises.

## Exercise 1 — Identify clock dependence

Snapshot summaries depend only on table state. Trailing/current-period reports
also depend on the clock and need a bound `as_of_date` for reproducible review.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 1, read from the inline `VALUES` fixture. Build the answer toward `object_name`, and `clock_contract`; keep `object_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-60 Exercise 1, expected output: one row per `object_name`. The final columns are `object_name`, and `clock_contract`.
- **Independent verification:** For sql-60 Exercise 1, reselect the returned keys directly from the source; require unique `object_name` where the expected grain is one row per key and confirm the projected `object_name`, and `clock_contract` against the inline `VALUES` fixture. Add one source row with a new `object_name`; verify the result gains exactly one row carrying that `object_name` value.
- **Intermediate relation check:** For sql-60 Exercise 1, select `object_name` from the inline `VALUES` fixture before adding derived columns.
- **Clause check:** For sql-60 Exercise 1, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `object_name`, and finish with `object_name`, and `clock_contract`.
- **Alternative/trade-off:** For sql-60 Exercise 1, the chosen form is justified by this lesson-specific rationale: Snapshot summaries depend only on table state. Evaluate another form against the concrete expected result (one row per `object_name`) and the verification above.
- **Edge case:** Add one source row with a new `object_name`; verify the result gains exactly one row carrying that `object_name` value.

## Exercise 2 — Return executable sign-off checks

Each check contains observed/expected values, computed pass status, severity,
and remediation. A typed label cannot substitute for the equality expression.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 2, read from `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-60 Exercise 2, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`. The final order is `severity, check_name`.
- **Independent verification:** For sql-60 Exercise 2, project `order_id` plus the raw source columns from `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-60 Exercise 2, run `checks` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-60 Exercise 2, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders`, preserve one row per `order_id`, and finish with `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` ordered by `severity, check_name`.
- **Alternative/trade-off:** For sql-60 Exercise 2, the chosen form is justified by this lesson-specific rationale: Each check contains observed/expected values, computed pass status, severity, and remediation. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 3 — Calculate LAG once

`monthly` establishes grain; `with_previous` computes LAG one time; the outer
query calculates growth. The first month remains NULL because it has no valid
comparison.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 3, read from `orders`, and `v_monthly_revenue_refactored_solution`. Build the answer toward `month`, `revenue`, `previous_month`, and `month_over_month_growth`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-60 Exercise 3, expected output: one row per `month`. The final columns are `month`, `revenue`, `previous_month`, and `month_over_month_growth`. The final order is `month`.
- **Independent verification:** For sql-60 Exercise 3, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month`, `revenue`, `previous_month`, and `month_over_month_growth` against `orders`, and `v_monthly_revenue_refactored_solution`. Repeat with `NULL` in `LAG` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-60 Exercise 3, run `monthly`, and `with_previous` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
- **Clause check:** For sql-60 Exercise 3, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `orders`, and `v_monthly_revenue_refactored_solution`, preserve one row per `month`, and finish with `month`, `revenue`, `previous_month`, and `month_over_month_growth` ordered by `month`.
- **Alternative/trade-off:** For sql-60 Exercise 3, the chosen form is justified by this lesson-specific rationale: `monthly` establishes grain; `with_previous` computes LAG one time; the outer query calculates growth. Evaluate another form against the concrete expected result (one row per `month`) and the verification above.
- **Edge case:** Repeat with `NULL` in `LAG` and state whether the row is kept, rejected, or classified.

## Exercise 4 — Flag an incomplete month

The current calendar month is marked explicitly. Production evaluation should
bind an as-of date and avoid comparing a partial period with a complete one.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 4, read from `v_monthly_revenue_refactored_solution`. Build the answer toward `month`, `revenue`, and `is_incomplete_month`; keep `month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-60 Exercise 4, expected output: one row per `month`. The final columns are `month`, `revenue`, and `is_incomplete_month`. The final order is `month DESC`.
- **Independent verification:** For sql-60 Exercise 4, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month`, `revenue`, and `is_incomplete_month` against `v_monthly_revenue_refactored_solution`. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
- **Intermediate relation check:** For sql-60 Exercise 4, check `month DESC` before applying the row cap.
- **Clause check:** For sql-60 Exercise 4, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `v_monthly_revenue_refactored_solution`, preserve one row per `month`, and finish with `month`, `revenue`, and `is_incomplete_month` ordered by `month DESC`.
- **Alternative/trade-off:** For sql-60 Exercise 4, the chosen form is justified by this lesson-specific rationale: The current calendar month is marked explicitly. Evaluate another form against the concrete expected result (one row per `month`) and the verification above.
- **Edge case:** Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.

## Exercise 5 — Retain structured plan evidence

`EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` captures plan shape, estimates, actual
rows, buffer activity, and timing. Evidence applies only to the tested server,
data volume, parameters, and cache state.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 5, run the underlying read-only query over `v_monthly_revenue_refactored_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-60 Exercise 5, expected output: at most 12 rows keyed by `plan_node`. The final columns are `plan_node`, `estimated_rows`, `actual_rows`, `loops`, and `buffers`. The final order is `month DESC`.
- **Independent verification:** For sql-60 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-60 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows.
- **Clause check:** For sql-60 Exercise 5, the solution actually uses `FROM`, `SELECT`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `v_monthly_revenue_refactored_solution`, preserve one row per `plan_node`, and finish with `plan_node`, `estimated_rows`, `actual_rows`, `loops`, and `buffers` ordered by `month DESC`.
- **Alternative/trade-off:** For sql-60 Exercise 5, the chosen form is justified by this lesson-specific rationale: `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` captures plan shape, estimates, actual rows, buffer activity, and timing. Evaluate another form against the concrete expected result (at most 12 rows keyed by `plan_node`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 6 — Complete the operational release checklist

Rollback, ownership, privileges, refresh, monitoring, contracts, and limits all
have named owners/evidence. Query correctness alone is not production readiness.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 6, read from the inline `VALUES` fixture. Build the answer toward `item`, `evidence`, and `owner`; keep `evidence` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-60 Exercise 6, expected output: one row per `evidence`. The final columns are `item`, `evidence`, and `owner`.
- **Independent verification:** For sql-60 Exercise 6, reselect the returned keys directly from the source; require unique `evidence` where the expected grain is one row per key and confirm the projected `item`, `evidence`, and `owner` against the inline `VALUES` fixture. Add one source row with a new `evidence`; verify the result gains exactly one row carrying that `evidence` value.
- **Intermediate relation check:** For sql-60 Exercise 6, select `evidence` from the inline `VALUES` fixture before adding derived columns.
- **Clause check:** For sql-60 Exercise 6, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `evidence`, and finish with `item`, `evidence`, and `owner`.
- **Alternative/trade-off:** For sql-60 Exercise 6, the chosen form is justified by this lesson-specific rationale: Rollback, ownership, privileges, refresh, monitoring, contracts, and limits all have named owners/evidence. Evaluate another form against the concrete expected result (one row per `evidence`) and the verification above.
- **Edge case:** Add one source row with a new `evidence`; verify the result gains exactly one row carrying that `evidence` value.

## Exercise 7 — Publish lineage

Every published metric maps to sources, transformation grain, and a validation
query. This gives Codex and human maintainers a compact impact-analysis trail.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 7, read from the inline `VALUES` fixture. Build the answer toward `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`; keep `metric_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-60 Exercise 7, expected output: one row per `metric_name`. The final columns are `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`.
- **Independent verification:** For sql-60 Exercise 7, reselect the returned keys directly from the source; require unique `metric_name` where the expected grain is one row per key and confirm the projected `metric_name`, `source_tables`, `transformation_grain`, and `validation_query` against the inline `VALUES` fixture. Add one source row with a new `metric_name`; verify the result gains exactly one row carrying that `metric_name` value.
- **Intermediate relation check:** For sql-60 Exercise 7, select `metric_name` from the inline `VALUES` fixture before adding derived columns.
- **Clause check:** For sql-60 Exercise 7, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `metric_name`, and finish with `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`.
- **Alternative/trade-off:** For sql-60 Exercise 7, the chosen form is justified by this lesson-specific rationale: Every published metric maps to sources, transformation grain, and a validation query. Evaluate another form against the concrete expected result (one row per `metric_name`) and the verification above.
- **Edge case:** Add one source row with a new `metric_name`; verify the result gains exactly one row carrying that `metric_name` value.

## Exercise 8 — Reconcile dashboard totals

Monthly-view revenue is summed and compared with the simplest order total.
Nonzero difference blocks sign-off before any optimization is accepted.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 8, read from `v_monthly_revenue_refactored_solution`, and `orders`. Compute `dashboard_total`, `source_total`, and `difference` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-60 Exercise 8, expected output: exactly one aggregate summary row. The final columns are `dashboard_total`, `source_total`, and `difference`.
- **Independent verification:** For sql-60 Exercise 8, evaluate each of `dashboard_total`, and `source_total` in a separate control `SELECT` over `v_monthly_revenue_refactored_solution`, and `orders`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-60 Exercise 8, select `order_id` from `v_monthly_revenue_refactored_solution`, and `orders` before adding derived columns.
- **Clause check:** For sql-60 Exercise 8, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `v_monthly_revenue_refactored_solution`, and `orders`, preserve exactly one summary row, and finish with `dashboard_total`, `source_total`, and `difference`.
- **Alternative/trade-off:** For sql-60 Exercise 8, the chosen form is justified by this lesson-specific rationale: Monthly-view revenue is summed and compared with the simplest order total. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Exercise 9 — Test edge fixtures

The in-query fixture represents NULL, one-row-like, and duplicate-key cases
without changing course data. Counts expose assumptions that production
constraints or quarantine rules must enforce.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 9, read from `edge_fixture`. Build the answer toward `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows`; keep `fixture_rows` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-60 Exercise 9, expected output: one row per `fixture_rows`. The final columns are `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows`.
- **Independent verification:** For sql-60 Exercise 9, reselect the returned keys directly from the source; require unique `fixture_rows` where the expected grain is one row per key and confirm the projected `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows` against `edge_fixture`. Repeat with `NULL` in `fixture_rows`, and `null_email_rows` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-60 Exercise 9, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-60 Exercise 9, the solution actually uses `WITH`, `FROM`, `WHERE`, aggregate `FILTER`, and `SELECT`. Read only those operations: begin at `edge_fixture`, preserve one row per `fixture_rows`, and finish with `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows`.
- **Alternative/trade-off:** For sql-60 Exercise 9, the chosen form is justified by this lesson-specific rationale: The in-query fixture represents NULL, one-row-like, and duplicate-key cases without changing course data. Evaluate another form against the concrete expected result (one row per `fixture_rows`) and the verification above.
- **Edge case:** Repeat with `NULL` in `fixture_rows`, and `null_email_rows` and state whether the row is kept, rejected, or classified.

## Exercise 10 — Distinguish FAIL from NOT_RUN

Executed checks compare observed and expected values. An unexecuted Windows CI
bootstrap remains `NOT_RUN`; prose or confidence must never upgrade it to PASS.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 10, read from `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders`. Build the answer toward `criterion`, and `result`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-60 Exercise 10, expected output: one row per `order_id`. The final columns are `criterion`, and `result`. The final order is `criterion`.
- **Independent verification:** For sql-60 Exercise 10, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `criterion`, and `result` against `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
- **Intermediate relation check:** For sql-60 Exercise 10, check `criterion` before applying the row cap.
- **Clause check:** For sql-60 Exercise 10, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `v_dq_customers_solution`, `v_customer_ltv_solution`, and `orders`, preserve one row per `order_id`, and finish with `criterion`, and `result` ordered by `criterion`.
- **Alternative/trade-off:** For sql-60 Exercise 10, the chosen form is justified by this lesson-specific rationale: Executed checks compare observed and expected values. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
