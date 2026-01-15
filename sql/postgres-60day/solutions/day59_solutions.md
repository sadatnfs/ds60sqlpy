# Day 59 — Solutions (Final Capstone, Part 2 — KPIs, Performance, Stakeholder Views)

We assemble business KPIs, add performance aids (indexes + EXPLAIN), and build stakeholder views. Below are step‑by‑step, line‑by‑line explanations for each section of the day’s SQL.

KPI A — LTV by cohort and segment (annotated)
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
Line‑by‑line
- order_values: collapse each order to a revenue number at order grain.
- ltv: per‑customer lifetime value and first_order_month (for context).
- cohort: attach signup cohort month and segment.
- Final: average LTV by (segment, cohort_month); COUNT gives cohort size for interpretation.

KPI B — Conversion funnel from events → orders (last 90 days)
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
Notes
- MAX(CASE ...) turns presence of an event into a 0/1 flag per customer.
- buyers CTE counts unique purchasers in the same window.
- Compare ratios buyers/viewers, checkouts/adders, etc. for funnel drop‑offs.

KPI C — Top product pairs revenue (market basket)
```sql
WITH items AS (
  SELECT order_id, product_id FROM order_items GROUP BY order_id, product_id
), pairs AS (
  SELECT a.product_id AS p1, b.product_id AS p2, COUNT(*) AS together
  FROM items a
  JOIN items b ON a.order_id = b.order_id AND a.product_id < b.product_id
  GROUP BY a.product_id, b.product_id
)
SELECT p1.name AS product_a, p2.name AS product_b, together
FROM pairs
JOIN products p1 ON p1.product_id = pairs.p1
JOIN products p2 ON p2.product_id = pairs.p2
ORDER BY together DESC
LIMIT 20;
```
Line‑by‑line
- Distinct items per order avoid double counting.
- a.product_id < b.product_id enforces one ordering for pairs.
- Join names for a human‑readable report; LIMIT to top pairs.

Performance aids — Indexes and EXPLAIN (annotated)
```sql
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_order_date ON payments(order_id, payment_date);

EXPLAIN ANALYZE
SELECT o.customer_id, SUM(o.total_amount)
FROM orders o
WHERE o.order_date >= now() - interval '180 days'
GROUP BY o.customer_id
ORDER BY SUM(o.total_amount) DESC
LIMIT 50;
```
How to read the plan
- Expect an index/bitmap scan on orders constrained by order_date (or a seq scan if table is small).
- Check rows/loops vs actuals; high misestimates suggest ANALYZE or better stats.
- Look at Sort method (memory vs disk) and overall execution time.

Stakeholder views — Finance: Budget vs Actual YTD
```sql
WITH ytd_exp AS (
  SELECT date_trunc('year', expense_date)::date AS yr,
         category,
         SUM(amount) AS actual
  FROM expenses
  WHERE expense_date >= date_trunc('year', now())
  GROUP BY 1,2
), ytd_bud AS (
  SELECT date_trunc('year', period)::date AS yr,
         category,
         SUM(amount) AS budget
  FROM budgets
  WHERE period >= date_trunc('year', now())
  GROUP BY 1,2
)
SELECT COALESCE(b.category, e.category) AS category,
       COALESCE(b.yr, e.yr) AS year,
       COALESCE(b.budget,0) AS budget_ytd,
       COALESCE(e.actual,0) AS actual_ytd,
       ROUND(COALESCE(e.actual,0) - COALESCE(b.budget,0),2) AS variance
FROM ytd_bud b
FULL OUTER JOIN ytd_exp e ON e.yr=b.yr AND e.category=b.category
ORDER BY category;
```
Line‑by‑line
- date_trunc('year') aligns months into YTD totals.
- FULL OUTER JOIN ensures categories present in one side still show up.

Stakeholder views — Marketing: Campaign‑assisted purchases (within 7 days)
```sql
WITH first_purchase AS (
  SELECT o.customer_id, MIN(o.order_date) AS first_buy
  FROM orders o
  GROUP BY o.customer_id
), touch AS (
  SELECT e.customer_id, e.event_time, COALESCE(e.metadata->>'campaign','none') AS campaign
  FROM events e
)
SELECT t.campaign,
       COUNT(DISTINCT t.customer_id) AS assisted_customers
FROM touch t
JOIN first_purchase fp ON fp.customer_id = t.customer_id
WHERE t.event_time BETWEEN fp.first_buy - interval '7 days' AND fp.first_buy
GROUP BY t.campaign
ORDER BY assisted_customers DESC
LIMIT 20;
```
Notes
- Counts customers, not touches; switch to COUNT(*) for touch counts.
- Adjust window length per business definition of assistance.

Operational tips
- Keep separate notebooks/tickets for each KPI with its SQL and EXPLAIN before/after.
- Save plan text and timing for regression detection after deployments.
