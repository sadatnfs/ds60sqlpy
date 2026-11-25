# Day 60 Solution: End-to-End Capstone Sign-off


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day60_solutions.sql
```

The solution creates three views inside one transaction and prints the
one-row quality summary (500, 0, 0, 0), the reconciliation row with
2,355,646.89 on both sides, five `CREATE INDEX` tags, an
`EXPLAIN (ANALYZE, BUFFERS)` plan for the latest 12 months that touched 65
shared buffers in under a millisecond on our run, and the five-row
checklist. The ten exercise results follow, including a fourth view, the
46-month series twice and one JSON plan, before `ROLLBACK` removes every
object. Use the
[solution-reading steps](../../STUDY-GUIDE.md#read-a-solution) to compare
that transcript with yours.

## Clause-by-clause reading map

Every statement below follows
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order),
and the file keeps returning to three decisions:

- **Where revenue comes from.** Every money figure sums
  `orders.total_amount`, never order lines, so LTV, the monthly view and both
  reconciliations share one definition. Exercise 8 then compares two routes
  to that same figure.
- **When NULL is the answer.** The first month keeps a NULL
  `previous_month` instead of 0, `NULLIF(previous_month, 0)` keeps the
  division safe, and Exercise 10 tests `executed` before comparing values so
  an unrun check prints `NOT_RUN`.
- **What follows the clock.** Only Exercise 4 calls `CURRENT_DATE`; every
  other statement reads table state, which is the split Exercise 1 records.

Exercises 1, 6 and 7 are typed `VALUES` lists whose correctness is a review
question, while Exercises 2, 8 and 10 run the queries that back them with
data.

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

## Deliverable 1: Reusable DQ views

The learner creates `v_dq_customers` and `v_dq_orders`. The reference solution
uses a suffixed customer view so it cannot collide with a learner's view:

```sql
BEGIN;
SET search_path TO training, public;

CREATE VIEW v_dq_customers_solution AS
SELECT
  COUNT(*) AS total_rows,
  COUNT(*) FILTER (WHERE email IS NULL
    OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$') AS invalid_email,
  COUNT(*) FILTER (WHERE country !~ '^[A-Z]{2}$') AS invalid_country,
  COUNT(*) FILTER (WHERE trim(full_name) = '') AS invalid_name
FROM
  customers;

SELECT
  *
FROM
  v_dq_customers_solution;

SELECT
  COUNT(*) AS total_rows,
  COUNT(*) FILTER (WHERE total_amount < 0) AS negative_amounts,
  COUNT(*) FILTER (WHERE customer_id IS NULL) AS missing_customer
FROM
  orders;

ROLLBACK;
```

Expected shape: one customer summary row and one order summary row. The course
seed should report zero failures.

## Deliverable 2: Core business views and reconciliation

```sql
BEGIN;
SET search_path TO training, public;

CREATE VIEW v_customer_ltv_solution AS
SELECT
  c.customer_id,
  c.country,
  COALESCE(SUM(o.total_amount), 0)::numeric(14, 2) AS ltv
FROM
  customers c
  LEFT JOIN orders o USING (customer_id)
GROUP BY
  c.customer_id,
  c.country;

CREATE VIEW v_monthly_revenue_solution AS
WITH monthly AS (
  SELECT
    date_trunc('month', order_date)::date AS month,
    SUM(total_amount) AS revenue
  FROM
    orders
  GROUP BY
    date_trunc('month', order_date))
SELECT
  month,
  revenue,
  LAG(revenue) OVER (ORDER BY month) AS previous_month,
  ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) / NULLIF (LAG(revenue) OVER (ORDER BY month), 0), 4) AS month_over_month_growth
FROM
  monthly;

SELECT
  (
    SELECT
      ROUND(SUM(ltv), 2)
    FROM
      v_customer_ltv_solution) AS customer_ltv_total,
  (
    SELECT
      ROUND(SUM(total_amount), 2)
    FROM
      orders) AS order_total,
  (
    SELECT
      ROUND(SUM(ltv), 2)
    FROM
      v_customer_ltv_solution) - (
    SELECT
      ROUND(SUM(total_amount), 2)
    FROM
      orders) AS difference;

