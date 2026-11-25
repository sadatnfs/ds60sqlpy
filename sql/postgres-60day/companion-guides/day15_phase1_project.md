# Day 15: Phase 1 Project: Multi-Dimensional Revenue Report (Companion Guide)

## How to run this lesson

In `./classroom`, choose PostgreSQL, open **sql-15** and run it with **Whole SQL lesson (psql)**. The file runs inside `BEGIN`/`ROLLBACK` against `advanced_sql_training` and holds one starter report: monthly net revenue by customer segment and country, built from two CTEs (`line` and `segment`) and capped at 200 rows. Nothing in it writes, so the transcript is one result block between the `BEGIN`, `SET` and `ROLLBACK` tags. The six project prompts follow as comments. Example 2 below, the `EXPLAIN` of that report, lives only in this guide; paste it into **SQL snippet** to see the plan.

Your saved copy is
`.learning/sql/sql-15/lesson/workspace/sql/postgres-60day/day15_phase1_project.sql`.
This is a project day, so the file grows: add each prompt's query under its comment, rerun the whole script and confirm the earlier results still print before reading the new one. If the sixth query fails, `ON_ERROR_STOP` ends the run there, the open transaction is discarded with the session, and the first five results are the only evidence you have.

Shared steps for [loading and resetting tables](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) and the [notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route) live in the study guide.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 14; numeric types and casting](day14_numeric_and_casting.md)
  and the complete Day 01-14 foundation sequence
- **Artifacts:** [learner SQL](../day15_phase1_project.sql) ·
  [solution reasoning](../solutions/day15_solutions.md) ·
  [executable solution](../solutions/day15_solutions.sql)

## A beginner's mental model for this lesson

A Phase 1 report mixes three fact tables that sit at different grains: `order_items` has one row per order line (13,085 rows), `orders` one row per order (4,362) and `payments` one row per payment (3,836, because 347 orders were paid in two parts). A **metric contract** names the grain each number is computed at before anything is joined. Net revenue is a line fact, `unit_price * quantity * (1 - discount)`; stored revenue is the order-level `total_amount`; paid revenue is a sum over payments.

The worked report keeps those grains apart with CTEs. `line` collapses order lines to one row per customer and UTC month, and only then joins `segment`, which has one row per customer. Because each side holds at most one row per customer and month at that point, the join cannot repeat revenue, and `COUNT(DISTINCT l.customer_id)` counts active customers rather than lines. Join `order_items` to `payments` first instead and every line of a two-payment order appears twice, doubling its revenue.

A **control total** proves that nothing was lost or duplicated along the way. On this fixture, net revenue summed straight from `order_items` is 2,355,647.12 and `total_amount` summed over `orders` is 2,355,646.89; the 0.23 gap is cent rounding inside each stored total, not a join bug. Every report you build today should land on one of those two numbers, depending on which revenue definition its contract names.

## Two worked SQL examples

### Example 1

```sql
WITH line AS (
  SELECT
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_utc,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
),
segment AS (
  SELECT
    c.customer_id,
    COALESCE(c.segment, 'standard') AS segment,
    c.country
  FROM
    customers c
)
SELECT
  s.segment,
  s.country,
  l.month_utc,
  ROUND(SUM(l.revenue), 2) AS revenue,
  COUNT(DISTINCT l.customer_id) AS actives,
  ROUND(SUM(l.revenue) / NULLIF (COUNT(DISTINCT l.customer_id), 0), 2) AS rev_per_active
FROM
  line l
  JOIN segment s ON s.customer_id = l.customer_id
GROUP BY
  s.segment,
  s.country,
  l.month_utc
ORDER BY
  l.month_utc DESC,
  revenue DESC,
  s.segment,
  s.country
LIMIT 200;
```

**How to read it:** Read the CTEs before the outer query. `line` joins each order to its items and groups by customer and UTC month, so a customer with three orders in one month becomes a single row holding their summed net revenue. `segment` is `customers` with `COALESCE(c.segment, 'standard')`; every fixture customer already belongs to gold, platinum, silver or standard (125 each), so the fallback guards future data without changing today's rows. The outer query joins the two on `customer_id`, groups by segment, country and month, and divides revenue by `NULLIF(COUNT(DISTINCT l.customer_id), 0)` so a group with no active customers could never divide by zero.

