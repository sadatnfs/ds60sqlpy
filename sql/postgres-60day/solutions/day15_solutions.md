# Day 15 solutions — Phase 1 Project: Multi-Dimensional Revenue Report

These answers align one-for-one with [day15_phase1_project.sql](../day15_phase1_project.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.
- **Assumptions:** All monetary summaries identify stored totals versus computed net line revenue. Reporting month uses UTC and empty populations remain visible where required.
- **Primary pitfall:** Combining fact tables before fixing their grain multiplies measures; every project output must state its row grain and acceptance checks.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Create a customer performance table with order count, stored revenue, and latest order date, retaining customers with no orders.

**Reasoning:** Left join from customers and aggregate at customer grain.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name,
       c.country,
       COUNT(o.order_id) AS order_count,
       COALESCE(ROUND(SUM(o.total_amount), 2), 0) AS stored_revenue,
       MAX(o.order_date) AS latest_order_date
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name, c.country
ORDER BY stored_revenue DESC, c.customer_id;
```

**Expected shape:** One row per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 2 — Query writing

**Prompt:** Create a product profitability table from net order-line revenue and catalog cost.

**Reasoning:** Calculate line revenue and line cost at item grain, then aggregate to product.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT p.product_id,
       p.name,
       p.category,
       SUM(oi.quantity) AS units_sold,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_revenue,
       ROUND(SUM(p.cost * oi.quantity), 2) AS catalog_cost,
       ROUND(
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount))
           - SUM(p.cost * oi.quantity),
         2
       ) AS gross_profit
FROM products AS p
JOIN order_items AS oi
  ON oi.product_id = p.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY gross_profit DESC, p.product_id;
```

**Expected shape:** One row per sold product.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 3 — Query writing

**Prompt:** Build a UTC monthly order-status report with counts and stored revenue.

**Reasoning:** Derive one reporting month and group by month/status.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS utc_month,
       o.status,
       COUNT(*) AS order_count,
       ROUND(SUM(o.total_amount), 2) AS stored_revenue
FROM orders AS o
GROUP BY date_trunc('month', o.order_date AT TIME ZONE 'UTC'), o.status
ORDER BY utc_month, o.status;
```

**Expected shape:** One row per observed month and status.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 4 — Debugging

**Prompt:** Reconcile stored order total, computed line total, and paid total without multiplying details.

**Reasoning:** Aggregate items and payments independently to order grain before joining.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH line_totals AS (
  SELECT oi.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_total
  FROM order_items AS oi
  GROUP BY oi.order_id
), paid_totals AS (
  SELECT p.order_id,
         SUM(p.amount) AS paid_total
  FROM payments AS p
  GROUP BY p.order_id
)
SELECT o.order_id,
       ROUND(o.total_amount, 2) AS stored_total,
       ROUND(lt.line_total, 2) AS line_total,
       ROUND(COALESCE(pt.paid_total, 0), 2) AS paid_total,
       ROUND(o.total_amount - lt.line_total, 2) AS stored_minus_lines,
       ROUND(o.total_amount - COALESCE(pt.paid_total, 0), 2) AS unpaid_balance
FROM orders AS o
JOIN line_totals AS lt
  ON lt.order_id = o.order_id
LEFT JOIN paid_totals AS pt
  ON pt.order_id = o.order_id
ORDER BY ABS(o.total_amount - lt.line_total) DESC, o.order_id;
```

**Expected shape:** One row per order with differences.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 5 — Prediction

**Prompt:** Compare monthly budgets with actual expenses and preserve missing sides.

**Reasoning:** Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
- `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH actual AS (
  SELECT e.category,
         date_trunc('month', e.expense_date)::date AS period,
         SUM(e.amount) AS amount
  FROM expenses AS e
  GROUP BY e.category, date_trunc('month', e.expense_date)
), planned AS (
  SELECT b.category,
         b.period,
         SUM(b.amount) AS amount
  FROM budgets AS b
  GROUP BY b.category, b.period
)
SELECT COALESCE(p.category, a.category) AS category,
       COALESCE(p.period, a.period) AS period,
       ROUND(p.amount, 2) AS budget_amount,
       ROUND(a.amount, 2) AS actual_amount,
       ROUND(a.amount - p.amount, 2) AS variance
FROM planned AS p
FULL JOIN actual AS a
  ON a.category = p.category
 AND a.period = p.period
ORDER BY period, category;
```

**Expected shape:** One row per category/month in either source.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Exercise 6 — Extension

**Prompt:** Produce one executive summary row with population, activity, stored revenue, computed revenue, and payments.

**Reasoning:** Compute independent one-row aggregates, then cross join them to avoid detail multiplication.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.

```sql
WITH customer_kpis AS (
  SELECT COUNT(*) AS customers
  FROM customers
), order_kpis AS (
  SELECT COUNT(*) AS orders,
         SUM(total_amount) AS stored_revenue
  FROM orders
), line_kpis AS (
  SELECT SUM(unit_price * quantity * (1 - discount)) AS computed_revenue
  FROM order_items
), payment_kpis AS (
  SELECT SUM(amount) AS payments
  FROM payments
)
SELECT c.customers,
       o.orders,
       ROUND(o.stored_revenue, 2) AS stored_revenue,
       ROUND(l.computed_revenue, 2) AS computed_revenue,
       ROUND(p.payments, 2) AS payments
FROM customer_kpis AS c
CROSS JOIN order_kpis AS o
CROSS JOIN line_kpis AS l
CROSS JOIN payment_kpis AS p;
```

**Expected shape:** Exactly one summary row.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