ROLLBACK;
```

Expected reconciliation: `difference = 0.00`. The monthly view has one row per
represented order month; it does not manufacture missing months.

## Deliverable 3: Stakeholder-ready outputs

The learner file contains three runnable outputs:

- Finance: YTD actual, budget, and variance at `(month, category)` grain.
- Marketing: active customers by signup cohort and lifecycle month 0-6. A full
  retention rate additionally needs the cohort-size denominator from Day 47.
- Operations: an `EXPLAIN` of recent units by product category.

For each output, record the consumer, business definition, result grain,
freshness expectation, and at least one reconciliation or sanity check.

## Deliverable 4: Performance sign-off

```sql
BEGIN;
SET search_path TO training, public;

CREATE INDEX idx_orders_date_day60_solution ON orders (order_date);

CREATE INDEX idx_orders_customer_day60_solution ON orders (customer_id);

CREATE INDEX idx_order_items_order_day60_solution ON order_items (order_id);

CREATE INDEX idx_expenses_date_day60_solution ON expenses (expense_date);

CREATE INDEX idx_budgets_period_day60_solution ON budgets (period);

CREATE VIEW v_monthly_revenue_solution AS
WITH monthly AS (
  SELECT
    date_trunc('month', order_date)::date AS month,
    SUM(total_amount) AS revenue
  FROM
    orders
  GROUP BY
    date_trunc('month', order_date))
SELECT
  month,
  revenue,
  LAG(revenue) OVER (ORDER BY month) AS previous_month,
  ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) / NULLIF (LAG(revenue) OVER (ORDER BY month), 0), 4) AS month_over_month_growth
FROM
  monthly;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  *
FROM
  v_monthly_revenue_solution
ORDER BY
  month DESC
LIMIT 12;