**Expected result/shape:** The full grouping has 303 segment, country and month combinations on the load used here, so `LIMIT 200` drops the oldest 103. The newest UTC month comes first, led by silver CA with 16,564.70 from 11 active customers (1,505.88 per active). BR never appears: its 62 customers have no orders, so the inner join from `line` has nothing to match. As a control, the 303 rounded group revenues add to 2,355,647.17, a few cents from the 2,355,647.12 you get by summing net revenue directly from `order_items`.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (
  COSTS OFF
) WITH line AS (
  SELECT
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_utc,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date),
  segment AS (
    SELECT
      c.customer_id,
      COALESCE(c.segment, 'standard') AS segment,
      c.country
    FROM
      customers c
)
  SELECT
    s.segment,
    s.country,
    l.month_utc,
    ROUND(SUM(l.revenue), 2) AS revenue,
  COUNT(DISTINCT l.customer_id) AS actives,
  ROUND(SUM(l.revenue) / NULLIF (COUNT(DISTINCT l.customer_id), 0), 2) AS rev_per_active
FROM
  line l
  JOIN segment s ON s.customer_id = l.customer_id
GROUP BY
  s.segment,
  s.country,
  l.month_utc
ORDER BY
  l.month_utc DESC,
  revenue DESC,
  s.segment,
  s.country
