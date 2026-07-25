# Day 60 Solution — End-to-End Capstone Sign-off

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
