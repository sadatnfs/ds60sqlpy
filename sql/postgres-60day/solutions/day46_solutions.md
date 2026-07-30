# Day 46 Solutions — E-commerce Analytics, Part 1

This project begins with explicit lifetime-value segments and signup-cohort
revenue. The canonical executable answer is
[`day46_solutions.sql`](day46_solutions.sql).

## Exercise 1 — Gold, silver, and bronze LTV by country

The thresholds below are example business policy. Confirm or tune them for a
real organization rather than presenting them as statistically derived.

```sql
SET search_path TO training, public;

WITH lifetime AS (
  SELECT c.customer_id,
         c.country,
         COALESCE(SUM(o.total_amount), 0) AS ltv
  FROM customers c
  LEFT JOIN orders o USING (customer_id)
  GROUP BY c.customer_id, c.country
), segmented AS (
  SELECT *,
         CASE
           WHEN ltv >= 20000 THEN 'gold'
           WHEN ltv >= 10000 THEN 'silver'
           ELSE 'bronze'
         END AS ltv_segment
  FROM lifetime
)
SELECT country,
       ltv_segment,
       COUNT(*) AS customers,
       ROUND(AVG(ltv), 2) AS avg_ltv,
       ROUND(SUM(ltv), 2) AS total_ltv
FROM segmented
GROUP BY country, ltv_segment
ORDER BY country, avg_ltv DESC;
```

Expected grain: one row per `(country, ltv_segment)`. The `LEFT JOIN` retains
customers with no orders and assigns them zero LTV.

## Exercise 2 — Cohort revenue at month offsets 0 through 12

```sql
SET search_path TO training, public;

WITH cohorts AS (
  SELECT customer_id,
         date_trunc('month', created_at)::date AS cohort_month
  FROM customers
), monthly_customer AS (
  SELECT customer_id,
         date_trunc('month', order_date)::date AS order_month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY customer_id, date_trunc('month', order_date)
), cohort_revenue AS (
  SELECT c.cohort_month,
         mc.order_month,
         (
           EXTRACT(year FROM age(mc.order_month, c.cohort_month)) * 12
           + EXTRACT(month FROM age(mc.order_month, c.cohort_month))
         )::int AS month_offset,
         SUM(mc.revenue) AS revenue
  FROM cohorts c
  JOIN monthly_customer mc USING (customer_id)
  GROUP BY c.cohort_month, mc.order_month
)
SELECT cohort_month,
       month_offset,
       ROUND(revenue, 2) AS revenue
FROM cohort_revenue
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month DESC, month_offset;
```

Expected grain: one row per cohort and lifecycle month. A missing offset means
that cohort generated no orders in that lifecycle month; it is not automatically
equivalent to a stored zero.

## Reasoning, safety, and pitfalls

- Use one customer row in the LTV CTE; joining items without first controlling
  grain can inflate totals.
- `age()` exposes both years and months. Using only `EXTRACT(month ...)` wraps
  after 11 and breaks multi-year offsets.
- Signup month defines the cohort here, while LTV includes all available order
  history.
- These answers are read-only and repeatable.

## Exercise 3 — Compare relative and fixed segments

`NTILE(4)` is recalculated over the current population, so another customer's
arrival can move a boundary. Fixed monetary thresholds are stable but require a
reviewed business policy. The executable answer displays both.

## Exercise 4 — Build a customer-grain feature row

The `behavior` CTE aggregates orders once per customer. Its outer join preserves
no-order customers and supports LTV, frequency, average order value, and recency
without mixing grains.

## Exercise 5 — Prevent LTV fanout

Line revenue is reduced to one row per order before it becomes customer LTV.
Payments would need their own order-grain aggregation; joining both raw sources
would multiply values.

## Exercise 6 — Retain no-order customers

The answer keeps the LEFT JOIN outer and applies `COALESCE` only after grouping.
A WHERE predicate on order columns would accidentally remove the intended
zero-LTV population.
