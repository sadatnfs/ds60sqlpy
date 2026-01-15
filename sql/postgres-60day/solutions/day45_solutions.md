# Day 45 — Solutions (Phase 3 Optimization Project)

In this project day we create a repeatable optimization workflow: measure → hypothesize → change → verify → guardrail. We’ll tune a representative workload (reporting + API reads), addressing schema, indexing, query structure, and caching. Each section shows concrete SQL and the rationale.

Goal
- Reduce P95 latency and total CPU for the top N queries while preserving correctness
- Produce a runbook and guardrails to prevent regressions

Baseline (measure)
```sql
-- Reset counters (if allowed) and gather current top queries
SELECT pg_stat_statements_reset();
-- Let the system run under typical load, then sample:
SELECT queryid,
       calls,
       round(total_exec_time/1000,2) AS total_s,
       round(mean_exec_time ,2)      AS mean_ms,
       rows,
       left(query,160) AS sample
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```
Run EXPLAIN (ANALYZE, BUFFERS) for the worst offenders. Capture the plan text into your ticket for before/after diffs.

1) Index and predicate tuning
- Make predicates sargable (no functions/casts on columns)
- Align composite index order with common filters and ORDER BY
```sql
-- Example: frequent shape WHERE customer_id=? AND order_date BETWEEN ... ORDER BY order_date DESC
CREATE INDEX IF NOT EXISTS idx_orders_cust_date_desc ON orders(customer_id, order_date DESC);

-- Time-window queries
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);

-- Case-insensitive lookups
CREATE INDEX IF NOT EXISTS idx_customers_email_lower ON customers (lower(email));
```
Verify improvement with EXPLAIN (ANALYZE, BUFFERS) and pg_stat_statements deltas.

2) Query shape refactors (avoid fanout, pre-aggregate)
```sql
-- Anti-pattern: join raw 1:N then group at the end
-- Refactor to pre-aggregate items to order grain
WITH order_lines AS (
  SELECT oi.order_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_revenue
  FROM order_items oi
  GROUP BY oi.order_id
)
SELECT c.country,
       SUM(ol.order_revenue) AS revenue
FROM orders o
JOIN customers c ON c.customer_id=o.customer_id
JOIN order_lines ol ON ol.order_id=o.order_id
GROUP BY c.country;
```
Use CTEs only for readability; ensure PG12+ inlines them (avoid forced materialization on old versions).

3) Materialized views / caching expensive aggregates
```sql
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_monthly_country AS
SELECT date_trunc('month', o.order_date)::date AS month,
       c.country,
       SUM(o.total_amount) AS revenue,
       COUNT(*) AS orders
FROM orders o
JOIN customers c ON c.customer_id=o.customer_id
GROUP BY 1,2;

CREATE UNIQUE INDEX IF NOT EXISTS uid_mv_monthly_country ON mv_monthly_country (month, country);
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_country;
```
Consumers read from the MV; schedule refresh aligned with freshness needs.

4) Partitioning for large fact tables (optional)
```sql
-- RANGE partition by month to prune old data quickly and reduce scan footprint
-- (See Day 37 for full example)
```
Confirm partition pruning via EXPLAIN.

5) JSONB/text search acceleration
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_products_name_trgm ON products USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_products_extra_gin ON products USING gin (extra jsonb_path_ops);
```
Rewrite infix ILIKE and JSONB @> filters to use these indexes.

6) Concurrency and lock avoidance
- Adopt SKIP LOCKED for worker queues
- Use NOWAIT for user-facing fast-fail operations
```sql
WITH take AS (
  SELECT id FROM jobs WHERE status='queued' ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 20
)
UPDATE jobs j SET status='in_progress' FROM take t WHERE j.id=t.id RETURNING j.*;
```

7) Guardrails (correctness + perf)
- Unit queries: row counts, sums, and key business metrics compared before/after
- EXPLAIN budget: ensure no large seq scan sneaks in; add expected plan checks to CI if possible
- Non-regression checks for P95 latency with a load test (keep artifacts)

8) Rollout plan
- Apply DDL during a low-traffic window (CONCURRENTLY when possible)
- Enable auto_explain in staging first; watch for slow-plan regressions
- Monitor pg_stat_statements total_exec_time for targets over 24–48h

Checklist (tick when complete)
- [ ] Baseline captured (pg_stat_statements, EXPLAIN plans)
- [ ] Indexes created/aligned; predicates made sargable
- [ ] Query shapes refactored to pre-aggregate
- [ ] Caching/MVs introduced with refresh schedule
- [ ] (Optional) Partitioning tested and pruning verified
- [ ] Concurrency patterns updated (NOWAIT/SKIP LOCKED)
- [ ] Guardrails written (unit/profiling/latency tests)
- [ ] Rollout executed; monitor & iterate
