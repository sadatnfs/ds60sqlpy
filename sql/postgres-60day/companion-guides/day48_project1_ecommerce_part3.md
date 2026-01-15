# Day 48 — Project 1: E‑commerce (Part 3) — LTV Curves, Profitability, and Experiments (Companion Guide)

Objectives
- Produce LTV curves (cumulative revenue versus months since signup) by cohort/segment
- Incorporate cost to estimate contribution margin and payback period
- Analyze simple A/B experiments on onboarding or promotions

LTV curves
- Build months_since_signup as on Day 47; aggregate cumulative revenue per cohort and offset
- Window cumulative: SUM(revenue) OVER (PARTITION BY cohort_month ORDER BY month_offset ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
- Plot/compare curves across cohorts/segments; compute area under curve at fixed horizons (90/180/365 days)

Profitability and payback
- Add cost_of_goods (from products) and acquisition_cost per cohort (marketing)
- Contribution margin = revenue − cogs − variable_costs
- Payback month = smallest offset where cumulative margin ≥ acquisition_cost

A/B experiments (simplified)
- Define treatment flag (e.g., promo code at signup, onboarding variant) from events or attributes
- For comparable cohorts, compute uplift in activation rate, first‑purchase rate, and 90‑day LTV
- Use WHERE cohort_month in a narrow window; ensure overlap of distributions (avoid time confounding)

Techniques
- Window cumulatives, partitioned by cohort
- Joining external cost tables; careful handling of NULL costs
- Percent uplift and confidence intervals (optionally with stats functions outside SQL)

Pitfalls
- Comparing cohorts from different seasons; control for seasonality
- Average of ratios vs ratio of averages; pick the meaningful metric
- Survivorship bias (customers with more time have more chance to convert)

Deliverables
- ltv_curve table/view with cohort_month, month_offset, cum_revenue, cum_margin
- Payback summary by cohort/segment and A/B treatment flag

Stretch goals
- Quantile LTV curves (p50/p90) using ordered‑set aggregates
- CUPED or diff‑in‑diff designs for better variance reduction (outline only)
