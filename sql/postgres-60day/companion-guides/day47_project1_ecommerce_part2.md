# Day 47 — Project 1: E‑commerce (Part 2) — Retention, Cohorts, and Funnels (Companion Guide)

Objectives
- Build retention/returning behavior views by cohort and months‑since‑signup
- Create a cohort retention matrix (cohort_month × month_offset)
- Model a purchase funnel and compute step‑to‑step conversion rates

Why this matters
Acquisition without retention is a leaky bucket. Cohort retention normalizes behavior over time and funnels reveal where customers drop off.

Data model refresh
- Customers (created_at, segment, country)
- Orders (order_date, customer_id, total_amount, status)
- Events (occurred_at, customer_id, kind, payload)

Cohort and retention pipeline (CTEs)
1) cohorts AS (
   SELECT customer_id,
          date_trunc('month', created_at)::date AS cohort_month
   FROM customers)
2) order_months AS (
   SELECT o.customer_id,
          date_trunc('month', o.order_date)::date AS order_month
   FROM orders o)
3) offsets AS (
   SELECT c.cohort_month,
          o.customer_id,
          (EXTRACT(YEAR FROM o.order_month)*12 + EXTRACT(MONTH FROM o.order_month)
           - (EXTRACT(YEAR FROM c.cohort_month)*12 + EXTRACT(MONTH FROM c.cohort_month)))::int AS month_offset
   FROM cohorts c
   JOIN order_months o USING (customer_id)
   WHERE o.order_month >= c.cohort_month)
4) retention AS (
   SELECT cohort_month, month_offset, COUNT(DISTINCT customer_id) AS active_customers
   FROM offsets
   GROUP BY 1,2)
5) cohort_sizes AS (
   SELECT cohort_month, COUNT(*) AS cohort_size
   FROM cohorts GROUP BY 1)

Outputs
- Retention rate per offset: active_customers / cohort_size
- Retention matrix pivot (optional with crosstab) or conditional aggregation

Funnel analysis
- Define steps (e.g., visit → add_to_cart → checkout → purchase) using events.kind
- For a time window (e.g., first 30 days post‑signup), compute counts per step and conversion rates
- Use semi‑joins/EXISTS per step keyed by customer or session; ensure step ordering via occurred_at

Techniques used
- Date math for month offsets
- COUNT(DISTINCT ...) with cohort denominators
- Conditional aggregation or crosstab for matrices

Pitfalls
- Misaligned calendars (use date_trunc('month') everywhere)
- Counting repeat orders instead of active customers (distinct customer_ids per offset)
- Including months before signup; enforce o.order_month >= cohort_month

Deliverables
- Table/view retention_rates(cohort_month, month_offset, retention_rate)
- Funnel summary with step counts and conversion rates, segmented by cohort or segment

Stretch goals
- Revenue retention (sum order totals) in addition to customer count retention
- Survival curves and median time‑to‑second‑purchase
