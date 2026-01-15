# Day 33 — Solutions (Index Optimization Strategies)

We go beyond fundamentals to choose the right indexes, reduce bloat, and keep write cost under control. We cover composite indexes, partial and expression indexes, INCLUDE columns, maintenance (VACUUM/REINDEX), and when not to index.

Setup
- Workloads: mix of OLTP (writes) and analytics (reads)
- Tools: `pg_stat_user_indexes`, `pg_stat_all_tables`, `pg_stat_io` (PG16), `pgstattuple` extension for bloat estimation

Exercise 1 — Composite index ordering (leftmost prefix) and query shapes
```sql
-- Suppose frequent queries filter customer_id and order_date range, then ORDER BY order_date DESC
CREATE INDEX IF NOT EXISTS idx_orders_cust_date ON orders(customer_id, order_date DESC);

-- Satisfied by index order, no extra sort
EXPLAIN (ANALYZE)
SELECT order_id, order_date, total_amount
FROM orders
WHERE customer_id = 123 AND order_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY order_date DESC
LIMIT 100;
```
Guidance
- Order columns by equality predicates first (customer_id), then range/sort column (order_date). If many shapes exist, consider multiple targeted indexes rather than one giant index.

Exercise 2 — Partial indexes for hot partitions
```sql
-- Only index recent orders commonly queried, cut write cost and index size
CREATE INDEX IF NOT EXISTS idx_orders_recent
  ON orders(order_date)
  WHERE order_date >= CURRENT_DATE - INTERVAL '180 days';

EXPLAIN (ANALYZE)
SELECT *
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '90 days';
```
Notes
- Planner uses partial index only if predicate implies the index WHERE clause. Good for time‑series/soft deletes (WHERE deleted_at IS NULL).

Exercise 3 — Expression indexes and function calls in predicates
```sql
-- Case-insensitive search on email
CREATE INDEX IF NOT EXISTS idx_customers_email_lower ON customers (lower(email));

EXPLAIN (ANALYZE)
SELECT customer_id
FROM customers
WHERE lower(email) = lower('User@Example.com');
```
Why
- Without expression index, wrapping column in a function blocks regular index use. Normalize inputs or index the expression you query.

Exercise 4 — INCLUDE for covering scans
```sql
-- Keep key order on (customer_id, order_date) but include total_amount for covering
CREATE INDEX IF NOT EXISTS idx_orders_cover2
  ON orders(customer_id, order_date)
  INCLUDE (total_amount);

EXPLAIN (ANALYZE)
SELECT customer_id, order_date, total_amount
FROM orders
WHERE customer_id = 123
ORDER BY order_date DESC
LIMIT 50;
```
Notes
- INCLUDE columns are stored in the index but do not affect sort order; enables Index Only Scans (if visibility map allows).

Exercise 5 — GIN/Trigram tuning
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_products_name_trgm ON products USING gin (name gin_trgm_ops);
SET pg_trgm.similarity_threshold = 0.3;  -- example tuning
SELECT * FROM products WHERE name ILIKE '%notebook%';
```
Tips
- Lower thresholds increase recall but may increase false positives and cost. Measure with EXPLAIN ANALYZE.

Exercise 6 — Bloat detection and maintenance (safely)
```sql
-- Estimate bloat (requires pgstattuple)
CREATE EXTENSION IF NOT EXISTS pgstattuple;
SELECT indexrelid::regclass AS index, *
FROM pgstatindex('idx_orders_cust_date');

-- Rebuild a bloated index concurrently (avoids long locks)
REINDEX INDEX CONCURRENTLY idx_orders_cust_date;
```
Best practices
- Avoid indexing low‑cardinality flags unless they are heavily filtered with selective predicates combined.
- Monitor `pg_stat_user_indexes.idx_scan` vs `idx_tup_read/fetched` to drop unused/low‑value indexes.
- Keep indexes narrow and purpose‑built; test with EXPLAIN (ANALYZE, BUFFERS).
