# Day 15 — Phase 1 Project: Multi-Dimensional Revenue Report (Companion Guide)

Goal
- Produce a robust monthly revenue report segmented by customer attributes and product categories using techniques from Days 01–14.

What you’ll build
- A CTE pipeline that computes order-level revenue, joins customer and product dimensions, and aggregates to month.
- Metrics: revenue, active customers, AOV (revenue/actives). Add at least two more dimensions (e.g., payment method, promo flag).

Guidance
1) Start from an order_lines CTE: SUM(oi.unit_price*oi.quantity*(1-oi.discount)) per order_id.
2) Join customers/products; ensure you don’t create fanout (aggregate lines before joining both dimensions).
3) Aggregate by date_trunc('month', order_date), segment, country, category.
4) Validate totals: compare against naive sums; check NULLs and missing categories.
5) Document assumptions (returns, canceled orders) and edge cases.

Quality checklist
- Correct join cardinality (no double counting)
- Handling of NULL/unknown categories and segments
- Performance: indices on join keys; avoid unnecessary DISTINCT

Stretch goals
- Add a dimension for new vs returning customers per month.
- Parameterize date range; output to a materialized view for reuse.

Deliverable
- Final query with comments, plus a short findings write-up (top segments, trends, anomalies).
