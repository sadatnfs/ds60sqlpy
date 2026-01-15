# Day 46 — Project 1: E‑commerce Analytics (Part 1) — LTV and Cohorts (Companion Guide)

Objectives
- Compute customer Lifetime Value (LTV) robustly at order and customer grain
- Build signup cohorts (by month) and basic cohort descriptors
- Segment customers by LTV for downstream analysis

Why this matters
Understanding how value accrues over time drives acquisition, retention, and budgeting decisions. Cohorts normalize comparisons across signup dates.

Plan and mental model
- Revenue at line level: quantity × unit_price × (1 − discount)
- Order totals: sum of line revenue per order
- LTV: sum of order totals per customer (optionally net of refunds, taxes)
- Cohort: date_trunc('month', created_at) per customer

Pipeline (recommended CTEs)
1) order_values(order_id, customer_id, order_value) — aggregate lines to orders
2) ltv(customer_id, ltv) — sum order_value
3) enrich(customers ⋈ ltv) — add country/segment; bucket with NTILE or CASE
4) cohorts — group customers by cohort_month and summarize profile

Key techniques in this project
- Window NTILE(4) OVER (ORDER BY ltv DESC) for quartiles
- date_trunc for monthly bucketing; COALESCE for missing segments
- Validate with sanity checks (top/bottom customers, LTV distribution)

Common pitfalls
- Fanout: joining orders to order_items to products without pre‑aggregating order items first will double count
- Missing returns/refunds handling: define whether ltv is gross or net
- Inconsistent time zone handling; keep UTC, display local on output

Deliverables
- A table/view with customer_id, cohort_month, ltv, ltv_segment, country, segment
- A summary by cohort_month with new_customers, median_ltv, p90_ltv, share by ltv_segment

Stretch goals
- Compute LTV at fixed horizons (90/180/365 days since signup) using LEAD/LAG and interval filters
- Add RFM (Recency, Frequency, Monetary) segmentation and compare to LTV quartiles

Validation checklist
- Compare LTV sums against total revenue; differences explained by returns/exclusions
- Spot check five random customers for correctness