ROLLBACK;
```

Capture actual execution time and buffers before and after candidate indexes.
The transaction rolls back both views and indexes.

## Deliverable 5: Written sign-off

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
- Days 59-60 are sign-off checkpoints, so some deliverables are documentation
  and measured evidence rather than new SQL exercises.

## Exercise 1: Identify clock dependence

Snapshot summaries depend only on table state. Trailing/current-period reports
also depend on the clock and need a bound `as_of_date` for reproducible review.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 1, read the definitions of `v_dq_customers_solution` and `v_customer_ltv_solution` and of the trailing or current-period queries (the learner Finance CTEs and Operations filter call `now()`, and Exercise 4 calls `CURRENT_DATE`), then record each object's clock dependence in an inline `VALUES` fixture with `object_name` and `clock_contract`.
- **Expected result/shape:** For sql-60 Exercise 1, expected output: 3 rows: `v_dq_customers_solution` and `v_customer_ltv_solution` marked `snapshot-independent`, and `trailing/current-period reports` marked `clock-dependent: bind as_of_date`. The final columns are `object_name` and `clock_contract`.
- **Independent verification:** For sql-60 Exercise 1, inside the solution transaction run `SELECT viewname FROM pg_views WHERE schemaname = 'training' AND definition ~* '(now\(\)|current_date|current_timestamp)'`: it returns 0 rows, which backs both `snapshot-independent` labels. Then create a rolled-back probe view `v_clock_probe AS SELECT CURRENT_DATE AS as_of` and rerun the search: it returns exactly `v_clock_probe`, so the search does detect a clock call.
- **Intermediate relation check:** The `VALUES` list is the entire input: three typed rows. To test the classification rather than trust it, search `pg_views.definition` for `now()` and `CURRENT_DATE` inside the solution's transaction; neither solution view matched on our run.
- **Clause check:** `FROM (VALUES ...) AS reproducibility (object_name, clock_contract)` names the two columns and `SELECT *` prints the rows in typed order. There is no `ORDER BY`, so add one before diffing two transcripts.
- **Alternative/trade-off:** A comment beside each view says the same thing but cannot be filtered or counted. The third row names a category rather than an object; a stricter list would name Exercise 4's query and give it an `as_of_date` parameter.
- **Edge case:** A new view added to the capstone needs its own row, and if `now()` or `CURRENT_DATE` appears anywhere in it, including a CTE, its `clock_contract` must say clock-dependent.

## Exercise 2: Return executable sign-off checks

Each check contains observed/expected values, computed pass status, severity,
and remediation. A typed label cannot substitute for the equality expression.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 2, read `invalid_email` from the one-row `v_dq_customers_solution` and compare `SUM(ltv)` from `v_customer_ltv_solution` with `SUM(total_amount)` from `orders`; write each check as one `UNION ALL` branch of `checks` with `check_name`, `observed_value`, `expected_value`, `severity`, and `remediation`, then compute `pass` as `observed_value = expected_value`.
- **Expected result/shape:** For sql-60 Exercise 2, expected output: 2 rows, one per `check_name`: `invalid_customer_emails` (observed 0) and `ltv_reconciles_to_orders` (observed 0.00, the absolute gap between LTV and order totals), both `critical` with `expected_value` 0 and `pass` true. The final columns are `check_name`, `observed_value`, `expected_value`, `severity`, `remediation`, and `pass`. The final order is `severity, check_name`.
- **Independent verification:** For sql-60 Exercise 2, confirm that `SELECT invalid_email FROM v_dq_customers_solution` returns 0 and that `SUM(ltv)` and `SUM(total_amount)` both return 2,355,646.89, matching the two observed values. In a rolled-back transaction set customer 1's email to `'not-an-email'` (or to NULL): `invalid_customer_emails` then reports observed 1 and `pass` false, so the gate fails on a real defect.
- **Intermediate relation check:** Run each branch of the `UNION ALL` inside `checks` alone. Each returns one row, because `v_dq_customers_solution` is a one-row summary and the second branch is built from two scalar subqueries, so `checks` holds exactly two rows and no `order_id` appears at any stage.
- **Clause check:** `checks` stacks two one-row branches with `UNION ALL`; the outer `SELECT *` adds `observed_value = expected_value AS pass`, and `ORDER BY severity, check_name` sorts both as text. The first branch casts `invalid_email` to `numeric` so both branches share a column type.
- **Alternative/trade-off:** Separate one-row queries would print the same numbers but leave the reader to compare them by eye. One table with a computed `pass` lets a release gate select failing rows directly, and a `CASE` rank on `severity` would make the order follow risk rather than spelling.
- **Edge case:** If a check's subquery returns NULL, `pass` prints blank rather than `false`, so a gate written as `WHERE NOT pass` lets it through. Filter with `WHERE pass IS NOT TRUE` instead.

## Exercise 3: Calculate LAG once

`monthly` establishes grain; `with_previous` computes LAG one time; the outer
query calculates growth. The first month remains NULL because it has no valid
comparison.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 3, read `orders` through two CTEs: `monthly` sums `total_amount` by `date_trunc('month', order_date)::date`, and `with_previous` adds `LAG(revenue) OVER (ORDER BY month)` once as `previous_month`; the outer `SELECT` of `v_monthly_revenue_refactored_solution` derives `month_over_month_growth` from that column.
- **Expected result/shape:** For sql-60 Exercise 3, expected output: 46 rows, one per `month` from 2023-02-01 to 2026-11-01, with `previous_month` and `month_over_month_growth` NULL only on the first row and 13 negative growth values. The final columns are `month`, `revenue`, `previous_month`, and `month_over_month_growth`. The final order is `month`.
- **Independent verification:** For sql-60 Exercise 3, compare the refactored view with `v_monthly_revenue_solution` and with the learner `v_monthly_revenue` using `EXCEPT` in both directions: 0 rows each way, and `SUM(revenue)` is 2,355,646.89. In a rolled-back transaction set every February 2023 order's `total_amount` to 0: 2023-02-01 shows `revenue` 0.00, and 2023-03-01 shows `previous_month` 0.00 with NULL growth from `NULLIF` instead of a division error. Deleting the 37 May 2024 orders instead leaves 45 rows and gives 2024-06-01 April's 20,055.03 as `previous_month`, because `LAG` reads the previous row, not the previous calendar month.
- **Intermediate relation check:** Run `monthly` alone: 46 rows, one per calendar month, summing to 2,355,646.89. Then run `with_previous` and confirm the same 46 rows with `previous_month` NULL only on 2023-02-01.
- **Clause check:** `monthly` groups `orders` by `date_trunc('month', order_date)` and casts the result to `date`; `with_previous` evaluates `LAG(revenue) OVER (ORDER BY month)` once and names it; the outer `SELECT` reuses that name inside `ROUND((revenue - previous_month) / NULLIF(previous_month, 0), 4)`. The view has no `ORDER BY`, so the query that reads it adds `ORDER BY month`.
- **Alternative/trade-off:** `v_monthly_revenue_solution` repeats the same `LAG` three times, and the learner's `v_monthly_revenue` also wraps one in a `COALESCE(..., 0)` that can never matter, because a NULL lag already makes the denominator NULL. Naming the lag once leaves a single window to edit.
- **Edge case:** `LAG` reads the previous row, not the previous calendar month, so a month with no orders would be skipped silently; the series is safe here only because all 46 months are present. The first month's growth stays NULL rather than 0 or an error.

## Exercise 4: Flag an incomplete month

The current calendar month is marked explicitly. Production evaluation should
bind an as-of date and avoid comparing a partial period with a complete one.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 4, read the 46 rows of `v_monthly_revenue_refactored_solution` and add `is_incomplete_month` as `month = date_trunc('month', CURRENT_DATE)::date`.
- **Expected result/shape:** For sql-60 Exercise 4, expected output: 46 rows, one per `month`, newest first, with `is_incomplete_month` true only on the current calendar month (2026-11-01 at 85,364.67 when `CURRENT_DATE` was 2026-11-25) and false on the 45 complete months. The final columns are `month`, `revenue`, and `is_incomplete_month`. The final order is `month DESC`.
- **Independent verification:** For sql-60 Exercise 4, confirm that `COUNT(*) FILTER (WHERE is_incomplete_month)` is 1 of 46 rows and that the flagged month holds `MAX(order_date)`: on the checked load November 2026 had 151 orders over 23 order days against October's 313 over 31. Replace `CURRENT_DATE` with `DATE '2026-10-15'` and the flag moves to 2026-10-01 (170,179.13), which shows the result depends on the clock and needs a bound as-of date.
- **Intermediate relation check:** Before adding the flag, list the newest two rows: 2026-11-01 at 85,364.67 and 2026-10-01 at 170,179.13 on our run. Counting distinct order dates per month shows why November looks small.
- **Clause check:** The query reads the refactored view, computes `month = date_trunc('month', CURRENT_DATE)::date` as a boolean column and sorts `month DESC`. With no `WHERE`, all 46 months remain and at most one is true.
- **Alternative/trade-off:** Dropping the open month with `WHERE` would hide November's 151 orders from operational readers; a flag keeps the row while a chart can still exclude it. Passing an `as_of_date` instead of `CURRENT_DATE` would make the flag testable.
- **Edge case:** December has no row at all until its first order arrives, so on 1 December the flag cannot mark the new month, and November turns `false` the same day.

## Exercise 5: Retain structured plan evidence

`EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` captures plan shape, estimates, actual
rows, buffer activity, and timing. Evidence applies only to the tested server,
data volume, parameters, and cache state.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 5, run `SELECT * FROM v_monthly_revenue_refactored_solution ORDER BY month DESC LIMIT 12` alone first (12 rows, 2026-11-01 back to 2025-12-01), then wrap the same statement in `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` with seed rows, settings, and statistics unchanged.
- **Expected result/shape:** For sql-60 Exercise 5, expected output: one row in a single `QUERY PLAN` column holding a JSON array with one plan of 8 nodes: `Limit` (12 actual rows), `Sort` (top-N heapsort), `Subquery Scan` on `with_previous`, `WindowAgg`, `Sort`, `Subquery Scan` on `monthly`, a hashed `Aggregate`, and a `Seq Scan` on `orders` (4,362 rows). The final column is `QUERY PLAN`.
- **Independent verification:** For sql-60 Exercise 5, read each node's `Plan Rows` beside `Actual Rows` times `Actual Loops`: the hashed `Aggregate` plans 4,362 groups and returns 46, and the `Seq Scan` touches all 65 pages of `orders` (`Shared Hit Blocks` plus `Shared Read Blocks`). In a rolled-back transaction run `CREATE STATISTICS orders_month_stats ON (date_trunc('month', order_date)) FROM orders` and `ANALYZE orders`, then explain again: the same 8 nodes return the same 12 rows, but the `Aggregate` estimate drops to 46.
- **Intermediate relation check:** Run the `SELECT * ... ORDER BY month DESC LIMIT 12` without `EXPLAIN` first: 12 rows from 2026-11-01 back to 2025-12-01 on our run. Then read the JSON one node at a time, from the `Seq Scan` upward.
- **Clause check:** `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` executes the query and returns one row holding one JSON document; inside it the query reads the view, sorts by `month DESC` and keeps 12 rows. A per-node table needs a second step that walks the nested `Plans` arrays.
- **Alternative/trade-off:** Text format reads better; JSON stores and compares better, because fields such as `Plan Rows`, `Actual Rows` and `Shared Hit Blocks` sit at fixed keys. On our run a `DO` block that captured the JSON with `EXECUTE ... INTO` and a recursive CTE over `->'Plans'` produced one row per node, 8 in all.
- **Edge case:** The estimate gap is the finding: the hashed aggregate expects 4,362 groups and returns 46. Expression statistics on the `date_trunc` key fixed that on PostgreSQL 17.12, so record any `CREATE STATISTICS` or `ANALYZE` beside the before and after plans.

## Exercise 6: Complete the operational release checklist

Rollback, ownership, privileges, refresh, monitoring, contracts, and limits all
have named owners/evidence. Query correctness alone is not production readiness.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 6, list the release checklist as an inline `VALUES` relation with one row per `item`, its current `evidence`, and its `owner`.
- **Expected result/shape:** For sql-60 Exercise 6, expected output: 6 rows, one per checklist `item`: rollback plan, object ownership/privileges, refresh cadence, monitoring and alerts, data contracts, and known limits. The final columns are `item`, `evidence`, and `owner`.
- **Independent verification:** For sql-60 Exercise 6, confirm 6 rows with no NULL `evidence` or `owner` and no repeated `item`; every row whose `evidence` reads `review required` still needs a named reviewer before release.
- **Intermediate relation check:** For sql-60 Exercise 6, write the `VALUES` list with column aliases first and check that each `item` appears once.
- **Clause check:** `FROM (VALUES ...) AS release_check (item, evidence, owner)` with `SELECT *` prints six typed rows in typed order, each one item, its evidence and its owner.
- **Alternative/trade-off:** A wiki checklist holds the same text, but a relation can be filtered: `WHERE evidence = 'review required'` returns the two rows still owed a reviewer, and the list can sit beside Exercise 10's status rows.
- **Edge case:** A `VALUES` checklist records claims, not proof; link each `evidence` entry to an executed check or to the review that produced it.

## Exercise 7: Publish lineage

Every published metric maps to sources, transformation grain, and a validation
query. This gives the AI tutor and human maintainers a compact impact-analysis trail.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 7, write an inline `VALUES` lineage fixture with one row per published metric (`customer_ltv`, `monthly_revenue`, and `customer_dq`) giving its `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`.
- **Expected result/shape:** For sql-60 Exercise 7, expected output: 3 rows: `customer_ltv` from customers + orders at customer grain, `monthly_revenue` from orders at calendar-month grain, and `customer_dq` from customers as one snapshot summary. The final columns are `metric_name`, `source_tables`, `transformation_grain`, and `validation_query`.
- **Independent verification:** For sql-60 Exercise 7, turn each `validation_query` into a runnable check: `SUM(ltv)` over the 500 rows of `v_customer_ltv_solution`, `SUM(revenue)` over the 46 rows of the refactored monthly view, and `SUM(total_amount)` over `orders` all return 2,355,646.89, and `v_dq_customers_solution` reports 0 invalid emails, countries, and names over 500 customers. A row whose text cannot be rewritten as a `SELECT` with a pass condition is not yet lineage evidence.
- **Intermediate relation check:** The input is three typed rows. Rewrite each `validation_query` as runnable SQL in a scratch file to prove it is checkable; for `customer_ltv` that is the reconciliation printed near the top of the solution.
- **Clause check:** `FROM (VALUES ...) AS lineage (metric_name, source_tables, transformation_grain, validation_query)` names four text columns, and `SELECT *` prints them as typed.
- **Alternative/trade-off:** Storing real SQL in `validation_query` and running it from a script would turn the table into a test suite; text predicates document intent but cannot fail. `source_tables` packs two names into one string, so querying lineage by table would need one row per source.
- **Edge case:** A fourth metric such as retention needs its own row naming `customers` and `orders`, a (cohort, offset) grain and a check that each cohort's size equals its signup count.

## Exercise 8: Reconcile dashboard totals

Monthly-view revenue is summed and compared with the simplest order total.
Nonzero difference blocks sign-off before any optimization is accepted.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 8, sum `revenue` over the 46 rows of `v_monthly_revenue_refactored_solution` as `dashboard_total` and `total_amount` over the 4,362 `orders` as `source_total`, each rounded to 2 places in its own scalar subquery, and subtract them as `difference`.
- **Expected result/shape:** For sql-60 Exercise 8, expected output: one row with `dashboard_total` 2,355,646.89, `source_total` 2,355,646.89, and `difference` 0.00 on the checked load. The final columns are `dashboard_total`, `source_total`, and `difference`.
- **Independent verification:** For sql-60 Exercise 8, run the two scalar subqueries alone: both return 2,355,646.89. In a rolled-back transaction insert a 100.00 order for customer 1 dated `now()`: both totals become 2,355,746.89 and `difference` stays 0.00, so this control checks the view logic rather than the load. Make the dashboard side skip the open month with `FILTER (WHERE month < date_trunc('month', CURRENT_DATE)::date)` instead, and `difference` becomes -85,364.67, the November revenue that version would hide.
- **Intermediate relation check:** Run the two scalar subqueries alone: `SUM(revenue)` over the 46 view rows and `SUM(total_amount)` over the 4,362 orders, each rounded to 2 places. Both printed 2,355,646.89 on our run.
- **Clause check:** Three scalar subqueries in a `SELECT` with no `FROM` produce exactly one row; the third repeats the first two and subtracts. Rounding happens before subtraction, so `difference` compares the two printed values.
- **Alternative/trade-off:** A `CROSS JOIN` of two one-row CTEs would compute each sum once instead of twice. Comparing month by month, with a `FULL JOIN` between the view and a direct monthly `GROUP BY`, would also catch errors that cancel in the grand total.
- **Edge case:** An inserted order moves both totals equally and `difference` stays 0.00, so this check proves the view logic, not the load. A line-item or payment total is a different contract and needs a named tolerance.

## Exercise 9: Test edge fixtures

The in-query fixture represents NULL, one-row-like, and duplicate-key cases
without changing course data. Counts expose assumptions that production
constraints or quarantine rules must enforce.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 9, build a three-row `VALUES` fixture `edge_fixture(id, email, amount)` with one row whose email and amount are NULL and two rows that share `id` 2 with emails that differ only in case, then count rows, NULL emails, duplicate keys, and non-null amounts.
- **Expected result/shape:** For sql-60 Exercise 9, expected output: one row with `fixture_rows` 3, `null_email_rows` 1, `duplicate_key_rows` 1, and `nonnull_amount_rows` 2. The final columns are `fixture_rows`, `null_email_rows`, `duplicate_key_rows`, and `nonnull_amount_rows`.
- **Independent verification:** For sql-60 Exercise 9, confirm that `duplicate_key_rows` equals `COUNT(*) - COUNT(DISTINCT id)` (3 - 2 = 1) and `nonnull_amount_rows` equals `COUNT(amount)` (2); `COUNT(DISTINCT lower(email))` is 1, so the two `id` 2 rows also collide after email normalization.
- **Intermediate relation check:** For sql-60 Exercise 9, count each property in its own `SELECT` over the fixture first; `COUNT(column)` skips NULL, while `COUNT(*)` does not.
- **Clause check:** `WITH edge_fixture (id, email, amount) AS (VALUES ...)` names the columns, and one aggregate `SELECT` returns `COUNT(*)`, `COUNT(*) FILTER (WHERE email IS NULL)`, `COUNT(*) - COUNT(DISTINCT id)` and `COUNT(amount)`. The only `WHERE` sits inside `FILTER`, so no row is removed before counting.
- **Alternative/trade-off:** A temporary table would hold the same rows but needs cleanup, while the CTE leaves course data untouched. Adding `COUNT(DISTINCT email)` (2) beside `COUNT(DISTINCT lower(email))` (1) would expose the case-only duplicate as well as the key duplicate.
- **Edge case:** A report that only counts non-null amounts would silently drop the NULL row; keep `fixture_rows` beside every filtered count so missing values stay visible.

## Exercise 10: Distinguish FAIL from NOT_RUN

Executed checks compare observed and expected values. An unexecuted Windows CI
bootstrap remains `NOT_RUN`; prose or confidence must never upgrade it to PASS.

### Reasoning and verification

- **Inputs/evidence:** For sql-60 Exercise 10, list the acceptance criteria as a `VALUES` relation with `criterion`, an `executed` flag, the `observed` value from the solution views, and the `expected` value, then label each criterion `PASS`, `FAIL`, or `NOT_RUN`.
- **Expected result/shape:** For sql-60 Exercise 10, expected output: 3 rows ordered by `criterion`: `customer DQ` PASS, `LTV reconciliation` PASS, and `Windows CI bootstrap` NOT_RUN. The final columns are `criterion` and `result`. The final order is `criterion`.
- **Independent verification:** For sql-60 Exercise 10, confirm that each PASS row's observed value matches its expected value when queried directly (`SELECT invalid_email FROM v_dq_customers_solution` returns 0) and that the unexecuted criterion reports `NOT_RUN`, never `PASS`.
- **Intermediate relation check:** For sql-60 Exercise 10, write the `CASE` so that `executed` is tested before the comparison; an unexecuted check must never fall through to `PASS`.
- **Clause check:** `FROM (VALUES ...) AS acceptance (criterion, executed, observed, expected)` evaluates two scalar subqueries inside the list. The `CASE` tests `executed AND observed = expected`, then `executed`, then falls to `NOT_RUN`, and `ORDER BY criterion` sorts the text under the database collation.
- **Alternative/trade-off:** The two observed values repeat Exercise 2's subqueries; reading both from one shared `checks` CTE would stop the sign-off table and this status list from drifting apart. A sequence column in the `ORDER BY` would also remove the dependence on collation.
- **Edge case:** If `observed` is NULL, `observed = expected` is unknown and the `CASE` returns `FAIL`, which is the safe result for a check that produced no evidence.
