# Day 46 — Solutions (Project 1: E‑commerce Analytics, Part 1)

Today’s scripts compute customer lifetime value (LTV) and cohorts. Below are detailed, line‑by‑line solutions to the practice exercises.

Prereqs we’ll reuse
- Compute per‑customer LTV at order grain, then roll up
- Derive customer cohort by signup month

Reference snippet from the lesson (annotated)
```sql
WITH order_values AS (
  SELECT o.customer_id,
         -- order_value = sum of item price * qty, after discount
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value,
         o.order_id
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
), ltv AS (
  SELECT customer_id,
         ROUND(SUM(order_value), 2) AS ltv
  FROM order_values
  GROUP BY customer_id
)
SELECT c.customer_id, c.country, c.segment, l.ltv,
       NTILE(4) OVER (ORDER BY l.ltv DESC) AS ltv_quartile
FROM customers c
JOIN ltv l ON l.customer_id = c.customer_id
ORDER BY l.ltv DESC
LIMIT 100;
```
Explanation
- order_values CTE: collapse each order to one number (order_value). We group by (customer_id, order_id) so each order contributes exactly once.
- ltv CTE: roll up per customer by summing their orders. ROUND to 2 decimals for currency display.
- Final SELECT: join demographics (customers) to metrics (ltv). NTILE(4) assigns quartiles purely for inspection.

Exercise 1 — Create LTV segments (gold/silver/bronze) and analyze by country
Goal
- Turn numeric LTV into labeled segments, then aggregate by country to see distribution and totals.

Two common approaches
- Static thresholds (easiest for beginners)
- Dynamic thresholds (percentiles) when scale varies

A) Static thresholds example
```sql
WITH order_values AS (
  SELECT o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value,
         o.order_id
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
), ltv AS (
  SELECT customer_id, SUM(order_value) AS ltv
  FROM order_values
  GROUP BY customer_id
), segmented AS (
  SELECT c.customer_id,
         c.country,
         l.ltv,
         CASE
           WHEN l.ltv >= 1000 THEN 'gold'
           WHEN l.ltv >= 200  THEN 'silver'
           ELSE 'bronze'
         END AS ltv_segment
  FROM customers c
  JOIN ltv l ON l.customer_id = c.customer_id
)
SELECT country,
       ltv_segment,
       COUNT(*)                         AS customers,
       ROUND(SUM(ltv), 2)               AS total_ltv,
       ROUND(AVG(ltv), 2)               AS avg_ltv
FROM segmented
GROUP BY country, ltv_segment
ORDER BY country, -- alphabetical by country for report‑like readability
         CASE ltv_segment
           WHEN 'gold' THEN 1
           WHEN 'silver' THEN 2
           ELSE 3
         END;
```
Line‑by‑line notes
- order_values: same pattern as lesson. Compute per‑order revenue at item level.
- ltv: sum per customer => numeric LTV.
- segmented: attach labels with CASE; thresholds are example values you can tune.
- Final SELECT: aggregate by country + segment to see population and value.

B) Dynamic thresholds via percentiles (optional)
```sql
WITH order_values AS (
  SELECT o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value,
         o.order_id
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
), ltv AS (
  SELECT customer_id, SUM(order_value) AS ltv
  FROM order_values
  GROUP BY customer_id
), cuts AS (
  SELECT percentile_cont(0.33) WITHIN GROUP (ORDER BY ltv) AS p33,
         percentile_cont(0.66) WITHIN GROUP (ORDER BY ltv) AS p66
  FROM ltv
), segmented AS (
  SELECT c.customer_id, c.country, l.ltv,
         CASE
           WHEN l.ltv >= (SELECT p66 FROM cuts) THEN 'gold'
           WHEN l.ltv >= (SELECT p33 FROM cuts) THEN 'silver'
           ELSE 'bronze'
         END AS ltv_segment
  FROM customers c
  JOIN ltv l ON l.customer_id = c.customer_id
)
SELECT country, ltv_segment, COUNT(*) AS customers,
       ROUND(SUM(ltv), 2) AS total_ltv,
       ROUND(AVG(ltv), 2) AS avg_ltv
FROM segmented
GROUP BY country, ltv_segment
ORDER BY country, ltv_segment;
```
Notes
- cuts CTE computes dynamic breakpoints (33rd/66th percentile). This adapts to data scale.

Exercise 2 — Compute revenue per cohort month at month offsets 0..12
Goal
- Organize revenue by cohort (signup month) and how many months after signup the revenue occurred.

Solution
```sql
WITH cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month
  FROM customers c
), orders_m AS (
  SELECT o.customer_id,
         date_trunc('month', o.order_date)::date AS order_month,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, date_trunc('month', o.order_date)
), joined AS (
  SELECT co.cohort_month,
         om.order_month,
         EXTRACT(MONTH FROM age(om.order_month, co.cohort_month))::int AS month_offset,
         SUM(om.order_revenue) AS revenue
  FROM orders_m om
  JOIN cohorts co ON co.customer_id = om.customer_id
  GROUP BY co.cohort_month, om.order_month
)
SELECT cohort_month,
       month_offset,
       ROUND(revenue, 2) AS revenue
FROM joined
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month DESC, month_offset;
```
Line‑by‑line notes
- cohorts: anchor each customer to the month they signed up (their cohort).
- orders_m: collapse orders to month grain and sum item‑level revenue.
- joined: month_offset = months since cohort_month when revenue happened.
- Final filter restricts to the first 13 months of lifecycle (0..12).

Going further
- Pivot month_offset into columns for a cohort table (e.g., with crosstab) for BI‑style heatmaps.
- Normalize to per‑customer revenue to compare cohorts of different sizes.