LIMIT 200;
```

**How to read it:** `EXPLAIN (COSTS OFF)` prints the plan PostgreSQL chose for the same report without returning any revenue. Neither CTE gets its own node, because PostgreSQL inlines both: `line` turns into a `HashAggregate` sitting on a hash join of `order_items` and `orders`, and `segment` is just a `Seq Scan on customers` feeding a second hash join.

**Expected result/shape:** Roughly 19 plan lines. Read upward from the scans: the per-customer-month `HashAggregate`, the join to `customers`, a `Sort` that feeds a `GroupAggregate` (sorted input is what `COUNT(DISTINCT ...)` needs), an `Incremental Sort` that reuses the month order for the final `ORDER BY`, and `Limit` on top. Node names can differ between PostgreSQL versions; the part that should not change is that line revenue is aggregated below the join to customers.

## Learning objectives

- Design a multi-dimensional revenue report from a written metric contract.
- Reconcile joins, conditional metrics, subtotals, and time calculations before
  presenting the result.

## Vocabulary and concepts

- **Metric contract:** a written definition of grain, formula, filters, and
  exclusions.
- **Dimensional report:** measures grouped by descriptive attributes such as
  country, category, and month.
- **Control total:** an independently calculated value used for reconciliation.

## Worked example / walkthrough

Build one stable `order_lines` relation first, with one row per intended line or
order and a single net-revenue formula. Reconcile its total, then add dimension
joins one at a time and compare the total after each join. Only after totals
remain stable should you add grouping sets and display labels.

## Practice assumptions and review method

- **Focus:** Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.
- **Assumptions:** All monetary summaries identify stored totals versus computed net line revenue. Reporting month uses UTC and empty populations remain visible where required.
- **Failure to watch for:** Combining fact tables before fixing their grain multiplies measures; every project output must state its row grain and acceptance checks.
- **Review loop:** after each new query, compare its grand total with the matching figure in your Exercise 6 summary row; a mismatch points at the join that changed the grain.

## Exercises

Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.

Work the prompts in order. Exercises 1 to 3 each summarize one or two tables, Exercise 4 is where `payments` enters and fanout becomes possible, and Exercise 6 prints the control totals that every earlier answer should reconcile to.

1. **Query writing:** Create a customer performance table with order count, stored revenue, and latest order date, retaining customers with no orders.
   **Progressive hint:** Left join from customers and aggregate at customer grain.
   **Predict:** how many customers will show an `order_count` of 0, and which country do they share?
   **Inputs/evidence:** For sql-15 Exercise 1, `LEFT JOIN` all 500 `customers` to their `orders`, then count `o.order_id`, sum `total_amount` with `COALESCE(..., 0)`, and take `MAX(order_date)` per customer.
   **Expected result/shape:** For sql-15 Exercise 1, return 500 rows, one per customer, led by customer 181 (FR, 16 orders, 9502.21) and ending with the 62 `BR` customers who never ordered, each with 0 orders, 0 revenue, and a `NULL` `latest_order_date`. The final columns are `customer_id`, `full_name`, `country`, `order_count`, `stored_revenue`, and `latest_order_date`. The final order is `stored_revenue DESC, c.customer_id`.
   **Verify:** For sql-15 Exercise 1, confirm 500 distinct `customer_id` values, `SUM(order_count)` = 4,362, and `SUM(stored_revenue)` = 2355646.89, matching `orders`. Swap `COUNT(o.order_id)` for `COUNT(*)` and the 62 no-order customers must show 1 instead of 0. Customers 51 and 428 tie at 8970.66, so `c.customer_id` must place 51 first on every run.
2. **Query writing:** Create a product profitability table from net order-line revenue and catalog cost.
   **Progressive hint:** Calculate line revenue and line cost at item grain, then aggregate to product.
   **Predict:** the catalog has 300 products; which ones can an inner join to `order_items` never return?
   **Inputs/evidence:** For sql-15 Exercise 2, inner-join `products` to `order_items` and, per product, sum `quantity`, net line revenue, catalog cost `p.cost * oi.quantity`, and their difference as `gross_profit`.
   **Expected result/shape:** For sql-15 Exercise 2, return 275 rows, one per product that has sold at least once, led by product 271 (Apparel, 160 units, `gross_profit` 10939.20) and ending with product 3 at 323.61; products 276 to 300 have no item rows and are left out. The final columns are `product_id`, `name`, `category`, `units_sold`, `net_revenue`, `catalog_cost`, and `gross_profit`. The final order is `gross_profit DESC, p.product_id`.
   **Verify:** For sql-15 Exercise 2, confirm 275 distinct `product_id` values, `SUM(units_sold)` = 39,257, and `SUM(net_revenue)` = 2355647.12, the item-level total. Inside a rolled-back transaction, insert one `order_items` row for product 300 on order 1; the result must grow to 276 rows with product 300 at 1 unit sold.
3. **Query writing:** Build a UTC monthly order-status report with counts and stored revenue.
   **Progressive hint:** Derive one reporting month and group by month/status.
   **Predict:** is the row count exactly months times five statuses, or can the oldest months have gaps?
   **Inputs/evidence:** For sql-15 Exercise 3, group all 4,362 `orders` by UTC month (`date_trunc('month', o.order_date AT TIME ZONE 'UTC')`) and `status`, counting orders and summing `total_amount`.
   **Expected result/shape:** For sql-15 Exercise 3, return 224 rows, one per observed month and status pair, starting with `2023-02-01` `delivered` (1 order, 986.42); 46 months times 5 statuses would give 230, but the first three months lack 6 of the pairs. The final columns are `utc_month`, `status`, `order_count`, and `stored_revenue`. The final order is `utc_month, o.status`.
   **Verify:** For sql-15 Exercise 3, confirm 224 distinct (`utc_month`, `status`) pairs and that the `order_count` values add up to 4,362; `2023-02-01` must show only `delivered` and `shipped`. Inside a rolled-back transaction, insert one order with status `cancelled`; the result must grow to 225 rows with the new pair in the current month at 1 order.
4. **Debugging:** Reconcile stored order total, computed line total, and paid total without multiplying details.
   **Progressive hint:** Aggregate items and payments independently to order grain before joining.
   **Predict:** which `status` value marks the orders that have no payment rows, and what should their `paid_total` be?
   **Inputs/evidence:** For sql-15 Exercise 4, pre-aggregate `order_items` to `line_totals` and `payments` to `paid_totals`, one row per `order_id` each, then join both to `orders` (inner to line totals, left to payments).
   **Expected result/shape:** For sql-15 Exercise 4, return 4,362 rows, one per order; every `stored_minus_lines` is 0.00 after rounding (2,855 orders differ by under half a cent), so the order falls back to `order_id`, starting with order 21. 1,072 rows have a positive `unpaid_balance`, 873 of them `placed` orders with no payment row. The final columns are `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance`. The final order is `ABS(o.total_amount - lt.line_total) DESC, o.order_id`.
   **Verify:** For sql-15 Exercise 4, confirm 4,362 distinct `order_id` values, 0 rows with a negative `unpaid_balance`, and that `SUM(unpaid_balance)` is 523746.08, which equals 2355646.89 stored minus 1831900.81 paid. Inside a rolled-back transaction, set order 1's `total_amount` to 250.20; order 1 must jump to the first row with `stored_minus_lines` and `unpaid_balance` both 10.00.
5. **Prediction:** Compare monthly budgets with actual expenses and preserve missing sides.
   **Progressive hint:** Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero.
   **Predict:** if both tables cover the same five categories and months, how many rows does the full join add beyond an inner join?
   **Inputs/evidence:** For sql-15 Exercise 5, sum the 10,000 `expenses` rows by `category` and calendar month, sum the 125 `budgets` rows by `category` and `period`, then `FULL JOIN` the two summaries on both keys.
   **Expected result/shape:** For sql-15 Exercise 5, return 125 rows, 5 categories (`COGS`, `G&A`, `Infrastructure`, `Marketing`, `Payroll`) times 25 months from `2024-11-01` to `2026-11-01`; on the fixture every pair has both a budget and an actual, so no column is `NULL`. The first row is `COGS` for `2024-11-01` with 654000.00 budgeted against 72384.36 spent. The final columns are `category`, `period`, `budget_amount`, `actual_amount`, and `variance`. The final order is `period, category`.
   **Verify:** For sql-15 Exercise 5, confirm 125 distinct (`category`, `period`) pairs; joining raw `budgets` to raw `expenses` instead returns 10,000 rows, one per expense, which is the fanout the two summaries prevent. Inside a rolled-back transaction, add a `Travel` budget for `2026-11-01` and a `Legal` expense dated `2026-11-10`; both must appear, `Travel` with a `NULL` actual and `Legal` with a `NULL` budget, and both with a `NULL` variance.
6. **Extension:** Produce one executive summary row with population, activity, stored revenue, computed revenue, and payments.
   **Progressive hint:** Compute independent one-row aggregates, then cross join them to avoid detail multiplication.
   **Predict:** should stored revenue and computed line revenue match to the cent, and should payments match either one?
   **Inputs/evidence:** For sql-15 Exercise 6, compute each total in its own single-row CTE (customer count, order count and stored revenue, line revenue from `order_items`, and payment sum) and `CROSS JOIN` the four one-row results.
   **Expected result/shape:** For sql-15 Exercise 6, return one row: 500 customers, 4,362 orders, `stored_revenue` 2355646.89, `computed_revenue` 2355647.12, and `payments` 1831900.81. The final columns are `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments`.
   **Verify:** For sql-15 Exercise 6, confirm each value against its own query, for example `SELECT ROUND(SUM(amount), 2) FROM payments` returns 1831900.81. Then sum `o.total_amount` after `orders JOIN order_items` and get 8633041.53, more than 3.6 times the stored figure; that fanout is why every total is computed before the `CROSS JOIN`.

## Common mistakes and how to recover

- **Joining payments straight to order lines:** 347 orders have two payments, so `JOIN payments` before aggregating repeats every line of those orders. Exercise 4 avoids it by summing `payments` per order in its own CTE first.
- **`COUNT(*)` after a left join:** in Exercise 1 a customer with no orders still produces one joined row, so `COUNT(*)` reports one order for each of the 62 BR customers. `COUNT(o.order_id)` ignores the NULL and gives 0.
- **Using `COALESCE(..., 0)` everywhere:** in Exercise 4 a missing payment really is zero paid, so the 873 `placed` orders show their full total as `unpaid_balance`. Exercise 5 keeps a missing budget or actual as NULL, because a month with no budget is not a month budgeted at zero.
- **Truncating in the session time zone:** Exercise 3 groups on `order_date AT TIME ZONE 'UTC'`. Truncating the raw `timestamptz` uses the session's zone, so an order placed late on a month's last day can move to the next month when that setting changes.
- **Mixing revenue definitions:** stored `total_amount` and computed line revenue agree within half a cent per order but differ by 0.23 overall. Name the definition in each column alias instead of adding one to the other.

Transcript errors and missing relations: [recovering from common failures](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Does the grand total equal the independent net-line-revenue control?
- Are date window, payment handling, zero-activity entities, and subtotal
  `NULL`s documented?

## Next step

Continue to [Day 16; window-function fundamentals](day16_window_functions_fundamentals.md).

## Deep dive and reference

Goal
- Produce a robust monthly revenue report segmented by customer attributes and product categories using techniques from Days 01-14.

What you’ll build
- Extend the supplied monthly segment-country report while retaining its
  revenue, active-customer, and revenue-per-active metrics.
- Add at least two dimensions. The learner script suggests payment method and
  product category.

Guidance
1) Keep product category at line grain before aggregating; it cannot be
   recovered after all lines have been collapsed to one order total.
2) Pre-aggregate payments to the order-method grain before joining to lines.
3) Aggregate by month, segment, country, and the two chosen dimensions.
4) Validate totals against net line revenue and inspect split-payment orders.
5) Document whether all order statuses are included; the starter query does not
   exclude `placed`, `returned`, or any other status.

Quality checklist
- Correct join cardinality (no double counting)
- Handling of NULL/unknown categories and segments
- Performance: indices on join keys; avoid unnecessary DISTINCT

Deliverable checklist
- Complete all six prompts above and document grain, missing-side behavior,
  UTC boundaries, money definitions, and reconciliation evidence.

## Ask an AI tutor about this lesson

No tutor is needed to finish the project. If you use one, paste the prompt below and ask it to challenge your Exercise 4 reconciliation: which orders should carry a nonzero `unpaid_balance`, and why. The [tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) cover keeping `solutions/` closed until you ask.

```text
Tutor me through sql-15: Phase 1 Project: Multi-Dimensional Revenue Report.

I have completed the direct catalog prerequisite: `sql-14`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day15_phase1_project.md
- Answer-free learner SQL: sql/postgres-60day/day15_phase1_project.sql

Key terms to teach in context: Metric contract, Dimensional report, Control total. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Build one stable `order_lines` relation first, with one row per intended line or order and a single net-revenue formula. Reconcile its total, then add dimension joins one at a time and compare the total after each join. Only after totals remain stable should you add grouping sets and display labels.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-15/ working copy. Never point setup, reset, DDL, or DML
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
