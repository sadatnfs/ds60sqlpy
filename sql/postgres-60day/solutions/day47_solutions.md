# Day 47 Solutions — E-commerce Analytics, Part 2

The deliverables are a true retention rate and a tidy six-cohort result suitable
for a line chart. See [`day47_solutions.sql`](day47_solutions.sql).

## Exercises 1 and 2 — Retention rate and chart-ready curves

```sql
SET search_path TO training, public;

WITH cohorts AS (
  SELECT customer_id,
         date_trunc('month', created_at)::date AS cohort_month
  FROM customers
), cohort_sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_size
  FROM cohorts
  GROUP BY cohort_month
), active_months AS (
  SELECT customer_id,
         date_trunc('month', order_date)::date AS order_month
  FROM orders
  GROUP BY customer_id, date_trunc('month', order_date)
), retained AS (
  SELECT c.cohort_month,
         a.order_month,
         (
           EXTRACT(year FROM age(a.order_month, c.cohort_month)) * 12
           + EXTRACT(month FROM age(a.order_month, c.cohort_month))
         )::int AS month_offset,
         COUNT(DISTINCT a.customer_id) AS active_customers
  FROM cohorts c
  JOIN active_months a USING (customer_id)
  GROUP BY c.cohort_month, a.order_month
), curves AS (
  SELECT r.cohort_month,
         r.month_offset,
         s.cohort_size,
         r.active_customers,
         r.active_customers::numeric / NULLIF(s.cohort_size, 0) AS retention_rate
  FROM retained r
  JOIN cohort_sizes s USING (cohort_month)
  WHERE r.month_offset BETWEEN 0 AND 12
), latest_six AS (
  SELECT cohort_month
  FROM cohort_sizes
  ORDER BY cohort_month DESC
  LIMIT 6
)
SELECT cohort_month,
       month_offset,
       cohort_size,
       active_customers,
       ROUND(retention_rate, 4) AS retention_rate
FROM curves
WHERE cohort_month IN (SELECT cohort_month FROM latest_six)
ORDER BY cohort_month DESC, month_offset;
```

Expected grain: one row per `(cohort_month, month_offset)` for the six newest
signup cohorts, with numerator, denominator, and rate. Chart with
`month_offset` on X, `retention_rate` on Y, and `cohort_month` as the series.
The chart itself is explicitly outside SQL; this answer produces the tidy data
to export or pass to a notebook/BI tool.

## Reasoning, safety, and pitfalls

- `active_months` deliberately deduplicates multiple orders by one customer in
  one month.
- Cohort size is all signups in the cohort, not only customers who eventually
  ordered.
- Cast before division to avoid integer truncation.
- A missing row at an offset is different from a zero-rate row. To force a
  complete retention matrix, cross join cohorts to `generate_series(0, 12)` and
  left join activity.
- The seed is synthetic, so chart shape demonstrates technique rather than a
  business retention benchmark.

## Exercise 1 — Calculate retention rates

`cohort_sizes` supplies the denominator and active distinct customers supply the
numerator. Numeric casting prevents integer truncation.

## Exercise 2 — Return six tidy curves

The final rows retain cohort month, offset, size, active count, and rate. “Chart
it” is downstream presentation; SQL should preserve the auditable components.

## Exercise 3 — Choose a cohort anchor

Signup month measures post-registration behavior; first-order month measures
repeat purchasing. The answer displays both per customer so the semantic choice
is visible.

## Exercise 4 — Complete the cohort grid

Cross joining cohorts with offsets creates every expected cell. A left join
then turns missing observed activity into zero without losing cohort size.

## Exercise 5 — Reject negative chronology

The diagnostic returns customers whose first order precedes recorded signup.
Such rows should be corrected or explicitly excluded before retention math.

## Exercise 6 — Preserve future unknowns

An offset beyond the latest observed month is not a measured zero. The
`is_observable` flag keeps not-yet-available periods distinct.
